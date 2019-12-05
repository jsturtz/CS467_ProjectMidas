from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
import sys, traceback
from Midas import data_import, data_analysis, data_cleaning, machine_learning
from Midas.databases import create_new_session, get_session_data, get_all_sessions, save_model, update_model, get_model, delete_session
from Midas.ML_pipeline import ML_Custom, categorical_to_dummy, encode_test_data
from Midas import machine_learning
from .forms import UploadTraining, UploadTesting, CleaningOptions
import pickle
import pandas as pd


def about(request):

    context = {}
    return render(request, 'about.html', context=context)

def home(request):

    if request.method == 'GET':
  
        feature = request.GET.get('feature_detail')
  
        if feature:
            data = data_analysis.make_feature_details(feature, request.session['outcome'], request.session['training_data_path'])
            return render(request, 'feature_details.html', data)
  
        elif request.GET.get('recommended_dtypes'):
            context = data_analysis.get_recommended_dtypes(request.session['outcome'], request.session['training_data_path'])
            return render(request, 'select_data_types.html', context)
  
        elif request.GET.get('columns'):
            context = data_analysis.get_features(request.session['training_data_path'])
            return render(request, 'select_outcome.html', context) 
  
        elif request.GET.get('cleaning_options'):
            model_name = request.GET.get('cleaning_options')
            request.session['ml_algorithm'] = model_name
            opt = ML_Custom(model_name).get_options()
            cleaning_form = CleaningOptions(standardize=opt["standardize"], missing_data = opt["missing_data"], outliers=opt["outliers"])
            return render(request, 'data_cleaning_form.html', {"form": cleaning_form})
  
        elif request.GET.get('run-model'):
            record_id = request.GET.get('run-model')
            session_data = get_session_data(record_id)[0]
            cleaning_options = session_data["cleaning_options"]
            encoding = session_data["encoding"]
            model = get_model(session_data["model_id"])[0]["pickled_model"]
            df = pd.read_csv(request.session["testing_data_path"])
            results = execute_model(df, model, cleaning_options, encoding)
            rows_output = [{"index": i, "label": r} for i, r in enumerate(results)]
            for k, v in cleaning_options.items():
                print("%s: %s" % (k, v))
        
            return render(request, "execution_results.html", {
                "rows": rows_output, 
                "response": cleaning_options["label_mapping"]["outcome"], 
                "identifier": df.columns.tolist()[0], 
            })
  
        elif request.GET.get('delete-model'):
            print("THis is hit!")
            record_id = request.GET.get('delete-model');
            delete_session(record_id)
            return JsonResponse({'error': False, 'message': 'Successfully deleted entry'})

        # no queries were passed
        else:
            upload_training = UploadTraining()
            upload_testing = UploadTesting()
  
            # FIXME: Call a function called get_all_sessions or whatever that queries mongo and returns a list like that below:
            # need to make a call to get the session id
            all_sessions = get_all_sessions()
            return render(request, 'home.html', {'upload_training': upload_training, 'upload_testing': upload_testing, 'sessions': all_sessions})
  
    elif request.method == 'POST':
        # for k, v in request.POST.items():
        #     print("%s: %s" % (k, v))
  
        if request.POST['action'] == 'upload':
            return upload_data(request)
        elif request.POST['action'] == 'outcome':
            return choose_outcome(request)
        elif request.POST['action'] == 'analysis':
            return get_analysis(request)
        # handles both cleaning and training
        elif request.POST['action'] == 'cleaning':
            if CleaningOptions(request.POST).is_valid():
                return run_training(request, clean_data(request))
            else:
                return JsonResponse({'error': True, 'message': 'Invalid form submission for cleaning'})
        elif request.POST['action'] == 'save':
            return save_session(request)
        else:
            return JsonResponse({'error': True, 'message': 'Not a valid post request'})


def execute_model(df, model, cleaning_options, encoding):
    # def _format_result(results):
    #     # ex:
    #     # results = [{"index": 1, "label": 0}, ...]
    #     # left most column usually the index
    #     print(results)
    df = data_cleaning.clean_data(
            df,
            cleaning_options["label_mapping"],
            cleaning_options["numeric_strategy"],
            cleaning_options["categorical_strategy"],
            cleaning_options["outliers"],
            cleaning_options["standardize"],
            cleaning_options["variance_retained"]
    )

    # encode test data
    df = encode_test_data(df, encoding)
    results = machine_learning.run_model(df, cleaning_options["label_mapping"]["outcome"], model)
    return results


# handles post request to upload data
def upload_data(request):

    if request.POST['file_type'] == 'training':
        form = UploadTraining(request.POST, request.FILES)
    else:
        form = UploadTesting(request.POST, request.FILES)

    if form.is_valid() and request.POST['file_type'] == 'training':
        request.session["training_data_path"] = data_import.handle_uploaded_file(request.FILES["filepath"])
        return JsonResponse({'error': False, 'message': 'Successfully Imported File'})
    elif form.is_valid() and request.POST['file_type'] == 'testing':
        request.session["testing_data_path"] = data_import.handle_uploaded_file(request.FILES["filepath"]) 
        return JsonResponse({'error': False, 'message': 'Successfully Imported File'})
    else:
        return JsonResponse({'error': True, 'message': form.errors})

def choose_outcome(request):
    request.session['outcome'] = request.POST['outcome']
    return JsonResponse({'error': False, 'message': 'Successfully saved response variable', 'outcome': request.POST['outcome']})

# FIXME: This function throws an error when user clicks on feature to get details
def get_analysis(request):

    # get collection from session
    training_data_path = request.session['training_data_path']

    # grab only those categoricals
    categoricals = [ k for k, v in request.POST.items() if v == "categorical"]

    # stuff results into label_mapping for use by clean_data route
    request.session["label_mapping"] = data_analysis.get_label_mapping(training_data_path, request.session['outcome'], categoricals=categoricals)
    request.session["label_mapping"]["outcome"] = request.session['outcome']

    # get data dictionary, render
    data = data_analysis.make_data_dictionary(training_data_path, categoricals=categoricals)
    data['outcome'] = request.session['outcome']
    # for r in data['rows']:
    #     print(r)
    return render(request, 'data_dictionary.html', data)

# handles post request to clean data
def clean_data(request):
    request.session["cleaning_options"] = dict(
    training_data_path  = request.session['training_data_path'],
    standardize          = request.POST.get('standardize'),
    outliers             = request.POST.get('outliers')             if request.POST.get('outliers') != "none" else None,
    variance_retained    = request.POST.get('variance_retained')    if request.POST.get("do_PCA") else 0,
    label_mapping        = request.session["label_mapping"]         if request.POST.get("do_imputation") else None,
    numeric_strategy     = request.POST.get('numeric_strategy')     if request.POST.get("do_imputation") else None,
    categorical_strategy = request.POST.get('categorical_strategy') if request.POST.get("do_imputation") else None)

    results = data_cleaning.clean_training_data(
        filepath             = request.session['training_data_path'],
        standardize          = request.POST.get('standardize'),
        outliers             = request.POST.get('outliers')                 if request.POST.get('outliers') != "none" else None,
        variance_retained    = int(request.POST.get('variance_retained'))   if request.POST.get("do_PCA") else 0,
        label_mapping        = request.session["label_mapping"]             if request.POST.get("do_imputation") else None,
        numeric_strategy     = request.POST.get('numeric_strategy')         if request.POST.get("do_imputation") else None,
        categorical_strategy = request.POST.get('categorical_strategy')     if request.POST.get("do_imputation") else None
    )

    return results


def run_training(request, clean_data):

    encoded_data, encoding = categorical_to_dummy(clean_data, request.session['outcome'])
    pickled_model, training_results = machine_learning.train_model(
      encoded_data,
      request.session['outcome'],
      request.session["ml_algorithm"])
    request.session["training_results"] = training_results

    # save the model in models collection
    model_id = save_model(pickled_model)
    request.session["model_id"] = str(model_id)
    request.session["encoding"] = encoding
    
    for k, v in training_results.items():
        print("%s: %s" % (k, v))
    # write reference to session object
    return render(request, "training_results.html", training_results)


def save_session(request):
    #FIXME: Need to add record to Mongo, storing everything in request.session. Ignore cleaned_data for now since it's too big
    session_id = create_new_session(
      {
        "model_id": request.session["model_id"],
        "ml_algorithm": request.session["ml_algorithm"],
        "cleaning_options": request.session["cleaning_options"],
        "pretty_name": request.POST.get("pretty_name"),
        "results": request.session["training_results"],
        "encoding": request.session["encoding"]
      }
    )

    update_model(request.session["model_id"], {"session_id": str(session_id)})

    # show it works
    print(f"model's session id: {get_model(request.session['model_id'])[0]['session_id']}")
    print(f"session results: {get_session_data(session_id)[0]['results']}")

    return JsonResponse({'error': False, 'message': "Successful"})

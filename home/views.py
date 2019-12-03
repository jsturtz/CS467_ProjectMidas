from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
import sys, traceback
from Midas import data_import, data_analysis, data_cleaning, machine_learning
from Midas.databases import create_new_session, get_session_data, delete_model, get_all_sessions, save_model, update_model, get_model
from Midas.ML_pipeline import ML_Custom
from Midas import machine_learning
from .forms import UploadTraining, UploadTesting, CleaningOptions 
import pickle

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
          context = data_analysis.get_columns(request.session['training_data_path'])
          return render(request, 'select_outcome.html', context)

      elif request.GET.get('cleaning_options'):
          model_name = request.GET.get('cleaning_options')
          request.session['ml_algorithm'] = model_name
          opt = ML_Custom(model_name).get_options()
          cleaning_form = CleaningOptions(standardize=opt["standardize"], missing_data = opt["missing_data"], outliers=opt["outliers"])
          return render(request, 'data_cleaning_form.html', {"form": cleaning_form})

      elif request.GET.get('run-model'):
          print("run-model route")
          record_id = request.GET.get('run-model')
          print(f"record_id: {record_id}")
          # s = databases.get_session(record_id)
          session_data = get_session_data(record_id)[0]
          print(f"session_data: {session_data}")
          cleaning_options = session_data["cleaning_options"]
          df = read_csv(request.session["testing_data_path"])
          cleaned_data = clean_data(
                  df, 
                  cleaning_options["label_mapping"], 
                  cleaning_options["numeric_strategy"], 
                  cleaning_options["categorical_strategy"], 
                  cleaning_options["outliers"], 
                  cleaning_options["standardize"], 
                  cleaning_options["variance_retained"]
          )
          print(session_data)
          model = get_model(session_data["model_id"])[0]
          print(model)
          # FIXME: Implement this function to replace hardcoded results
          results = execute_model(cleaned_data, model)
          # results = [{"index": 1, "label": 0}, {"index": 2, "label": 1}, {"index": 3, "label": 0}]
          return render(request, "execution_results.html", {"rows": results})

      elif request.GET.get('delete-model'):
          record_id = request.GET.get('delete-model');
          # FIXME: Call to database to delete model 
          # delete_model(record_id)

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
          return run_training(request, clean_data(request))
      elif request.POST['action'] == 'save':
          return save_session(request)

      #FIXME: Add route to handle saving the model. This will wrap up all the data and save to collection.
      # elif request.POST['action'] == 'save':
      #     return save_model(request)
      # Johnny: by default, models are saved. I don't think there's a need to have an explicit save call.

      else:
          return JsonResponse({'error': True, 'message': 'Not a valid post request'})


def execute_model(df, model):
    # def _format_result(results):
    #     # ex:
    #     # results = [{"index": 1, "label": 0}, ...]
    #     # left most column usually the index
    #     print(results)

    results = machine_learning.run_model(df, model)
    print(f"results: {results}")

    return results


# handles post request to upload data
def upload_data(request):

    if request.POST['file_type'] == 'training':
        form = UploadTraining(request.POST, request.FILES)
    else:
        # FIXME: We need to store the raw testing data separately from the raw training data. This right here is for 
        # when the user uploads data on the run subpage to execute the model against
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
    # for k, v in request.POST.items():
    #     print("%s: %s" % (k, v))
    form = CleaningOptions(request.POST)
    if form.is_valid():
        
        request.session["cleaning_options"] = dict(
        training_data_path  = request.session['training_data_path'],
        standardize          = request.POST.get('standardize'),
        outliers             = request.POST.get('outliers')             if request.POST.get('outliers') != "none" else None,
        variance_retained    = request.POST.get('variance_retained')    if request.POST.get("do_PCA") else 0,
        label_mapping        = request.session["label_mapping"]         if request.POST.get("do_imputation") else None,
        numeric_strategy     = request.POST.get('numeric_strategy')     if request.POST.get("do_imputation") else None,
        categorical_strategy = request.POST.get('categorical_strategy') if request.POST.get("do_imputation") else None,)

        # FIXME: Delete these
        # print("**********ARGUMENTS**************")
        # print("training_data_path: %s" % training_data_path)
        # print("outliers: %s" % outliers)
        # print("standardize: %s" % standardize)
        # print("variance_retained: %s" % variance_retained)
        # print("label_mapping: %s" % label_mapping)
        # print("numeric_strategy: %s" % numeric_strategy)
        # print("categorical_strategy: %s" % categorical_strategy)
        
        results = data_cleaning.clean_training_data(
            filepath             = request.session['training_data_path'], 
            standardize          = request.POST.get('standardize'),
            outliers             = request.POST.get('outliers')                 if request.POST.get('outliers') != "none" else None,
            variance_retained    = int(request.POST.get('variance_retained'))   if request.POST.get("do_PCA") else 0,
            label_mapping        = request.session["label_mapping"]             if request.POST.get("do_imputation") else None,
            numeric_strategy     = request.POST.get('numeric_strategy')         if request.POST.get("do_imputation") else None,
            categorical_strategy = request.POST.get('categorical_strategy')     if request.POST.get("do_imputation") else None
        )

        # request.session["cleaned_data"] = results.to_json()
        return results

def run_training(request, clean_data):

    pickled_model, training_results = machine_learning.train_model(
      clean_data,
      request.session['outcome'],
      request.session["ml_algorithm"])
    request.session["training_results"] = training_results
    # request.session["model"] = pickled_model
    # save the model in models collection
    model_id = save_model(pickled_model)
    request.session["model_id"] = str(model_id)

    # write reference to session object
    return render(request, "training_results.html", training_results)


def save_session(request):
    #FIXME: Need to add record to Mongo, storing everything in request.session. Ignore cleaned_data for now since it's too big
    session_id = create_new_session(
      request.session["model_id"],
      request.session["ml_algorithm"],
      request.POST.get("pretty_name"),
      request.session["cleaning_options"],
      request.session["training_results"])

    update_model(request.session["model_id"], {"session_id": str(session_id)})

    # show it works
    print(f"model's session id: {get_model(request.session['model_id'])[0]['session_id']}")
    print(f"session results: {get_session_data(session_id)[0]['results']}")

    return JsonResponse({'error': False, 'message': "Successful"})

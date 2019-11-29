from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
import sys, traceback
from Midas import data_import, data_analysis, data_cleaning
from Midas.databases import create_new_session, get_session_data
from Midas.ML_pipeline import ML_Custom
from .forms import UploadTraining, UploadTesting, CleaningOptions

def about(request):

    context = {}
    return render(request, 'about.html', context=context)

def home(request):
    
  if request.method == 'GET':
      
      feature = request.GET.get('feature_detail')

      if feature:
          data = data_analysis.make_feature_details(feature, request.session['outcome'], request.session['current_raw_data_id'])
          return render(request, 'feature_details.html', data)

      elif request.GET.get('recommended_dtypes'):
          context = data_analysis.get_recommended_dtypes(request.session['outcome'], request.session['current_raw_data_id'])
          return render(request, 'select_data_types.html', context)

      elif request.GET.get('columns'):
          context = data_analysis.get_columns(request.session['current_raw_data_id'])

          # Jordan-FIXME: we need a way to save the selected outcome variable not sure how to do this.

          return render(request, 'select_outcome.html', context)

      elif request.GET.get('cleaning_options'):
          model_name = request.GET.get('cleaning_options')
          opt = ML_Custom(model_name).get_options()
          cleaning_form = CleaningOptions(standardize=opt["standardize"], missing_data = opt["missing_data"], encoding=opt["encoding"], outliers=opt["outliers"])
          return render(request, 'data_cleaning_form.html', {"form": cleaning_form})

      elif request.GET.get('run-model'):
          # record_id = request.GET.get('run-model');
          # FIXME: Call to database to execute model and return whatever we need to display on the frontend
          # model = database.get_model(record_id)
          # return JsonResponse({'error': False, 'data': model, 'message': 'Model retrieved'})

          # in this situation, we need to provide a results table of what they uploaded
          # presumably, the user will have uploaded data that does not include the label
          # the call to run the model will require that we clean the data in the same way as it was before
          # and a labeled set is returned to the user.
          # this can be in the form of a csv
          session = get_session_data(request.GET.get('run-model'))

          clean_data_args = dict(
            standardize=session['cleaning_options']['standardize'],
            outliers=session['cleaning_options']['outliers'],
            variance_retained=session['cleaning_options']['variance_retained'],
            numeric_strategy=session['cleaning_options']['numeric_strategy'],
            categorical_strategy=session['cleaning_options']['categorical_strategy']
          )

          # how do we get the model_id? is it tied to a session or is this a user-input?
          results = run_model(testing_raw_data_id, model_id, session['label_mapping'], **clean_data_args)

          return JsonResponse({'error': False, 'message': 'Model retrieved'})

      elif request.GET.get('delete-model'):
          record_id = request.GET.get('delete-model');
          # FIXME: Call to database to delete model 

          return JsonResponse({'error': False, 'message': 'Successfully deleted entry'})


      # no queries were passed
      else:
          upload_training = UploadTraining()
          upload_testing = UploadTesting()

          # FIXME: Call a function called get_all_sessions or whatever that queries mongo and returns a list like that below: 
          all_sessions = get_all_sessions()
          # need to make a call to get the session id 
          sessions_fixme = [ 
                  {"id": "id_01", "pretty_name": "KNN with no outliers", "ml_algorithm": "KNN"}, 
                  {"id": "id_02", "pretty_name": "SVN no imputation", "ml_algorithm": "SVN"}, 
                  {"id": "id_03", "pretty_name": "KNN all options", "ml_algorithm": "KNN"}
          ]
          return render(request, 'home.html', {'upload_training': upload_training, 'upload_testing': upload_testing, 'sessions': sessions_fixme})

  elif request.method == 'POST':
      if request.POST['action'] == 'upload':
          return upload_data(request)
      elif request.POST['action'] == 'outcome':
          return choose_outcome(request)
      elif request.POST['action'] == 'analysis':
          return get_analysis(request)
      elif request.POST['action'] == 'cleaning':
          return clean_data(request)
      #FIXME: Add route to handle executing the actual training 
      elif request.POST['action'] == 'training':
          # save the training metadata
          return train_model(request)

      #FIXME: Add route to handle saving the model. This will wrap up all the data and save to collection.
      # elif request.POST['action'] == 'save':
      #     return save_model(request)
      # Johnny: by default, models are saved. I don't think there's a need to have an explicit save call.

      else:
          return JsonResponse({'error': True, 'message': 'Not a valid post request'})


def train_model(request):
    # Jordan-FIXME: 
    # user selects a training method/strategy, not sure how to access

    model_id, results = machine_learning.train_model(
      request.session['current_raw_data_id'],
      request.session['outcome'],
      model_strategy=requests.POST.get('model_strategy') # maybe like this?
      )

    # Jordan-FIXME: not sure where you want to declare the ml_algorithms or pretty_name options
    # session_id = create_new_session(model_id, ml_algorithm, pretty_name, cleaning_options)

    return session_id, model_id, results


# handles post request to upload data
def upload_data(request):

    if request.POST['file_type'] == 'training':
        form = UploadTraining(request.POST, request.FILES)
    else:
        # FIXME: We need to store the raw testing data separately from the raw training data. This right here is for 
        # when the user uploads data on the run subpage to execute the model against
        form = UploadTesting(request.POST, request.FILES)

    if form.is_valid() and request.POST['file_type'] == 'training':
        # collection = data_import.handle_uploaded_file(request.FILES["filepath"], request.session['_id'])
        current_raw_data_id = data_import.handle_uploaded_file(request.FILES["filepath"], request.session['_id'])
        request.session['current_raw_data_id'] = current_raw_data_id
        data = data_analysis.make_data_dictionary(current_raw_data_id)
        return JsonResponse({'error': False, 'message': 'Successfully Imported File'})
    elif form.is_valid() and request.POST['file_type'] == 'testing':
        testing_raw_data_id = data_import.handle_uploaded_file(request.FILES["filepath"], request.session['_id'])
    else:
        return JsonResponse({'error': True, 'message': form.errors})

def choose_outcome(request):
    request.session['outcome'] = request.POST['outcome']
    return JsonResponse({'error': False, 'message': 'Successfully saved response variable', 'outcome': request.POST['outcome']})

# FIXME: This function throws an error when user clicks on feature to get details
def get_analysis(request):
    
    # get collection from session
    current_raw_data_id = request.session['current_raw_data_id']

    # grab only those categoricals 
    categoricals = [ k for k, v in request.POST.items() if v == "categorical"]
    print(categoricals)

    # stuff results into label_mapping for use by clean_data route
    print("Data ID: %s" % current_raw_data_id)
    request.session["label_mapping"] = data_analysis.get_label_mapping(current_raw_data_id, categoricals=categoricals)
    
    # get data dictionary, render
    data = data_analysis.make_data_dictionary(current_raw_data_id, categoricals=categoricals)
    data['outcome'] = request.session['outcome']
    print(data['outcome'])
    return render(request, 'data_dictionary.html', data)

# handles post request to clean data
def clean_data(request):
    for k, v in request.POST.items():
        print("%s: %s" % (k, v))
    form = CleaningOptions(request.POST)
    if form.is_valid():
        
        current_raw_data_id  = request.session['current_raw_data_id']
        standardize          = request.POST.get('standardize')
        outliers             = request.POST.get('outliers')             if request.POST.get('outliers') != "none" else None
        variance_retained    = request.POST.get('variance_retained')    if request.POST.get("do_PCA") else None
        label_mapping        = request.session["label_mapping"]         if request.POST.get("do_imputation") else None
        numeric_strategy     = request.POST.get('numeric_strategy')     if request.POST.get("do_imputation") else None
        categorical_strategy = request.POST.get('categorical_strategy') if request.POST.get("do_imputation") else None

        cleaning_options = dict(
            standardize=standardize,
            outliers=outliers,
            variance_retained=variance_retained,
            label_mapping=label_mapping,
            numeric_strategy=numeric_strategy,
            categorical_strategy=categorical_strategy,
        )

        # FIXME: Delete these
        print("**********ARGUMENTS**************")
        print("current_raw_data_id: %s" % current_raw_data_id)
        print("outliers: %s" % outliers)
        print("standardize: %s" % standardize)
        print("variance_retained: %s" % variance_retained)
        print("label_mapping: %s" % label_mapping)
        print("numeric_strategy: %s" % numeric_strategy)
        print("categorical_strategy: %s" % categorical_strategy)

        result = data_cleaning.clean_data(
            raw_data_id          = request.session['current_raw_data_id'], 
            standardize          = request.POST.get('standardize'),
            outliers             = request.POST.get('outliers')             if request.POST.get('outliers') != "none" else None,
            variance_retained    = request.POST.get('variance_retained')    if request.POST.get("do_PCA") else None,
            label_mapping        = request.session["label_mapping"]         if request.POST.get("do_imputation") else None,
            numeric_strategy     = request.POST.get('numeric_strategy')     if request.POST.get("do_imputation") else None,
            categorical_strategy = request.POST.get('categorical_strategy') if request.POST.get("do_imputation") else None
        )

        if result:
            return JsonResponse({'error': False, 'message': "Data Cleaning Successful"})
        else:
            return JsonResponse({'error': True, 'message': "Data Cleaning Unsuccessful!"})
    else:
        print("SHIT ISNT VALID")


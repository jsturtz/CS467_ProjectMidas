from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
import sys, traceback
from Midas import data_import, data_analysis, data_cleaning
from Midas.databases import create_new_session
from .forms import UploadTraining, UploadTesting, CleaningOptions

def about(request):

    context = {}
    return render(request, 'about.html', context=context)

def home(request):

  # session id not declared
  if not request.session.get('_id'):
      request.session['_id'] = create_new_session()
    
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
          return render(request, 'select_outcome.html', context)

      # no queries were passed
      else:
          upload_training = UploadTraining()
          upload_testing = UploadTesting()
          cleaning_options = CleaningOptions()
          return render(request, 'train.html', {'upload_training': upload_training, 'upload_testing': upload_testing, 'cleaning_options': cleaning_options})

  elif request.method == 'POST':
      if request.POST['action'] == 'upload':
          return upload_data(request)
      elif request.POST['action'] == 'outcome':
          return choose_outcome(request)
      elif request.POST['action'] == 'analysis':
          return get_analysis(request)
      elif request.POST['action'] == 'cleaning':
          return clean_data(request)

# handles post request to upload data
def upload_data(request):

    if request.POST['file_type'] == 'training':
        form = UploadTraining(request.POST, request.FILES)
    else:
        form = UploadTesting(request.POST, request.FILES)
    if form.is_valid():
        # collection = data_import.handle_uploaded_file(request.FILES["filepath"], request.session['_id'])
        current_raw_data_id = data_import.handle_uploaded_file(request.FILES["filepath"], request.session['_id'])
        request.session['current_raw_data_id'] = current_raw_data_id
        data = data_analysis.make_data_dictionary(current_raw_data_id)
        return JsonResponse({'error': False, 'message': 'Successfully Imported File'})
    else:
        return JsonResponse({'error': True, 'message': form.errors})

def choose_outcome(request):
    request.session['outcome'] = request.POST['outcome']
    return JsonResponse({'error': False, 'message': 'Successfully saved response variable', 'outcome': request.POST['outcome']})

def get_analysis(request):
    
    # db = Mongo.dosomeshit().todict()
    # outcome = db[x][outcome]
    # sessions = {
    #     _id : 1,
    #     pretty_name: "Logistic Regression",
    #     outcome: "isfraud",
    #     label_mapping = ["TransactionID"...]
    #     raw_data = {}
    # }


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
    form = CleaningOptions(request.POST, request.FILES)
    if form.is_valid():
        
        current_raw_data_id  = request.session['current_raw_data_id']
        standardize          = request.POST.get('standardize')
        outliers             = request.POST.get('outliers')             if request.POST.get('outliers') != "none" else None
        variance_retained    = request.POST.get('variance_retained')    if request.POST.get("do_PCA") else None
        label_mapping        = request.session["label_mapping"]         if request.POST.get("do_imputation") else None
        numeric_strategy     = request.POST.get('numeric_strategy')     if request.POST.get("do_imputation") else None
        categorical_strategy = request.POST.get('categorical_strategy') if request.POST.get("do_imputation") else None
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


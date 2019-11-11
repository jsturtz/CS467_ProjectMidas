from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
import sys, traceback
from Midas import data_import, data_analysis #, data_cleaning
from .forms import UploadTraining, UploadTesting, CleaningOptions

def home(request):

    context = {}
    return render(request, 'home.html', context=context)

def about(request):

    context = {}
    return render(request, 'about.html', context=context)

def train(request):
    
  if request.method == 'GET':
      feature            = request.GET.get('feature_detail')
      recommended_dtypes = request.GET.get('recommended_dtypes')

      if feature:
          data = data_analysis.make_feature_details(feature, request.session['collection'])
          return render(request, 'feature_details.html', data)

      elif recommended_dtypes:
          context = data_analysis.get_recommended_dtypes(request.session['collection'])
          return render(request, 'select_data_types.html', context)

      # no queries were passed
      else:
          upload_training = UploadTraining()
          upload_testing = UploadTesting()
          cleaning_options = CleaningOptions()
          return render(request, 'train.html', {'upload_training': upload_training, 'upload_testing': upload_testing, 'cleaning_options': cleaning_options})

  elif request.method == 'POST':
      if request.POST['action'] == 'upload':
          return upload_data(request)
      if request.POST['action'] == 'cleaning':
          return clean_data(request)

# handles post request to upload data
def upload_data(request):

    if request.POST['file_type'] == 'training':
        form = UploadTraining(request.POST, request.FILES)
    else:
        form = UploadTesting(request.POST, request.FILES)
    if form.is_valid():
        collection = data_import.handle_uploaded_file(request.FILES["filepath"])
        request.session['collection'] = collection
        data = data_analysis.make_data_dictionary(collection)
        return render(request, 'data_dictionary.html', data)
    else:
        return JsonResponse({'error': True, 'message': form.errors})


# def clean_data(
#         collection,
#         label_mapping,
#         numeric_strategy='mean',
#         categorical_strategy='fill_with_missing',
#         outliers=None,
#         standarize=None,
#         variance_retained=0,
#         db='raw_data'):

# label_mapping = {
#     'numeric': ['TransactionAMT',...],
#     'categorical': ['card1', 'card2'...]
# }

# handles post request to clean data
def clean_data(request):
    form = CleaningOptions(request.POST, request.FILES)
    if form.is_valid():
        
        # get label mapping from POST
        numeric     = [ k for k, v in request.POST.items() if v == "numeric"]
        categorical = [ k for k, v in request.POST.items() if v == "categorical"]
        label_mapping = {"numeric": numeric, "categorical": categorical}
        
        # the rest of the values are just sitting in the POST request by name
        # result = data_cleaning.clean_data(
        #     collection           = request.session.collection, 
        #     label_mapping        = label_mapping,
        #     numeric_strategy     = request.POST.numeric_strategy,
        #     categorical_strategy = request.POST.categorical_strategy,
        #     outliers             = request.POST.outliers,
        #     variance_retained    = request.POST.variance_retained, 
        #     standardize          = request.POST.standardize
        # )
        # if result:
        if False:
            return JsonResponse({'error': False, 'message': "Data Cleaning Successful"})
        else:
            return JsonResponse({'erro': True, 'message': "Data Cleaning Unsuccessful!"})

def run(request):

    context = {}
    return render(request, 'run.html', context=context)



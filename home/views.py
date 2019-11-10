from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
import sys, traceback
from Midas import data_analysis, data_import
from .forms import UploadTraining, UploadTesting

def home(request):

    context = {}
    return render(request, 'home.html', context=context)

def about(request):

    context = {}
    return render(request, 'about.html', context=context)

def train(request):
    
  if request.method == 'GET':
      feature = request.GET.get('feature_detail')
      if feature:
          data = data_analysis.make_feature_details(feature, request.session['collection'])
          print("data: %s" % data)
          print("plot: %s" % data['plot'])
          return render(request, 'feature_details.html', data)

      # no queries were passed
      else:
          training_form = UploadTraining()
          testing_form = UploadTesting()
          return render(request, 'train.html', {'training_form': training_form, 'testing_form': testing_form})

  elif request.method == 'POST':
      if request.POST['action'] == 'upload':
          return upload_data(request)

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

def run(request):

    context = {}
    return render(request, 'run.html', context=context)



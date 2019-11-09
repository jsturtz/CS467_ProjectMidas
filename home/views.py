from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
import sys, traceback
from Midas import data_analysis, tools
from .forms import UploadIdentity, UploadTransaction

# every view must return an HttpResponse object
def home(request):

    context = {}
    return render(request, 'home.html', context=context)

def about(request):

    context = {}
    return render(request, 'about.html', context=context)

def train(request):

  if request.method == 'POST':

      # user requests to upload csv
      if request.POST['do'] == 'upload_transaction':
        form = UploadTransaction(request.POST, request.FILES)
        if form.is_valid():
            identifier = tools.handle_uploaded_file(request.FILES["filepath"])
            html = data_analysis.make_data_dictionary(identifier)
            return JsonResponse({'error': False, 'message': 'Uploaded successfully', 'data': html})
        else:
            return JsonResponse({'error': True, 'message': form.errors})

      elif request.POST['do'] == 'upload_identity':
        form = UploadIdentity(request.POST, request.FILES)
        if form.is_valid():
            identifier = tools.handle_uploaded_file(request.FILES["filepath"])
            html = data_analysis.make_data_dictionary(identifier)
            return JsonResponse({'error': False, 'message': 'Uploaded successfully', 'data': html})
        else:
            return JsonResponse({'error': True, 'message': form.errors})

  # request method was get, so render page
  else:
      transaction_form = UploadTransaction()
      identity_form = UploadIdentity()
      return render(request, 'train.html', {'transaction_form': transaction_form, 'identity_form': identity_form})

def run(request):

    context = {}
    return render(request, 'run.html', context=context)



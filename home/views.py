from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .tools import handle_uploaded_file
from .forms import UploadIdentity, UploadTransaction
import json
import sys, traceback

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
            collection_name = handle_uploaded_file(request.FILES["filepath"])
            return JsonResponse({'error': False, 'message': f'Uploaded successfully. Collection: {collection_name}'})
        else:
            return JsonResponse({'error': True, 'message': form.errors})

      elif request.POST['do'] == 'upload_identity':
        form = UploadIdentity(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["filepath"])
            return JsonResponse({'error': False, 'message': 'Uploaded successfully'})
        else:
            return JsonResponse({'error': True, 'message': form.errors})

      # user requests to generate dictionary
      elif request.POST['do'] == 'generate_dict':
        # Here is where we need to invoke the python libraries we've written. Talk to Johnny about this
        return JsonResponse({'error': False, 'message': 'Generated successfully!'})

  # request method was get, so render page
  else:
      transaction_form = UploadTransaction()
      identity_form = UploadIdentity()
      return render(request, 'train.html', {'transaction_form': transaction_form, 'identity_form': identity_form})

def run(request):

    context = {}
    return render(request, 'run.html', context=context)



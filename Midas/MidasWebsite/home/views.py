from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .tools import handle_uploaded_file
from .forms import UploadCSV

# every view must return an HttpResponse object
def home(request):
    
    context = {}
    return render(request, 'home.html', context=context)
  
def about(request):
    
    context = {}
    return render(request, 'about.html', context=context)

def train(request):

  # for when user uploads CSV    
  if request.method == 'POST':
      form = UploadCSV(request.POST, request.FILES)
      if form.is_valid():
          return JsonResponse({'error': False, 'message': 'Uploaded successfully'})
      else:
          return JsonResponse({'error': True, 'message': form.errors})

  # for when user navigates to page for first time
  else:
      form = UploadCSV()

  return render(request, 'train.html', {'uploadCSV': form})
  
def run(request):
    
    context = {}
    return render(request, 'run.html', context=context)



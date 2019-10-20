from django.shortcuts import render
from django.http import HttpResponse

# every view must return an HttpResponse object
def home(request):
    
    context = {}
    return render(request, 'home.html', context=context)
  
def about(request):
    
    context = {}
    return render(request, 'about.html', context=context)

def train(request):
    
    # the right way to inject template
    context = {}
    return render(request, 'train.html', context=context)
  
def run(request):
    
    context = {}
    return render(request, 'run.html', context=context)

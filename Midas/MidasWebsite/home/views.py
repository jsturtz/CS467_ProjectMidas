from django.shortcuts import render
from django.http import HttpResponse

# every view must return an HttpResponse object
def home(request):
    
    # The most basic HttpResponse object
    # return HttpResponse("Hello, world. You're at the Midas index")

    # the right way to inject template
    context = { }

    return render(request, 'home.html', context=context)


def about(request):
    
    # the right way to inject template
    context = { }

    return render(request, 'about.html', context=context)

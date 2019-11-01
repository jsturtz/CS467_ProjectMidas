from django.apps import AppConfig

# The power of this feature is that it allows you to create an application configuration 
# class which has a ready method, allowing you to perform initialization tasks such as 
# registering signals when the application first loads.

# Link
# https://chriskief.com/2014/02/28/django-1-7-signals-appconfig/

class MidasConfig(AppConfig):
    name = 'Midas'

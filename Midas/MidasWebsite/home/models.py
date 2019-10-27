from django.db import models

# Create your models here.

# A model is the single, definitive source of information about your data. It contains the essential fields 
# and behaviors of the data you’re storing. Generally, each model maps to a single database table.

# class RawData(models.Model):
#   name = models.CharField(max_length=30)
#   path = models.FileField(upload_to=".", max_length=30)
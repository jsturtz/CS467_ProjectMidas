from django.db import models

# Create your models here.

# A model is the single, definitive source of information about your data. It contains the essential fields 
# and behaviors of the data you’re storing. Generally, each model maps to a single database table.
# The basics:
# Each model is a Python class that subclasses django.db.models.Model.
# Each attribute of the model represents a database field.
# With all of this, Django gives you an automatically-generated database-access API; see Making queries.

# EXAMPLE
class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

# This class creates the following table
# CREATE TABLE myapp_person (
#     "id" serial NOT NULL PRIMARY KEY,
#     "first_name" varchar(30) NOT NULL,
#     "last_name" varchar(30) NOT NULL
# );


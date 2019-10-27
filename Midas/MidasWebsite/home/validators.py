import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  
    extensions = [".csv"]
    if not ext.lower() in extensions:
        raise ValidationError(u'Unsupported file extension.')
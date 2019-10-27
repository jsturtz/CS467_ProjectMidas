from django import forms
from .validators import validate_file_extension

# for csv files
class UploadCSV(forms.Form):
  filepath = forms.FileField(validators=[validate_file_extension])
from django import forms
from Midas.validators import validate_file_extension

# for csv files
class UploadTraining(forms.Form):
  filepath = forms.FileField(label="Training File", validators=[validate_file_extension])

class UploadTesting(forms.Form):
  filepath = forms.FileField(label="Testing File", validators=[validate_file_extension])

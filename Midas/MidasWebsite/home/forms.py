from django import forms
from .validators import validate_file_extension

# for csv files
class UploadTransaction(forms.Form):
  filepath = forms.FileField(label="Transaction File", validators=[validate_file_extension])

class UploadIdentity(forms.Form):
  filepath = forms.FileField(label="Identity File", validators=[validate_file_extension])
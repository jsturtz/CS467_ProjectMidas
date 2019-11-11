from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from Midas.validators import validate_file_extension

# for csv files
class UploadTraining(forms.Form):
    filepath = forms.FileField(label="Training File", validators=[validate_file_extension])

class UploadTesting(forms.Form):
    filepath = forms.FileField(label="Testing File", validators=[validate_file_extension])

class CleaningOptions(forms.Form):
    n_strategy = [
        ('mean', 'Mean'),
        ('median', 'Median')
    ]

    c_strategy = [
        ('fill_with_missing', "Fill With Missing")
    ]

    numerical_strategy=forms.ChoiceField(label="Numeric Imputation Method", choices=n_strategy)
    categorical_strategy=forms.ChoiceField(label="Categorical Imputation Method", choices=c_strategy)
    outliers=forms.BooleanField(label="Remove Outliers?", required=False)
    standardize=forms.BooleanField(label="Standardize columns?", required=False)
    variance_retained=forms.IntegerField(
        label="Percentage Variance Retained",
        initial=100,
        validators = [MaxValueValidator(100), MinValueValidator(1)])

# def clean_data(
#         collection,
#         label_mapping,
#         numeric_strategy='mean',
#         categorical_strategy='fill_with_missing',
#         outliers=None,
#         standarize=None,
#         variance_retained=0,
#         db='raw_data'):


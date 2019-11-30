from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from Midas.validators import validate_file_extension

# for csv files
class UploadTraining(forms.Form):
    filepath = forms.FileField(label="Training File", validators=[validate_file_extension])

class UploadTesting(forms.Form):
    filepath = forms.FileField(label="Testing File", validators=[validate_file_extension])

class CleaningOptions(forms.Form):
    
    # whether to standardize data
    standardize=forms.BooleanField(label="Standardize columns", required=False)

    # do_imputation will toggle the imputation fields, which start out hidden
    do_imputation=forms.BooleanField(label="Impute for Missing Data", required=False)
    numeric_strategy=forms.ChoiceField(label="Numeric Imputation Method", choices=[('mean', 'Mean'), ('median', 'Median')], required=False)
    categorical_strategy=forms.ChoiceField(label="Categorical Imputation Method", choices=[('fill_with_missing', 'Fill With Missing')], required=False)

    # do_PCA will toggle the PCA field, which starts out hidden
    do_PCA=forms.BooleanField(label="Perform Principle Components Analysis", required=False)
    variance_retained=forms.IntegerField(
        label="Percentage Variance Retained",
        initial=100, required=False,
        validators = [MaxValueValidator(100), MinValueValidator(1)])
   
    # # whether to encode
    # encoding=forms.BooleanField(label="Dummy Encode Variables", required=False)
    
    # how to handle outliers
    outliers=forms.ChoiceField(
        widget=forms.RadioSelect(),
        initial="none", 
        label="Handle Outliers", 
        required=True, 
        choices=[
        ("value", "Remove Rows with Outliers"), 
        ("obs", "Impute Missing for Outliers")
        ]
    )
    
    # at initialization, can decide whether to hide fields
    def __init__(self, *args, **kwargs):
        # remove and store all kwargs if exist so can invoke super constructor
        standardize = kwargs.pop('standardize') if 'standardize' in kwargs else True
        missing_data = kwargs.pop('missing_data') if 'missing_data' in kwargs else True
        outliers = kwargs.pop('outliers') if 'outliers' in kwargs else True
        super(CleaningOptions, self).__init__(*args, **kwargs)
        self.initial['outliers'] = "value";
        
        # use optional args to decide whether to make form elements required

        if not standardize:
            self.fields['standardize'].required = True

        if not missing_data:
            self.fields['do_imputation'].required = True
            self.fields['numeric_strategy'].required = True
            self.fields['categorical_strategy'].required = True
            self.fields['do_PCA'].required = True
            self.fields['variance_retained'].required = True

        if not outliers:
            self.fields['outliers'].required = True

        # if not standardize:
        #     self.fields['standardize'].widget = forms.HiddenInput()

        # if not missing_data:
        #     self.fields['do_imputation'].widget = forms.HiddenInput()
        #     self.fields['numeric_strategy'].widget = forms.HiddenInput()
        #     self.fields['categorical_strategy'].widget = forms.HiddenInput()
        #     self.fields['do_PCA'].widget = forms.HiddenInput()
        #     self.fields['variance_retained'].widget = forms.HiddenInput()

        # if not encoding:
        #     self.fields['encoding'].widget = forms.HiddenInput()

        # if not outliers:
        #     self.fields['outliers'].widget = forms.HiddenInput()

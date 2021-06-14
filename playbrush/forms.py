from django import forms
from .models import Files


class FilesForm(forms.ModelForm):

    class Meta:
        model = Files
        fields = ['csv1', 'csv2']
        labels = {
            "csv1": "Raw data csv",
            "csv2": "Group data csv"
        }

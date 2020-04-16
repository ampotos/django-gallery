from django import forms
from .models import Picture
from taggit_selectize import widgets as tag_widget

class UploadZipForm(forms.Form):
    file = forms.FileField()
    

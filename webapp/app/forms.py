from django import forms
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

class PaperForm(forms.Form):
	file = forms.FileField(label='')

class NotesForm(forms.Form):
    notes = forms.CharField()
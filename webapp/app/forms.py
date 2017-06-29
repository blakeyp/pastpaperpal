from django import forms

class PaperForm(forms.Form):   # paper upload form
	file = forms.FileField(label='')
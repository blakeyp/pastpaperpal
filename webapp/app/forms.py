from django import forms

class PaperForm(forms.Form):
	file = forms.FileField(label='')
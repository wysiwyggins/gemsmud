from django import forms

class AppForm(forms.Form):
    name = forms.CharField(label='Character Name', max_length=80)
    background = forms.CharField(label='Background')

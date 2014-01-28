from django import forms
from django.contrib.auth.decorators import login_required


class ManageKey(forms.Form):
    deletekey = forms.IntegerField(required=False)
    addkey = forms.CharField(max_length=32, required=False)
    keydesc = forms.CharField(required=False)
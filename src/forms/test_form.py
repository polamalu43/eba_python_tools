from django import forms
from ..models import Test

class Test(forms.Form):
    class Meta:
        model = Test

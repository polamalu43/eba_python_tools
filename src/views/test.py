from django.shortcuts import render
from django.http import HttpResponse
from ..forms import Test
from django.views import View

class Test(View):
    def get(self, request):
        return render(request, 'pages/test.html')

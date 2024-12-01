from django.shortcuts import render
from django.http import HttpResponse
from ..forms import Test
from django.views import View
import logging
from ..services.negative_word_check_service import NegativeWordCheckService

class NegativeWordCheckView(View):
    def __init__(self):
        self.nWordCheckService = NegativeWordCheckService()

    def get(self, request):
        count = self.nWordCheckService.getCount()
        context = {
            'count': count
        }
        return render(request, 'pages/negative_word_check.html', context)

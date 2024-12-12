from django.shortcuts import render
from django.http import HttpResponse
from ..forms import Test
from django.views import View
import logging
from ..services.negative_word_check_service import NegativeWordCheckService

class NegativeWordCheckView(View):
    def __init__(self):
        self.nword_check_service = NegativeWordCheckService()

    def get(self, request):
        options = {
            'page': '1',
            'searchString': 'あ',
            'memberName': '',
            'maxPageCount': '50',
            'ymFrom': '2024-1',
            'weekFrom': '1',
            'ymTo': '2024-12',
            'weekTo': '1',
            'search': '',
        }
        count = self.nword_check_service.get_nwords()
        context = {
            'count': count
        }
        return render(request, 'pages/negative_word_check.html', context)

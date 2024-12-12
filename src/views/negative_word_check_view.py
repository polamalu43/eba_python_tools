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
            'search_string': 'あ',
            'member_name': '',
            'max_page_count': '50',
            'ym_from': '2024-1',
            'week_from': '1',
            'ym_to': '2024-12',
            'week_to': '1',
            'search': '',
        }
        count = self.nword_check_service.count_target_nword(options)
        context = {
            'count': count
        }
        return render(request, 'pages/negative_word_check.html', context)

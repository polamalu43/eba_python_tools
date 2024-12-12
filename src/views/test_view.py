from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options
import base64
from time import sleep

class TestView(View):
    def get(self, request):
        return render(request, 'pages/test.html')

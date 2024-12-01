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
        options = Options()
        options.add_argument("--headless")
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options)
        self.login()
        self.getData()
        return render(request, 'pages/test.html')

    def getData(self):
        self.driver.get("https://eba-report.xyz/subordinate_leader_detail?leader_member_no=285")
        table = self.driver.find_element(By.XPATH, value='//table[@class="list_table scroll_table"]')
        print(table.get_attribute('outerHTML'))

    def login(self):
        self.loginBasicAuthentication()
        self.loginIndexAuthentication()

    def loginBasicAuthentication(self):
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.execute_cdp_cmd(
            "Network.setExtraHTTPHeaders",
            {
                "headers": self.getAuthorizationHeader(
                    's.minami',
                    'r8hXYE0r'
                )
            }
        )

    def getAuthorizationHeader(self, user, password):
        b64 = "Basic " + base64.b64encode('{}:{}'.format(user, password).encode('utf-8')).decode('utf-8')
        return {"Authorization": b64}

    def loginIndexAuthentication(self):
        self.driver.get('https://eba-report.xyz/index')
        self.element(selector='//input[@name="login_id"]', _type=By.XPATH, style='input', text='s.minami')
        self.element(selector='//input[@name="login_pass"]', _type=By.XPATH, style='input', text='CxjsvIHe')
        self.element(selector='//button[@name="accept"]', _type=By.XPATH, style='click')

    def element(self, selector='', _type='xpath', multi=False, target_num=0, style='get', text='', non_sleep=False):
        if multi:
            element = self.driver.find_elements(by=_type, value=selector)[target_num]
        else:
            element = self.driver.find_element(by=_type, value=selector)
        if style == 'get':
            return element
        if style == 'click':
            element.click()
            if not non_sleep:
                sleep(4)
        if style == 'input':
            element.send_keys(text)


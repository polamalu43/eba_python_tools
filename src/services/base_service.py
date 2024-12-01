import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import base64
from time import sleep
import gspread
from google.oauth2.service_account import Credentials
from ..constants import *

class BaseService():
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
        self.driver.get(EBA_REPORT_INDEX_URL)
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

    def getParseHtml(self, html):
        return BeautifulSoup(html, 'html.parser')

    def authenticate_gspread(credentials_filepath: str):
        scope = [
            GSPREAD_AUTH_SHEETS_URL,
            GSPREAD_AUTH_DRIVE_URL,
        ]
        credentials = Credentials.from_service_account_file(credentials_filepath, scopes=scope)
        return gspread.authorize(credentials)

    def handle_gspread(self, gspread_url):
        gc = self.authenticate_gspread
        gspread = gc.open_by_url(gspread_url)

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
from ..utils.env_utils import env
from ..utils.common_utils import debug
import json
from selenium.webdriver.remote.webelement import WebElement
from typing import Type

class BaseService():
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(self.options)

    def login(self) -> None:
        self.login_basic_authentication()
        self.login_index_authentication()

    def login_basic_authentication(self) -> None:
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.execute_cdp_cmd(
            "Network.setExtraHTTPHeaders",
            {
                "headers": self.get_authorization_header(
                    env('AUTHENTICATION_USER_NAME'),
                    env('BASIC_AUTHENTICATION_PASSWORD')
                )
            }
        )

    def get_authorization_header(self, user: str, password: str) -> dict[str]:
        b64 = "Basic " + base64.b64encode('{}:{}'.format(user, password).encode('utf-8')).decode('utf-8')
        return {"Authorization": b64}

    def login_index_authentication(self) -> None:
        self.driver.get(EBA_REPORT_INDEX_URL)
        self.element(selector='//input[@name="login_id"]', _type=By.XPATH, style='input', text=env('AUTHENTICATION_USER_NAME'))
        self.element(selector='//input[@name="login_pass"]', _type=By.XPATH, style='input', text=env('INDEX_AUTHENTICATION_PASSWORD'))
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

    def get_parse_html(self, html: WebElement) -> BeautifulSoup:
        return BeautifulSoup(html, 'html.parser')

    def authenticate_gspread(self):
        scope = [
            GSPREAD_AUTH_SHEETS_URL,
            GSPREAD_AUTH_DRIVE_URL,
        ]
        credentials_json = env('GSPREAD_CREDENTIAL_JSON')
        service_account_info = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)
        return gspread.authorize(credentials)

    def get_gspread_col_data(self, gspread_url: str, worksheet_name: int, col: int) -> Type[object]:
        worksheet = self.get_gspread_worksheet(gspread_url, worksheet_name)
        data = worksheet.col_values(col)
        return data

    def get_gspread_worksheet(self, gspread_url: str, worksheet_name: int) -> Type[object]:
        gc = self.authenticate_gspread()
        gspread = gc.open_by_url(gspread_url)
        worksheet = gspread.get_worksheet(worksheet_name)
        return worksheet

    def update_gspread_col_data(self, gspread_url, worksheet_name: str):
        worksheet = self.get_gspread_worksheet(gspread_url, worksheet_name)

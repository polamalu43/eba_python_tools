from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import base64
from time import sleep
from ..constants import *
from ..utils.common_utils import env
from selenium.webdriver.remote.webelement import WebElement

class BaseService():
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument('--no-sandbox')
        # self.options.add_argument('--disable-dev-shm-usage') 不要かも

        # self.options.add_argument('--disable-gpu')  # GPUを無効化
        # self.options.add_argument('--disable-software-rasterizer')  # ソフトウェアレンダリング無効化
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
        self.driver.get(env('EBA_REPORT_INDEX_URL'))
        self.element(selector='//input[@name="login_id"]', _type=By.XPATH, style='input', text=env('AUTHENTICATION_USER_NAME'))
        self.element(selector='//input[@name="login_pass"]', _type=By.XPATH, style='input', text=env('INDEX_AUTHENTICATION_PASSWORD'))
        self.element(selector='//button[@name="accept"]', _type=By.XPATH, style='click')

    def element(
        self,
        selector: str = '',
        _type: str = 'xpath',
        multi: bool = False,
        target_num: int =0,
        style: str ='get',
        text: str = '',
        non_sleep: bool = False
    ):
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

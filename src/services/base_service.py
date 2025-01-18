from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import base64
from ..constants import *
from ..utils.common_utils import env, errorlog

class BaseService():
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless") # ヘッドレスモード
        self.options.add_argument('--disable-gpu')  # GPUを無効化
        prefs = {"download.default_directory": DOWNLOAD_DIR}
        self.options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(self.options)

    def login(self) -> None:
        try:
            self.login_basic_authentication()
            self.login_index_authentication()
        except Exception as e:
            errorlog(f"ログイン処理時にエラーが発生しました。: {e}")
            raise

    def login_basic_authentication(self) -> None:
        try:
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
        except WebDriverException as e:
            errorlog(f"WebDriverのCDPコマンド実行エラーが発生しました。: {e}")
            raise
        except Exception as e:
            errorlog(f"basic認証中にエラーが発生しました。: {e}")
            raise

    def get_authorization_header(self, user: str, password: str) -> dict[str]:
        b64 = "Basic " + base64.b64encode('{}:{}'.format(user, password).encode('utf-8')).decode('utf-8')
        return {"Authorization": b64}

    def login_index_authentication(self) -> None:
        try:
            self.driver.get(env('EBA_REPORT_INDEX_URL'))
            login_id_elem = self.find_element(
                'XPATH',
                '//input[@name="login_id"]'
            )
            login_id_elem.send_keys(env('AUTHENTICATION_USER_NAME'))

            login_pass_elem = self.find_element(
                'XPATH',
                '//input[@name="login_pass"]'
            )
            login_pass_elem.send_keys(env('INDEX_AUTHENTICATION_PASSWORD'))

            accept_button_elem = self.find_element(
                'XPATH',
                '//button[@name="accept"]'
            )
            accept_button_elem.click()
        except Exception as e:
            errorlog(f"週報システムログイン時にエラーが発生しました: {e}")
            raise

    def get_parse_html(self, html: WebElement) -> BeautifulSoup:
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            errorlog(f"BeautifulSoupのHTMLパース中にエラーが発生しました: {e}")
            raise

    def wait_loading_complete(self) -> None:
        try:
            WebDriverWait(self.driver, env('LOADING_WAIT_TIME')).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
        except TimeoutException as e:
            errorlog(f"ページの読み込み時間が{env('LOADING_WAIT_TIME')}秒を超えたためタイムアウトしました。: {e}")
            raise

    def find_elements(self, type, value):
        by_type = getattr(By, type)
        return self.driver.find_elements(by_type, value)

    def find_element(self, type, value):
        by_type = getattr(By, type)
        return self.driver.find_element(by_type, value)

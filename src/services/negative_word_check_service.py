import logging
from .base_service import BaseService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

class NegativeWordCheckService(BaseService):
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')

    def getData(self):
        self.driver = webdriver.Chrome(self.options)
        self.login()
        self.driver.get("https://eba-report.xyz/weekly_report_search?page=1&search_string=【人間関係】&member_name=&max_page_count=50&ym_from=2024-10&week_from=1&ym_to=2024-11&week_to=1&search=")
        table = self.driver.find_element(By.XPATH, value='//table[@name="contact"]')
        return table.get_attribute('outerHTML')

    def getCount(self):
        self.driver = webdriver.Chrome(self.options)
        self.login()
        self.driver.get("https://eba-report.xyz/weekly_report_search?page=1&search_string=【人間関係】&member_name=&max_page_count=50&ym_from=2024-10&week_from=1&ym_to=2024-11&week_to=1&search=")
        table = self.driver.find_element(By.XPATH, value='//table[@name="contact"]')
        parseHtml = self.getParseHtml(table.get_attribute('outerHTML'))
        elements = parseHtml.find_all('td', class_='weekly_report_search-td')
        return len(elements)

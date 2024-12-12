from .base_service import BaseService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from ..utils.env_utils import env
from ..utils.common_utils import debug

class NegativeWordCheckService(BaseService):
    def count_target_nword(self, options):
        self.login()
        url = self.__get_nword_url(options)
        self.driver.get(url)
        pages = self.driver.find_element(By.XPATH, value='//div[@class="pagination_navi"]')
        count_page = self.__count_page(pages)
        count_nword = 0
        if count_page >= 2:
            for i in range(1, count_page-1):
                if i == 1:
                    table = self.driver.find_element(By.XPATH, value='//table[@name="contact"]')
                    count_nword += self.__count_table_row(table)
                    continue
                options['page'] = str(i)
                url = self.__get_nword_url(options)
                self.driver.get(url)
                table = self.driver.find_element(By.XPATH, value='//table[@name="contact"]')
                count_nword += self.__count_table_row(table)
        else:
            table = self.driver.find_element(By.XPATH, value='//table[@name="contact"]')
            count_nword = self.__count_table_row(table)
        return count_nword

    def get_nwords(self):
        return self.get_gspread_col_data(env('TARGET_GSPREAD_URL'), 0, 1)

    def update_nwords(self):
        self.update_gspread_col_data(env('TARGET_GSPREAD_URL'), 1, 1)

    def __get_nword_url(self, options):
        baseUrl='https://eba-report.xyz/weekly_report_search'
        pageParam = 'page=' + options['page']
        searchStringParam = 'search_string=' + options['searchString']
        memberNameParam = 'member_name=' + options['memberName']
        maxPageCountParam = 'max_page_count=' + options['maxPageCount']
        ymFromParam = 'ym_from=' + options['ymFrom']
        weekFromParam = 'week_from=' + options['weekFrom']
        ymToParam = 'ym_to=' + options['ymTo']
        weekToParam = 'week_to=' + options['weekTo']
        searchParam = 'search=' + options['search']
        url = baseUrl + '?' \
            + pageParam + '&' \
            + searchStringParam + '&' \
            + memberNameParam + '&' \
            + maxPageCountParam + '&' \
            + ymFromParam + '&' \
            + weekFromParam + '&' \
            + ymToParam + '&' \
            + weekToParam + '&' \
            + searchParam
        return url

    def __count_page(self, pages):
        parse_html_for_pages = self.get_parse_html(pages.get_attribute('outerHTML'))
        pages_elements = parse_html_for_pages.find_all('span', class_='pager_text')
        return len(pages_elements)

    def __count_table_row(self, table):
        parse_html_for_table = self.get_parse_html(table.get_attribute('outerHTML'))
        teble_elements = parse_html_for_table.find_all('td', class_='weekly_report_search-td')
        return len(teble_elements)

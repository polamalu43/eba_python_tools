from .base_service import BaseService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from ..utils.env_utils import env
from ..utils.common_utils import debug
from selenium.webdriver.remote.webelement import WebElement

class NegativeWordCheckService(BaseService):
    def exec(self, options: dict[str], latest_flg: bool):
        self.login()
        nword_list = self.__get_nword_list()
        count = 0
        for nword in nword_list:
            options['search_string'] = nword
            options['page'] = '1'
            count += self.__count_target_range_nword(options)
        debug(count)

    def __count_target_range_nword(self, options: dict[str]) -> int:
        """
        指定した範囲のネガティブワードの件数を合計で出力する。
        """
        url = self.__get_nword_url(options)
        self.driver.get(url)
        pages = self.driver.find_element(By.XPATH, value='//div[@class="pagination_navi"]')
        count_page = self.__count_page(pages)
        count_nword = 0
        if count_page >= 2:
            for i in range(1, count_page + 1):
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

    def __get_nword_list(self):
        return self.get_gspread_col_data(env('TARGET_GSPREAD_URL'), 0, 1)

    def __update_nword_list(self):
        self.update_gspread_col_data(env('TARGET_GSPREAD_URL'), 1, 1)

    def __get_nword_url(self, options: dict[str]) -> str:
        """
        週報システムの週報検索ページにアクセスし必要なデータを取得するためのURLを生成
        """
        base_url=env('WEEKLY_REPORT_SEARCH')
        page_param = 'page=' + options['page']
        search_string_param = 'search_string=' + options['search_string']
        member_name_param = 'member_name=' + options['member_name']
        max_page_count_param = 'max_page_count=' + options['max_page_count']
        ym_from_param = 'ym_from=' + options['ym_from']
        week_from_param = 'week_from=' + options['week_from']
        ym_to_param = 'ym_to=' + options['ym_to']
        week_to_param = 'week_to=' + options['week_to']
        search_param = 'search=' + options['search']
        url = base_url + '?' \
            + page_param + '&' \
            + search_string_param + '&' \
            + member_name_param + '&' \
            + max_page_count_param + '&' \
            + ym_from_param + '&' \
            + week_from_param + '&' \
            + ym_to_param + '&' \
            + week_to_param + '&' \
            + search_param
        return url

    def __count_page(self, pages: WebElement) -> int:
        """
        週報検索ページ検索結果のページ数を数える
        """
        parse_html_for_pages = self.get_parse_html(pages.get_attribute('outerHTML'))
        page_elements = parse_html_for_pages.find_all('span', class_='pager_text')
        filtered_page_elements = [
            element for element in page_elements
            if not any(keyword in element.text for keyword in ['前へ', '後へ', '最初へ', '最後へ'])
        ]
        return len(filtered_page_elements)

    def __count_table_row(self, table: WebElement) -> int:
        """
        週報検索ページ検索結果のテーブル行数を数える
        """
        parse_html_for_table = self.get_parse_html(table.get_attribute('outerHTML'))
        teble_elements = parse_html_for_table.find_all('td', class_='weekly_report_search-td')
        return len(teble_elements)

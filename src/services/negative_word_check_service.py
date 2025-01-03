from .base_service import BaseService
from selenium.webdriver.common.by import By
from ..utils.common_utils import env, debug, errorlog, get_week_of_month, get_previous_monday
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
from .gspread_service import GspreadService
from ..constants import *

class NegativeWordCheckService(BaseService):
    def __init__(self):
        super().__init__()
        self.gspread_service = GspreadService()

    def command_exec(self, options: dict[str], type: str) -> None:
        """
        コマンド実行時の処理
        """
        self.login()
        if type in LATEST_TYPE_WORDS:
            self.__exec_latest_type(options)
        elif type in GROUPING_TYPE_WORDS:
            self.__exec_grouping_type(options)
        elif type in SUM_TYPE_WORDS:
            self.__exec_sum_type(options)
        else:
            errorlog('該当するタイプの処理がありませんでした。')

    def __exec_latest_type(self, options: dict[str]) -> None:
        """
        typeがlatestの時に実行する処理
        """
        today = datetime.today().date()
        previous_monday = get_previous_monday(today)
        week_of_month = get_week_of_month(previous_monday)
        formatted_date = today.strftime('%Y年%m月')
        options['ym_from'] = formatted_date
        options['week_from'] = str(week_of_month)
        options['ym_to'] = formatted_date
        options['week_to'] = str(week_of_month)
        nword_list = self.__get_nword_list()
        count = 0

        for nword in nword_list:
            options['search_string'] = nword
            options['page'] = '1'
            count += self.__count_nword_sum(options)

        records = {
            'date':formatted_date + ' 第' + str(week_of_month) + '週',
            'count': count,
        }
        self.__insert_nword_number(records)

    def __exec_grouping_type(self, options: dict[str]) -> None:
        """
        typeがgroupingの時に実行する処理
        """
        nword_list = self.__get_nword_list()
        count_list = {}
        for nword in nword_list:
            options['search_string'] = nword
            options['page'] = WEEKLY_REPORT_FIRST_PAGE
            self.__count_nword_grouping(options, count_list)
        self.__insert_nword_number_list(count_list)

    def __exec_sum_type(self, options: dict[str]) -> None:
        """
        typeがsumの時に実行する処理
        """
        nword_list = self.__get_nword_list()
        count = 0
        for nword in nword_list:
            options['search_string'] = nword
            options['page'] = '1'
            count += self.__count_nword_sum(options)
        f_year, f_month = options['ym_from'].split('-')
        t_year, t_month = options['ym_to'].split('-')
        ym_from = f_year + '年' + f_month + '月'
        ym_to = t_year + '年' + t_month + '月'
        records = {
            'date': ym_from + ' 第' + options['week_from'] + '週 ~ ' + \
                ym_to + ' 第' + options['week_to'] + '週',
            'count': count,
        }
        self.__insert_nword_number(records)

    def __count_nword_grouping(self, options: dict[str], count_list: dict[str | int]) -> None:
        """
        指定した範囲のネガティブワードの件数を合計で出力する。
        """
        url = self.__get_nword_url(options)
        self.driver.get(url)
        pages = self.driver.find_elements(By.XPATH, value='//div[@class="pagination_navi"]')
        count_page = self.__count_page(pages)
        if count_page >= 2:
            for i in range(1, count_page + 1):
                if i == 1:
                    table = self.driver.find_elements(By.XPATH, value='//table[@name="contact"]')
                    self.__count_table_row_grouping(table, count_list)
                    continue
                options['page'] = str(i)
                url = self.__get_nword_url(options)
                self.driver.get(url)
                table = self.driver.find_elements(By.XPATH, value='//table[@name="contact"]')
                self.__count_table_row_grouping(table, count_list)
        else:
            table = self.driver.find_elements(By.XPATH, value='//table[@name="contact"]')
            self.__count_table_row_grouping(table, count_list)

    def __count_nword_sum(self, options: dict[str]) -> int:
        """
        指定した範囲のネガティブワードの件数を合計で出力する。
        """
        url = self.__get_nword_url(options)
        self.driver.get(url)
        pages = self.driver.find_elements(By.XPATH, value='//div[@class="pagination_navi"]')
        count_page = self.__count_page(pages)
        count_nword = 0
        if count_page >= 2:
            for i in range(1, count_page + 1):
                if i == 1:
                    table = self.driver.find_elements(By.XPATH, value='//table[@name="contact"]')
                    count_nword += self.__count_table_row(table)
                    continue
                options['page'] = str(i)
                url = self.__get_nword_url(options)
                self.driver.get(url)
                table = self.driver.find_elements(By.XPATH, value='//table[@name="contact"]')
                count_nword += self.__count_table_row(table)
        else:
            table = self.driver.find_elements(By.XPATH, value='//table[@name="contact"]')
            count_nword = self.__count_table_row(table)
        return count_nword

    def __get_nword_list(self):
        """
        スプレッドシートの指定した範囲からネガティブワード一覧を取得
        """
        return self.gspread_service.get_col_data(
            env('TARGET_GSPREAD_URL'),
            env('NWORD_LIST_SHEET'),
            1
        )

    def __insert_nword_number(self, records: dict[str | int], target_col: int = 1) -> None:
        """
        スプレッドシートの指定した範囲に検索したネガティブワードの件数と日付を入力
        """
        last_row = self.gspread_service.get_last_row(
            env('TARGET_GSPREAD_URL'),
            env('NWORD_NUMBER_INSERT_SHEET')
        )
        target_row = last_row + 1
        self.gspread_service.update_cell(
            env('TARGET_GSPREAD_URL'),
            env('NWORD_NUMBER_INSERT_SHEET'),
            target_row,
            target_col,
            records['date'],
        )
        self.gspread_service.update_cell(
            env('TARGET_GSPREAD_URL'),
            env('NWORD_NUMBER_INSERT_SHEET'),
            target_row,
            target_col + 1,
            records['count'],
        )

    def __insert_nword_number_list(self, data: dict[str,  int], target_col: int = 1) -> None:
        """
        辞書からスプレッドシートの指定した範囲に検索したネガティブワードの件数と日付を入力
        """
        last_row = self.gspread_service.get_last_row(
            env('TARGET_GSPREAD_URL'),
            env('NWORD_NUMBER_INSERT_SHEET')
        )
        target_row = last_row + 1
        data = sorted([[key, value] for key, value in data.items()])
        self.gspread_service.update(
            env('TARGET_GSPREAD_URL'),
            env('NWORD_NUMBER_INSERT_SHEET'),
            data,
            target_row,
            target_col
        )

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

    def __count_page(self, pages: dict[WebElement]) -> int:
        """
        週報検索ページ検索結果のページ数を数える
        """
        if not pages:
            return 0
        parse_html_for_pages = self.get_parse_html(pages[0].get_attribute('outerHTML'))
        page_elements = parse_html_for_pages.find_all('span', class_='pager_text')
        filtered_page_elements = [
            element for element in page_elements
            if not any(
                keyword in element.text for keyword in EXCEPTION_WEEKLY_REPORT_KEYWORDS
            )
        ]
        return len(filtered_page_elements)

    def __count_table_row(self, table: dict[WebElement]) -> int:
        """
        週報検索ページ検索結果のテーブル行数を数える
        """
        if not table:
            return 0
        parse_html_for_table = self.get_parse_html(table[0].get_attribute('outerHTML'))
        teble_elements = parse_html_for_table.find_all('td', class_='weekly_report_search-td')
        return len(teble_elements)

    def __count_table_row_grouping(self, table: dict[WebElement], count_list: dict[str, int]) -> bool:
        """
        グルーピングオプションの設定時に週報検索ページ検索結果のテーブル行数を数える
        """
        if not table or not table[0]:
            return False
        parse_html_for_table = self.get_parse_html(table[0].get_attribute('outerHTML'))
        tr_elements = parse_html_for_table.select('tr > td:nth-of-type(2)')
        for week in tr_elements:
            if week.text in count_list:
                count_list[week.text] += 1
            else:
                count_list[week.text] = 1
        return True

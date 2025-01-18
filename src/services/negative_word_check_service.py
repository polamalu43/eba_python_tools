from .base_service import BaseService
from selenium.webdriver.remote.webelement import WebElement
from ..utils.common_utils import env, errorlog, get_week_of_month, get_previous_monday
from datetime import datetime
from .gspread_service import GspreadService
from ..constants import *
from django.core.management.base import CommandError
from typing import Type
import re
import glob
import time

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
            print('処理が完了しました。')
        elif type in GROUPING_TYPE_WORDS:
            self.__exec_grouping_type(options)
            print('処理が完了しました。')
        elif type in SUM_TYPE_WORDS:
            self.__exec_sum_type(options)
            print('処理が完了しました。')
        elif type in CSV_TYPE_WORDS:
            self.__exec_csv_type(options)
            print(
                '処理が完了しました。以下のディレクトリにCSVファイルを格納しています。\n'
                + DOWNLOAD_DIR
            )
        else:
            raise CommandError('該当するタイプの処理がありませんでした。')

    def __exec_latest_type(self, options: dict[str]) -> None:
        """
        typeがlatestの時に実行する処理
        """
        today = datetime.today().date()
        previous_monday = get_previous_monday(today)
        week_of_month = get_week_of_month(previous_monday)
        formatted_date = previous_monday.strftime('%Y-%m')
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
        converted_date = self.__convert_ym_format(formatted_date)
        records = {
            'date': converted_date + ' 第' + str(week_of_month) + '週',
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
        ym_from = self.__convert_ym_format(options['ym_from'])
        ym_to = self.__convert_ym_format(options['ym_to'])
        records = {
            'date': ym_from + ' 第' + options['week_from'] + '週 ~ ' + \
                ym_to + ' 第' + options['week_to'] + '週',
            'count': count,
        }
        self.__insert_nword_number(records)

    def __exec_csv_type(self, options: dict[str]) -> None:
        """
        typeがcsvの時に実行する処理
        """
        nword_list = self.__get_nword_list()
        for nword in nword_list:
            options['search_string'] = nword
            options['page'] = '1'
            is_download = self.__download_csv(options)
            if not is_download:
                continue
            self.__rename_csv_filename(options['search_string'])

    def __download_csv(self, options: dict[str]) -> bool:
        """
        検索ページの検索結果をCSVでダウンロードする。(検索ワード毎にファイルをダウンロード)
        """
        try:
            url = self.__get_nword_url(options)
            self.driver.get(url)
            self.wait_loading_complete()

            elements = None
            self.__count_search_result()

            if self.__count_search_result() >= 1:
                elements = self.find_elements(
                    'XPATH',
                    '//input[@name="download" and @value="CSVダウンロード"]'
                )
            else:
                return False

            if elements:
                elements[0].click()
                self.__wait_csv_file_download()
                return True
            else:
                raise Exception("CSVダウンロードボタンが見つかりませんでした")
        except Exception as e:
            errorlog(f"CSVダウンロード処理中にエラーが発生しました: {e}")
            raise

    def __rename_csv_filename(self, search_string) -> None:
        """
        ダウンロードしたCSVファイルのファイル名を変更
        """
        file_pattern = os.path.join(DOWNLOAD_DIR, '*_weekly_report_search.csv')
        files = glob.glob(file_pattern)

        if files:
            for file in files:
                timestamp = os.path.basename(file).split('_')[0]
                new_file_name = f"{timestamp}_weekly_report_search_{search_string}.csv"
                new_file_path = os.path.join(DOWNLOAD_DIR, new_file_name)
                try:
                    os.rename(file, new_file_path)
                except Exception as e:
                    errorlog(f"ファイル名の変更中にエラーが発生しました: {e}")
                    raise
        else:
            raise Exception("該当するファイルが見つかりませんでした")

    def __wait_csv_file_download(self) -> None:
        timeout_second = int(env('DOWNLOAD_WAIT_TIME'))
        for i in range(timeout_second + 1):
            match_file_path = os.path.join(DOWNLOAD_DIR, '*_weekly_report_search.csv')
            files = glob.glob(match_file_path)

            if files:
                extensions = [
                    file_name for file_name in files if '.crdownload' in os.path.splitext(file_name)
                ]
                if not extensions:
                    break

            if i >= timeout_second:
                raise Exception('待機タイムアウト時間(秒)内にダウンロードが完了しませんでした')

            time.sleep(1)
        return None

    def __count_search_result(self) -> int:
        """
        週報検索ページ検索結果の件数を出力する。
        """
        try:
            elements = self.find_element('XPATH', '//p[@class="now_page_info"]')
            text = elements.text
            match = re.search(r'全(\d+)件', text)

            if match:
                return int(match.group(1))
            else:
                raise Exception("件数が取得できませんでした")
        except Exception as e:
            errorlog(f"検索結果の件数を取得中にエラーが発生しました: {e}")
            raise

    def __count_nword_grouping(self, options: dict[str], count_list: dict[str | int]) -> None:
        """
        指定した範囲のネガティブワードの件数をグルーピングで出力する。
        """
        try:
            url = self.__get_nword_url(options)
            self.driver.get(url)
            self.wait_loading_complete()
        except Exception as e:
            errorlog(f"検索ページの読み込み中にエラーが発生しました: {e}")
            raise

        pages = self.find_elements('XPATH', value='//div[@class="pagination_navi"]')
        count_page = self.__count_page(pages)
        if count_page >= 2:
            for i in range(1, count_page + 1):
                if i == 1:
                    table = self.find_elements('XPATH', value='//table[@name="contact"]')
                    self.__count_table_row_grouping(table, count_list)
                    continue
                options['page'] = str(i)
                url = self.__get_nword_url(options)
                self.driver.get(url)
                table = self.find_elements('XPATH', value='//table[@name="contact"]')
                self.__count_table_row_grouping(table, count_list)
        else:
            table = self.find_elements('XPATH', value='//table[@name="contact"]')
            self.__count_table_row_grouping(table, count_list)

    def __count_nword_sum(self, options: dict[str]) -> int:
        """
        指定した範囲のネガティブワードの件数を合計で出力する。
        """
        try:
            url = self.__get_nword_url(options)
            self.driver.get(url)
            self.wait_loading_complete()
        except Exception as e:
            errorlog(f"検索ページの読み込み中にエラーが発生しました: {e}")
            raise

        pages = self.find_elements('XPATH', value='//div[@class="pagination_navi"]')
        count_page = self.__count_page(pages)
        count_nword = 0
        if count_page >= 2:
            for i in range(1, count_page + 1):
                if i == 1:
                    table = self.find_elements('XPATH', value='//table[@name="contact"]')
                    count_nword += self.__count_table_row(table)
                    continue
                options['page'] = str(i)
                url = self.__get_nword_url(options)
                self.driver.get(url)
                table = self.find_elements('XPATH', value='//table[@name="contact"]')
                count_nword += self.__count_table_row(table)
        else:
            table = self.find_elements('XPATH', value='//table[@name="contact"]')
            count_nword = self.__count_table_row(table)
        return count_nword

    def __get_nword_list(self) -> Type[object]:
        """
        スプレッドシートの指定した範囲からネガティブワード一覧を取得
        """
        try:
            return self.gspread_service.get_col_data(
                env('TARGET_GSPREAD_URL'),
                env('NWORD_LIST_SHEET'),
                1
            )
        except Exception as e:
            errorlog(f"スプレッドシートからネガティブワード一覧を取得中にエラーが発生しました: {e}")
            raise

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
        before_sort_data = [
            [key, value, self.__convert_dateweek_to_number(key)] for key, value in data.items()
        ]
        sorted_data = [
            [entry[0], entry[1]] for entry in sorted(before_sort_data, key=lambda x: x[2])
        ]
        self.gspread_service.update(
            env('TARGET_GSPREAD_URL'),
            env('NWORD_NUMBER_INSERT_SHEET'),
            sorted_data,
            target_row,
            target_col
        )

    def __get_nword_url(self, options: dict[str]) -> str:
        """
        週報システムの週報検索ページにアクセスし必要なデータを取得するためのURLを生成
        """
        try:
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
        except KeyError as e:
            errorlog(f"週報検索ページのURL生成に必要なパラメータが欠けています: {e}")
            raise

    def __count_page(self, pages: dict[WebElement]) -> int:
        """
        週報検索ページ検索結果のページ数を数える
        """
        try:
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
        except Exception as e:
            errorlog(f"検索結果のページ数を数える際にエラーが発生しました: {e}")
            raise

    def __count_table_row(self, table: dict[WebElement]) -> int:
        """
        週報検索ページ検索結果のテーブル行数を数える
        """
        if not table:
            return 0
        parse_html_for_table = self.get_parse_html(table[0].get_attribute('outerHTML'))
        teble_elements = parse_html_for_table.find_all('td', class_='weekly_report_search-td')
        return len(teble_elements)

    def __count_table_row_grouping(self, table: dict[WebElement], count_list: dict[str, int]) -> None:
        """
        グルーピングオプションの設定時に週報検索ページ検索結果のテーブル行数を数える
        """
        if not table or not table[0]:
            return None
        parse_html_for_table = self.get_parse_html(table[0].get_attribute('outerHTML'))
        tr_elements = parse_html_for_table.select('tr > td:nth-of-type(2)')
        for week in tr_elements:
            if week.text in count_list:
                count_list[week.text] += 1
            else:
                count_list[week.text] = 1

    def __convert_ym_format(self, ym):
        year, month = ym.split('-')
        return year + '年' + month + '月'

    def __convert_dateweek_to_number(self, dateweek: str) -> int:
        """
        「Y年m月 w週」形式の文字列を数値に変換する(並び替えをするため)
        """
        match = re.match(r'(\d{4})年(\d{1,2})月 第(\d+)週', dateweek)
        if match:
            year = match.group(1)  # 年
            month = match.group(2).zfill(2)  # 月（1桁の場合はゼロ埋め）
            week = match.group(3)  # 週
            return int(year + month + week)  # 結合して整数に変換
        else:
            raise ValueError("日付の形式が正しくありません。")

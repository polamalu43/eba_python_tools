import gspread
from google.oauth2.service_account import Credentials
from ..constants import *
from ..utils.env_utils import env
import json
from typing import Type

class GspreadService():
    def authenticate_gspread(self):
        scope = [
            GSPREAD_AUTH_SHEETS_URL,
            GSPREAD_AUTH_DRIVE_URL,
        ]
        credentials_json = env('GSPREAD_CREDENTIAL_JSON')
        service_account_info = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)
        return gspread.authorize(credentials)

    def get_col_data(self, gspread_url: str, worksheet_name: str, col: int) -> Type[object]:
        worksheet = self.get_worksheet(gspread_url, worksheet_name)
        data = worksheet.col_values(col)
        return data

    def get_last_row(self, gspread_url: str, worksheet_name: str, target_col: int = 1) -> int:
        worksheet = self.get_worksheet(gspread_url, worksheet_name)
        last_row = len(worksheet.col_values(target_col))
        return last_row

    def update_cell(self,
        gspread_url: str,
        worksheet_name: str,
        row: int,
        col: int,
        value: str | int,
    ) -> None:
        worksheet = self.get_worksheet(gspread_url, worksheet_name)
        worksheet.update_cell(row, col, value)

    def get_worksheet(self, gspread_url: str, worksheet_name: str) -> Type[object]:
        gc = self.authenticate_gspread()
        workbook = gc.open_by_url(gspread_url)
        worksheet = workbook.worksheet(worksheet_name)
        return worksheet
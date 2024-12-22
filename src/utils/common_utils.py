import logging
from datetime import datetime, timedelta
import os
import environ
from pathlib import Path

def env(key):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    env = environ.Env()
    env.read_env(os.path.join(BASE_DIR, '.env'))
    return env(key)

def debug(value: any) -> None:
    return logging.debug(print(value))

def errorlog(value: any) -> None:
    return logging.error(value, exc_info=True)

def get_week_of_month(date: datetime.date, start_day_of_week: int=0) -> int:
    """
    月の週番号を取得する。
    処理の流れは以下の通り。
        月初日を取得
        ↓
        月初日の曜日を取得(0: 月曜日, 6: 日曜日）
        ↓
        スタート曜日を調整(start_day_of_weekを基準にして月初からの経過日数を調整)
        ↓
        目標の日付と月初日の日付を比較し、週の番号を計算
        ↓
        月初のスタート曜日までの日数を計算
        ↓
        週番号を計算
    """
    first_day_of_month = date.replace(day=1)
    first_day_weekday = first_day_of_month.weekday()
    adjusted_first_day_weekday = (first_day_weekday - start_day_of_week) % 7
    day_of_month = date.day
    days_since_month_start = day_of_month + adjusted_first_day_weekday
    week_number = (days_since_month_start - 1) // 7 + 1
    return week_number

def get_previous_monday(date: datetime) -> datetime | None:
    if date is None:
        return None
    weekday = date.weekday()
    return date - timedelta(days=weekday + 7)

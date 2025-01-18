import os

LATEST_TYPE_WORDS={'latest', 'l'}
GROUPING_TYPE_WORDS={'grouping', 'g'}
SUM_TYPE_WORDS={'sum', 's'}
CSV_TYPE_WORDS={'csv', 'c'}
WEEKLY_REPORT_PAGE='1'
WEEKLY_REPORT_MAX_PAGE='50'
EXCEPTION_WEEKLY_REPORT_KEYWORDS= ['前へ', '後へ', '最初へ', '最後へ']
WEEKLY_REPORT_FIRST_PAGE='1'
DOWNLOAD_DIR=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'csvs')

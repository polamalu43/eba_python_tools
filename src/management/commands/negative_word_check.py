from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from ...services.negative_word_check_service import NegativeWordCheckService
from ...utils.common_utils import debug, errorlog
from ...constants import *

class Command(BaseCommand):
    help = "指定した期間のネガティブワード件数を抽出"

    def add_arguments(self, parser):
        parser.add_argument(
            "-from",
            action="store",
            default='',
            type=str
        )
        parser.add_argument(
            "-to",
            action="store",
            default='',
            type=str
        )
        parser.add_argument(
            "-type",
            action="store",
            default='',
            type=str
        )

    def handle(self, *args, **options):
        """
        コマンド処理の制御。
        typeがlatestの時のみfromとtoのオプションが空なのを許容する。
        それ以外のケースで空の場合はエラーを発生させる。
        """
        type = options['type'] if not options['type'] == '' else 'l'

        try:
            if not type in LATEST_TYPE_WORDS and not self.__is_from_and_to(options['from'], options['to']):
                raise ValueError
        except ValueError:
            errorlog("FROMとTOが設定されていません。(タイプがlatest以外はFROMとTOの設定が必要)")
            return

        if self.__is_from_and_to(options['from'], options['to']):
            from_split = options['from'].split(",")
            ym_from = from_split[0]
            week_from = from_split[1]

            to_split = options['to'].split(",")
            ym_to = to_split[0]
            week_to = to_split[1]
        else:
            ym_from = ''
            week_from = ''
            ym_to = ''
            week_to = ''

        search_options = {
            'page': '1',
            'search_string': '',
            'member_name': '',
            'max_page_count': '50',
            'ym_from': ym_from,
            'week_from': week_from,
            'ym_to': ym_to,
            'week_to': week_to,
            'search': '',
        }
        nword_check_service = NegativeWordCheckService()
        nword_check_service.command_exec(search_options, type)

    def __is_from_and_to(self, from_arg: str, to_arg: str) -> bool:
        if not from_arg == '' and not to_arg == '':
            return True
        return False

from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from ...services.negative_word_check_service import NegativeWordCheckService
from ...utils.common_utils import debug

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
            "-latest",
            action="store",
            default='no',
            type=str
        )

    def handle(self, *args, **options):
        from_split = options['from'].split(",")
        to_split = options['to'].split(",")
        yes_word_list = {'true', 'yes', 'y', '1'}
        latest_flg = options['latest'].strip().lower() in yes_word_list

        ym_from = from_split[0]
        week_from = from_split[1]
        ym_to = to_split[0]
        week_to = to_split[1]

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
        service = NegativeWordCheckService()
        service.exec(search_options, latest_flg)

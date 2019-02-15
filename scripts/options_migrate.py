# all options that are added to the parent parser
# the parent parser gets incloded in some other also
# and provides common options

from config import BASE_PATH, BASE_INFO
from scripts.parser_handler import ParserHandler

def add_options_migrate(parser, result_dic = {}):
    """add options to the create parser

    Arguments:
        parser {argparse instance} -- instance to which arguments should be added
    """
    parent_parser = ParserHandler(parser, result_dic)

    parent_parser.add_argument(
        "-nmp", "--migrate-prepare",
        action="store", dest="migrate_prepare", default=False,
        help='prepare migraten, site name must be given'
    )


# all options that are added to the parent parser
# the parent parser gets incloded in some other also
# and provides common options

from config import BASE_PATH, BASE_INFO
from scripts.parser_handler import ParserHandler


def add_options_migrate(parser, result_dic={}):
    """add options to the create parser

    Arguments:
        parser {argparse instance} -- instance to which arguments should be added
    """
    parent_parser = ParserHandler(parser, result_dic)

    parent_parser.add_argument(
        "-mdump",
        "--migrate-dump-site",
        action="store_true",
        dest="migrate_dump_site",
        default=False,
        help="Dump odoo site into zip file. Default = False",
        need_name=True,
    )
    parent_parser.add_argument(
        "-mdbp",
        "--migrate-data-path",
        action="store",
        dest="migrate_data_path",
        default=False,
        help="provide path to odoo's datapath. Default = ~/.local/share/Odoo",
        need_name=True,
    )
    parent_parser.add_argument(
        "-mver",
        "--migrate-version",
        action="store",
        dest="migrate_version",
        default="",
        help="string with version info like  to write into the manifest",
        need_name=True,
    )
    parent_parser.add_argument(
        "-mconf",
        "--migrate-config",
        action="store",
        dest="migrate_config_path",
        default=False,
        help="provide path to odoo's migration file",
        need_name=True,
    )
    parent_parser.add_argument(
        "-mp",
        "--migrate-prepare",
        action="store",
        dest="migrate_prepare",
        default=False,
        help="prepare migration, site name must be given",
    )
    parent_parser.add_argument(
        "-mr",
        "--migrate-remove-apps",
        action="store",
        dest="migrate_remove_apps",
        default=False,
        help="provide a filename with modules to be removed, a name of the site must be given",
        need_name=True,
    )

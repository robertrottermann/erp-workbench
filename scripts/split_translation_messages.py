import os
import odoorpc
import getpass
import psycopg2
import psycopg2.extras
import urllib.request, urllib.error, urllib.parse
import base64
import os
import sys
from argparse import ArgumentParser
import argparse

class bcolors:
    """
    """

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    white = "\033[1;37m"
    normal = "\033[0;00m"
    red = "\033[1;31m"
    blue = "\033[1;34m"
    green = "\033[1;32m"
    lightblue = "\033[0;34m"


class OHandler(object):
    db_name = 'fsch_test'
    db_host = 'localhost'
    rpcport = 8069
    #db_user = 'admin'
    #db_user_pw = 'yYFCVEcL+dXJPdoLmrkFpEGEOsZ141IL'
    db_user = 'robert'
    db_user_pw = 'admin'
    postgres_port = 5432
    _odoo = None
    
    def __init__(self, opts, be_loud=False):
        self.opts = opts
        self.rpc_host = opts.host
        self.rpc_port = opts.port
        self.rpc_user = opts.user
        self.rpc_user_pw = opts.password

        c_info = self.get_cursor()
        if c_info:
            self.cursor, self.conn = c_info
        
    def execute(self, sql):
        try:
            self.cursor.execute(sql)
        except Exception as e:
            print(str(e))
            self.conn.rollback()

    def get_cursor(self, db_name=None, return_connection=None):
        """
        """
        dbuser = self.db_user
        dbhost = self.db_host
        dbpw = self.db_user_pw
        postgres_port = self.postgres_port
        db_name = self.db_name
        if dbpw:
            conn_string = "dbname='%s' user='%s' host='%s' password='%s'" % (
                db_name,
                dbuser,
                dbhost,
                dbpw,
            )
        else:
            conn_string = "dbname='%s' user=%s host='%s'" % (db_name, dbuser, dbhost)
        try:
            conn = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            try:
                    if postgres_port:
                            conn_string += " port=%s" % postgres_port
                            conn = psycopg2.connect(conn_string)
            except psycopg2.OperationalError:
                    print('ERP_NOT_RUNNING: %s' % db_name)
                    return
        except:
                return

        cursor_d = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return cursor_d, conn

    def get_odoo(self, no_db=False, verbose=True, login=[], force=False, simple=False):
        if not self._odoo:
            """
            get_module_obj logs into odoo and then
            returns an object with which we can manage the list of modules
            bail out if we can not log into a running odoo site
        
            """
            db_name = self.db_name
            rpchost = self.rpc_host
            rpcport = self.rpc_port
            rpcuser = self.rpc_user
            rpcpw = self.rpc_user_pw
            try:
                import odoorpc
            except ImportError:
                    print(bcolors.WARNING + "please install odoorpc")
                    print("execute pip install -r install/requirements.txt" + bcolors.ENDC)
                    return

            odoo = None
            try:
                if verbose:
                        print("*" * 80)
                        print("about to open connection to:")
                        print("host:%s, port:%s, timeout: %s" % (rpchost, rpcport, 1200))
                if not db_name:
                        print(bcolors.FAIL)
                        print("*" * 80)
                        print("hoppalla no database defined")
                        print(bcolors.ENDC)
                        return
                odoo = odoorpc.ODOO(rpchost, port=rpcport, timeout=1200)
                if not no_db:
                    if verbose:
                        print("about to login:")
                        print(
                            "dbname:%s, rpcuser:%s, rpcpw: %s"
                            % (db_name, rpcuser, rpcpw)
                        )
                print("*" * 80)
            except Exception as e:
                if verbose:
                    print("login failed, will retry with pw admin:")
                    print(
                        "dbname:%s, rpcuser:%s, rpcpw: admin"
                        % (db_name, rpcuser)
                    )
                    print("*" * 80)
                    odoo.login_sudo(db_name, rpcuser, "admin")
            except odoorpc.error.RPCError:
                    print(
                        "could not login to running odoo server host: %s:%s, db: %s, user: %s, pw: %s"
                        % (rpchost, rpcport, db_name, rpcuser, rpcpw)
                    )
                    return
            except urllib.error.URLError:
                    print(
                        "could not login to odoo server host: %s:%s, db: %s, user: %s, pw: %s"
                        % (rpchost, rpcport, db_name, rpcuser, rpcpw)
                    )
                    print("connection was refused")
                    print("make sure odoo is running at the given address" + bcolors.ENDC)
                    return
            self._odoo = odoo
            if not self._odoo:
                    print(
                        bcolors.FAIL
                        + "For what ever reason I could not login to odoo server host: %s:%s, db: %s, user: %s, pw: %s"
                        % (rpchost, rpcport, db_name, rpcuser, rpcpw)
                    )
                    print("make sure odoo is running at the given address" + bcolors.ENDC)
        if not self._odoo:
                print( 'ERP_NOT_RUNNING !!!!!!!!!!!!!!')

        return self._odoo

    def get_module_obj(self):
        odoo = self.get_odoo()
        if not odoo:
            return
        module_obj = odoo.env["ir.module.module"]
        return module_obj

    def update_module(self, m_list=[]): 
        module_obj = self.get_module_obj()
        if not m_list:
            m_list = (self.opts.modules and self.opts.modules.split(',')) or []
        modules = module_obj.browse(m_list)
        print(modules)


def set_uninstalled_modules(cr):
    cr.execute("""
        update ir_module_module set state = 'uninstalled'
        where name in ('fsch_post_migration', 'fsch_pre_migration',
        'l10n_ch_zip_and_bank', 'l10n_ch_zip', 'account_financial_report_qweb',
        'hr_attendance_terminal', 'bt_account', 'bt_indicator', 'bt_oplist',
        'bt_web_widget_datepicker_options', 'web_widget_color',
        'bt_invoice_followup', 'configuration_mail_parameters',
        'account_banking_sepa_credit_transfer', 'bt_todo',
        'l10n_ch_payment_slip', 'funid_integrity',
        'funid_account_financial_report_qweb', 'l10n_ch_base_bank',
        'l10n_ch_scan_bvr', 'fsch_execution', 'bt_helper',
        'fsch_translation_core', 'l10n_ch_pain_base',
        'l10n_ch_pain_credit_transfer', 'sett_hr', 'bt_report_webkit',
        'currency_rate_update', 'bt_payment_difference',
        'base_suspend_security', 'l10n_ch_dta', 'bt_swissdec_pre',
        'fsch_ticketing', 'bt_swissdec', 'web_sheet_full_width',
        'base_transaction_id', 'web_export_view', 'fsch_management_material',
        'web_display_html', 'web_wysiwyg', 'hr_holidays_calendar',
        'l10n_ch_bank', 'hr_holidays_gantt_calendar')""")
    # Temporal disable of modules
    cr.execute("""
        update ir_module_module set state = 'uninstalled'
        where name in ('contact_management_extension',
        'survey_result_date_filter')""")


def main(opts):
    ohandler = OHandler(opts=opts)
    if not opts.modules:
        print(bcolors.WARNING,' please use -m module-name', bcolors.ENDC)
        sys.exit()
    ohandler.update_module()
        


if __name__ == '__main__':
    usage = "split_translation_messages.py -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument(
        "-m",
        "--modules",
        action="store",
        dest="modules",
        help="What odoo modules to upgrade. Comma separated list",
    )
    parser.add_argument(
        "-l",
        "--language",
        action="store",
        dest="language",
        help="What language to test",
    )
    parser.add_argument(
        "-d",
        "--dbname",
        action="store",
        dest="dbname",
        help="What odoo dbname to use",
        default="fsch_test"
    )
    parser.add_argument(
        "-H",
        "--host",
        action="store",
        dest="host",
        help="What host to use",
        default="localhost"
    )
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        dest="port",
        help="What odoo port to use",
        default="8069"
    )
    parser.add_argument(
        "-u",
        "--user",
        action="store",
        dest="user",
        help="What odoo user to use",
        default="admin"
    )
    parser.add_argument(
        "-pw",
        "--password",
        action="store",
        dest="password",
        help="What odoo pw to use",
        default="admin"
    )

    opts = parser.parse_args()
    main(opts)

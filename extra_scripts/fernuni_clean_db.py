# this is a method, we pass the calling instance
# as first parameter. like this we have access on all its attributes
import os
import sys
import shutil
from odoorpc import ODOO
from argparse import ArgumentParser
import psycopg2
import psycopg2.extras

sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])
sys.path.insert(0, '%s/extra_scripts' % os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])

from scripts.bcolors import bcolors

wkhtmltopdf = shutil.which('wkhtmltopdf-amd64')
if not wkhtmltopdf:
    wkhtmltopdf = shutil.which('wkhtmltopdf')


BASE_CLEAN_COMMANDS_PH1 = [
    'UPDATE ir_cron SET active=False',
    'UPDATE res_users SET password=login',
    "update ir_mail_server set smtp_host = smtp_host || '1'",
    "update fetchmail_server set server = server || '1'",
    "UPDATE ir_config_parameter SET value='https://odootst.fernuni.ch' where key='web.base.url'",
    "UPDATE res_users SET password='admin' where login='admin'"
]
BASE_CLEAN_COMMANDS_PH2 = [
    'TRUNCATE hr_payslip CASCADE;',
    'TRUNCATE mail_message CASCADE;',
    'TRUNCATE mail_mail CASCADE;',
    'TRUNCATE account_move_line CASCADE;',
    'TRUNCATE hr_qst_line CASCADE;',
    'TRUNCATE fsch_ticketing_ticket CASCADE;',
    'TRUNCATE ir_attachment CASCADE;',
]

if wkhtmltopdf:
    BASE_CLEAN_COMMANDS_PH1.append(
        "UPDATE ir_config_parameter SET value='%s' where key='webkit_path'" % wkhtmltopdf)

class OdooHandler(object):

    def __init__(self, opts, odoo):
        self.opts = opts
        if not odoo:
            print ('host: %s, port: %s' % (opts.host, opts.port))
            odoo = ODOO(host=opts.host, port=opts.port)
            print ('dbname: %s, user: %s, password : %s' % (opts.dbname, opts.user, opts.password))
            odoo.login(db=opts.dbname, login=opts.user, password=opts.password)
        self.odoo = odoo
        self.ail=odoo.env['account.invoice.line']
        self.pt=odoo.env['product.template']
        self.mprods = self.pt.browse(self.pt.search([('id', 'in', (5,6,7))]))
        self.ai = odoo.env['account.invoice']

    # def list_invoices(self):
    #     invoices = {
    #     }
    #     old_invoices = []
    #     for il in self.ail.browse(self.ail.search([])):
    #             # products with id's in (5,6,7) are the membership types I am interested in
    #             # they have been looked up manually
    #         if il.product_id.id in (5,6,7):
    #             ilist = invoices.get(il.name, set())
    #             ilist.update([il.partner_id])
    #             invoices[il.name] = ilist
    #             old_invoices.append(il)
    #     counter = 0
    #     for k, partners in invoices.items():
    #         for p in partners:
    #             counter +=1
    #             print '(%s)' % counter,k, p.name, p.city, p.street


    #     #today = date.today()
    #     processed = []
    #     for il in old_invoices:
    #         if il.partner_id.id in processed:
    #             continue
    #         processed.append(il.partner_id.id)
    #         # we want to create a new invoice
    #         v = copy.deepcopy(VALS)
    #         td = date.today().strftime('%Y-%m-%d')
    #         due = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
    #         v['date_invoice'] = td
    #         v['date_due'] = due
    #         v['partner_id'] = il.partner_id.id
    #         v['partner_shipping_id'] = il.partner_id.id
    #         _x, _y, invoice_line = v['invoice_line_ids'][0]
    #         invoice_line['name'] = il.name
    #         invoice_line['product_id'] = il.product_id.id
    #         invoice_line['price_unit'] = il.price_unit
    #         v['invoice_line_ids']= [[_x, _y, invoice_line]]
    #         print '--->', self.ai.create(v)


class DbHandler(object):

    def __init__(self, opts):
        self.opts = opts

    _db_connection = None
    @property
    def db_connection(self):
        if not self._db_connection:
            self._db_connection = self.get_cursor()
        return self._db_connection

    _db_name = ''
    @property
    def db_name(self):
        if not self._db_name:
            self._db_name = self.opts.db_name
        return self._db_name
    
    _postgres_port = None
    @property
    def postgres_port(self):
        if not self._postgres_port:
            self._postgres_port = self.opts.postgres_port
        return self._postgres_port

    _db_user = ''
    @property
    def db_user(self):
        if not self._db_user:
            self._db_user = self.opts.user
        return self._db_user

    _db_user_pw = ''
    @property
    def db_user_pw(self):
        if not self._db_user_pw:
            self._db_user_pw = self.opts.password
        return self._db_user_pw

    _db_host = ''
    @property
    def db_host(self):
        if not self._db_host:
            self._db_host = self.opts.db_host
        return self._db_host

    _verbose = ''
    @property
    def verbose(self):
        if not self._verbose:
            self._verbose = self.opts.verbose
        return self._verbose
    
    # ----------------------------------
    # get_connection opens a connection to a database
    def get_cursor(self, db_name=None, return_connection=True):
        """
        """
        dbuser = self.db_user
        dbhost = self.db_host
        dbpw = self.db_user_pw
        postgres_port = self.postgres_port
        if not db_name:
            db_name = self.db_name

        if dbpw:
            conn_string = "dbname='%s' user='%s' host='%s' password='%s'" % (
                db_name, dbuser, dbhost, dbpw)
        else:
            conn_string = "dbname='%s' user=%s host='%s'" % (
                db_name, dbuser, dbhost)
        if self.verbose:
            print(bcolors.WARNING)
            print('*' * 80)
            print('about to connect using:')
            print(conn_string)
            print(bcolors.ENDC)
        try:
            conn = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            if postgres_port:
                conn_string += (' port=%s' % postgres_port)
                conn = psycopg2.connect(conn_string)

        cursor_d = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if return_connection:
            return cursor_d, conn
        return cursor_d

    # clean that crap
    def clean_db(self, phase=1):
        """clean the database according to the gospel of pedrito
        """
        cursor, connection = self.get_cursor()
        if self.verbose:
            print(bcolors.WARNING)
            print('*' * 80)
        
        if phase == 1:
            commands = BASE_CLEAN_COMMANDS_PH1
        else:
            commands = BASE_CLEAN_COMMANDS_PH2
        for cmd in commands:
            cursor.execute(cmd)
            if self.verbose:
                print(cmd)
                try:
                    rows = cursor.fetchall()
                    print('result:', rows)
                except:
                    print('no result!')
        if self.verbose:
            print(bcolors.ENDC)
        connection.commit()

def main(opts):
    handler = DbHandler(opts)
    connection = handler.get_cursor()
    handler.clean_db()
    handler.clean_db(phase=2)
    print('ha gmacht wasisöll')

if __name__ == '__main__':
    usage = "fernuni_clean_db.py -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument("-H", "--dbhost",
                        action="store", dest="db_host", default='localhost',
                        help="define db host default localhost")

    parser.add_argument("-p", "--port",
                        action="store", dest="port", default=8069,
                        help="define port default 8069")

    parser.add_argument("-pp", "--postgres-port",
                        action="store", dest="postgres_port", default=5432,
                        help="define postgres port default 5432")

    parser.add_argument("-d", "--db-name",
                        action="store", dest="db_name", default='fsch_test',
                        help="define dbname default 'fsch_test'")

    parser.add_argument("-u", "--user",
                        action="store", dest="user", default='odoo',
                        help="define user default 'admin'")

    parser.add_argument("-pw", "--password",
                        action="store", dest="password", default='admin',
                        help="define password default 'admin'")

    parser.add_argument("-uo", "--use-odoo",
                        action="store_true", dest="use_odoo", default=False,
                        help="run odoo, default false")

    parser.add_argument("-v", "--verbose",
                        action="store_true", dest="verbose", default=False,
                        help="be verbose, default false")

    opts = parser.parse_args()
    main(opts)

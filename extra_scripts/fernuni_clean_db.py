import os
import sys
import shutil
from odoorpc import ODOO
from argparse import ArgumentParser
import psycopg2
import psycopg2.extras
import logging
import datetime

MY_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.insert(0, MY_PATH)
#sys.path.insert(0, '%s/extra_scripts' % MY_PATH)


try:
    from scripts.bcolors import bcolors
except ImportError:
    class bcolors:
        """
        class to color bash shell's output 
        """
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        white = "\033[1;37m"
        normal = "\033[0;00m"
        red = "\033[1;31m"
        blue = "\033[1;34m"
        green = "\033[1;32m"
        lightblue = "\033[0;34m"
        

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
    """
    this class knows how to access odoo
    """

    def __init__(self, opts, odoo=None):
        """[summary]
        
        Arguments:
            opts {namespace} -- collection of selected options
        
        Keyword Arguments:
            odoo {odoo instance} -- a running odoo instance or nothing (default: {None})

        log into a running odoo,
        Open file to dump logdata into
        """
        self.opts = opts
        if not odoo:
            print ('host: %s, port: %s' % (opts.db_host, opts.port))
            odoo = ODOO(host=opts.db_host, port=opts.port)
            print ('dbname: %s, user: %s, password : %s' % (opts.db_name, opts.user, opts.password))
            odoo.login(db=opts.db_name, login=opts.user, password=opts.password)
        self.odoo = odoo
        self.env = odoo.env
        self.ail=odoo.env['account.invoice.line']
        self.pt=odoo.env['product.template']
        self.mprods = self.pt.browse(self.pt.search([('id', 'in', (5,6,7))]))
        self.ai = odoo.env['account.invoice']

        # open log file
        # we assume it should be relative to where we are running
        try:
            self.logfile_path = os.path.normpath('%s/%s' % (MY_PATH, opts.logfile))
            self.logfile = open(self.logfile_path, 'w')
        except:
            print(bcolors.FAIL)
            print('*' * 80)
            print('could not open logfile:%s' % self.logfile_path)
            print(bcolors.ENDC)
            sys.exit()



    def _attachments_to_filesystem_init(self):
        """Set up config parameter and cron job"""
        module_name = __name__.split('.')[-3]
        ir_model_data = self.env['ir.model.data']
        location = self.env['ir.config_parameter'].get_param(
            'ir_attachment.location'
        )
        if location:
            # we assume the user knows what she's doing. Might be file:, but
            # also whatever other scheme shouldn't matter. We want to bring
            # data from the database to there
            pass
        else:
            ir_model_data._update(
                'ir.config_parameter', module_name,
                {
                    'key': 'ir_attachment.location',
                    'value': 'file',
                },
                xml_id='config_parameter_ir_attachment_location'
            )

        # synchronous behavior
        if self.env['ir.config_parameter'].get_param(
                'attachments_to_filesystem.move_during_init'
        ):
            self._attachments_to_filesystem_cron(limit=None)
            return

        # otherwise, configure our cronjob to run next night
        user = self.env.user
        next_night = datetime.now() + relativedelta(
            hour=1, minute=42, second=0)
        user_tz = user.tz or 'UTC'
        next_night = pytz.timezone(user_tz).localize(next_night).astimezone(
            pytz.utc).replace(tzinfo=None)
        if next_night < datetime.now():
            next_night += relativedelta(days=1)
        self.env.ref('%s.cron_move_attachments' % module_name).write({
            'nextcall': fields.Datetime.to_string(next_night),
            'doall': True,
            'interval_type': 'days',
            'interval_number': 1,
        })

    def dump(self, limit=10000):
        """Do the actual moving"""
        limit = int(
            self.env['ir.config_parameter'].get_param(
                'attachments_to_filesystem.limit', '0')
        ) or limit
        ir_atts = self.env['ir.attachment']
        attachments = ir_atts.search(
            [('db_datas', '!=', False)], limit=limit)
        logging.info('moving %d attachments to filestore', len(attachments))

        self.logfile.write('*' * 80)
        self.logfile.write('date: %s' % datetime.datetime.now())
        self.logfile.write('*' * 80)
        self.logfile.write('\n')
        # attachments can be big, so we read every attachment on its own
        for counter, a_id in enumerate(attachments, start=1):
            attachment = ir_atts.browse([a_id])
            # attachment_data -> [{attachement, id, res_model}]
            attachment_data = attachment.read(['datas', 'res_model'])[0]
            if attachment_data['res_model'] and not self.env.registry.get(
                    attachment_data['res_model']
            ):
                logging.warning(
                    'not moving attachment %d because it links to unknown '
                    'model %s', attachment.id, attachment_data['res_model'])
                continue
            try:
                attachment.write({
                    'datas': attachment_data['datas'],
                    'db_datas': False,
                })
            except Exception:
                logging.exception('Error moving attachment #%d', attachment.id)
            if not counter % (len(attachments) / 100 or limit):
                logging.info('moving attachments: %d done', counter)
                data = {
                    fname :attachment.datas_fname,
                    dname : attachment.display_name,
                    store_fname : attachment.store_fname,
                    size : len(attachment.datas),
                }
                line = 'name: %(fname)s, %(dname)s, store: %(store_fname)s, size: %(size)s\n' % data
                self.logfile.write(line)




class DbHandler(object):
    """class to access a database directly using raw sql    
    """

    def __init__(self, opts):
        """[summary]
        
        Arguments:
            opts {namespace} -- collection of selected options
        
        Keyword Arguments:
            odoo {odoo instance} -- a running odoo instance or nothing (default: {None})
        """
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
    if opts.clean:        
        handler = DbHandler(opts)
        connection = handler.get_cursor()
        handler.clean_db()
        handler.clean_db(phase=2)
        print('ha gmacht wasisöll')
    elif opts.dump: 
        handler = OdooHandler(opts)
        handler.dump()
    else:
        print(bcolors.WARNING)
        print('*' * 80)
        print('Please indicate either -c --clean or -dumpa --dump-attachements')
        print(bcolors.ENDC)
        
if __name__ == '__main__':
    usage = "fernuni_clean_db.py -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument("-c", "--clean",
                        action="store_true", dest="clean", default=False,
                        help="Clean database")

    parser.add_argument("-H", "--dbhost",
                        action="store", dest="db_host", default='localhost',
                        help="define db host default localhost")

    parser.add_argument("-l", "--log-file",
                        action="store", dest="logfile", default='dump.log',
                        help="define logfile to to to print the path of the removed attchements to. Default dump.log")

    parser.add_argument("-p", "--port",
                        action="store", dest="port", default=8069,
                        help="define port default 8069")

    parser.add_argument("-pp", "--postgres-port",
                        action="store", dest="postgres_port", default=5432,
                        help="define postgres port default 5432")

    parser.add_argument("-dumpa", "--dump-attachements",
                        action="store_true", dest="dump", default=False,
                        help="Dump attachments to the filesystem")

    parser.add_argument("-d", "--db-name",
                        action="store", dest="db_name", default='fsch_test',
                        help="define dbname default 'fsch_test'")

    parser.add_argument("-u", "--user",
                        action="store", dest="user", default='admin',
                        help="define user default 'admin'")

    parser.add_argument("-pw", "--password",
                        action="store", dest="password", default='admin',
                        help="define password default 'admin'")

    parser.add_argument("-uo", "--use-odoo",
                        action="store_true", dest="use_odoo", default=False,
                        help="run odoo, default false")

    parser.add_argument("-v", "--verbose",
                        action="store_true", dest="verbose", default=True,
                        help="be verbose, default true")

    opts = parser.parse_args()
    main(opts)

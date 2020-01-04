import os
import sys
import shutil
from odoorpc import ODOO
from argparse import ArgumentParser
import psycopg2
import psycopg2.extras
import logging
import datetime
import yaml
from io import StringIO

MY_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.insert(0, MY_PATH)
# sys.path.insert(0, '%s/extra_scripts' % MY_PATH)


try:
    from scripts.bcolors import bcolors
except ImportError:

    class bcolors:
        """
        class to color bash shell's output 
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
        """
        self.opts = opts
        if not odoo:
            print("host: %s, port: %s" % (opts.db_host, opts.port))
            odoo = ODOO(host=opts.db_host, port=opts.port)
            print(
                "dbname: %s, user: %s, password : %s"
                % (opts.db_name, opts.user, opts.password)
            )
            odoo.login(db=opts.db_name, login=opts.user, password=opts.password)
        self.odoo = odoo
        self.env = odoo.env
        self.ail = odoo.env["account.invoice.line"]
        self.pt = odoo.env["product.template"]
        self.mprods = self.pt.browse(self.pt.search([("id", "in", (5, 6, 7))]))
        self.ai = odoo.env["account.invoice"]

        # open log file
        # we assume it should be relative to where we are running
        try:
            self.logfile_path = os.path.normpath("%s/%s" % (MY_PATH, opts.logfile))
            self.logfile = open(self.logfile_path, "w")
        except:
            print(bcolors.FAIL)
            print("*" * 80)
            print("could not open logfile:%s" % self.logfile_path)
            print(bcolors.ENDC)
            sys.exit()

    def _attachments_to_filesystem_init(self):
        """Set up config parameter and cron job"""
        module_name = __name__.split(".")[-3]
        ir_model_data = self.env["ir.model.data"]
        location = self.env["ir.config_parameter"].get_param("ir_attachment.location")
        if location:
            # we assume the user knows what she's doing. Might be file:, but
            # also whatever other scheme shouldn't matter. We want to bring
            # data from the database to there
            pass
        else:
            ir_model_data._update(
                "ir.config_parameter",
                module_name,
                {"key": "ir_attachment.location", "value": "file"},
                xml_id="config_parameter_ir_attachment_location",
            )

        # synchronous behavior
        if self.env["ir.config_parameter"].get_param(
            "attachments_to_filesystem.move_during_init"
        ):
            self._attachments_to_filesystem_cron(limit=None)
            return

        # otherwise, configure our cronjob to run next night
        user = self.env.user
        next_night = datetime.now() + relativedelta(hour=1, minute=42, second=0)
        user_tz = user.tz or "UTC"
        next_night = (
            pytz.timezone(user_tz)
            .localize(next_night)
            .astimezone(pytz.utc)
            .replace(tzinfo=None)
        )
        if next_night < datetime.now():
            next_night += relativedelta(days=1)
        self.env.ref("%s.cron_move_attachments" % module_name).write(
            {
                "nextcall": fields.Datetime.to_string(next_night),
                "doall": True,
                "interval_type": "days",
                "interval_number": 1,
            }
        )


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

    _db_name = ""

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

    _db_user = ""

    @property
    def db_user(self):
        if not self._db_user:
            self._db_user = self.opts.user
        return self._db_user

    _db_user_pw = ""

    @property
    def db_user_pw(self):
        if not self._db_user_pw:
            self._db_user_pw = self.opts.password
        return self._db_user_pw

    _db_host = ""

    @property
    def db_host(self):
        if not self._db_host:
            self._db_host = self.opts.db_host
        return self._db_host

    _verbose = ""

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
                db_name,
                dbuser,
                dbhost,
                dbpw,
            )
        else:
            conn_string = "dbname='%s' user=%s host='%s'" % (db_name, dbuser, dbhost)
        if self.verbose:
            print(bcolors.WARNING)
            print("*" * 80)
            print("about to connect using:")
            print(conn_string)
            print(bcolors.ENDC)
        try:
            conn = psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            if postgres_port:
                conn_string += " port=%s" % postgres_port
                conn = psycopg2.connect(conn_string)

        cursor_d = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if return_connection:
            return cursor_d, conn
        return cursor_d


def check_yaml(opts, vals={}):
    yaml_file = opts.yaml_file
    if not os.path.exists(yaml_file):
        print(bcolors.FAIL)
        print("*" * 80)
        print("cant open %s" % yaml_file)
        print(bcolors.ENDC)
        sys.exit()
    with open(yaml_file) as f:
        raw_yaml_data = f.read()
    # it can be hard to find an error when varibales are not well define
    # so check the content line by line
    counter = -1
    raw_yaml_data_stripped = []
    for line in raw_yaml_data.split("\n"):
        counter += 1
        if line.strip().startswith("#"):
            continue
        try:
            # just provoke an error if a value is used not in vals
            line % vals
            raw_yaml_data_stripped.append(line)
        except Exception:
            print(bcolors.FAIL)
            print("*" * 80)
            print("file %s" % yaml_file)
            print("line %s: %s has a problem" % (counter, line))
            print(bcolors.ENDC)
            raise
    raw_yaml_data = "\n".join(raw_yaml_data_stripped) % vals
    try:
        result = yaml.load(StringIO(raw_yaml_data), Loader=yaml.FullLoader)
        return result
    except yaml.parser.ParserError as e:
        print(bcolors.FAIL)
        print("*" * 80)
        print("file %s can not be parsed" % yaml_file)
        print(bcolors.ENDC)
        raise
    except Exception as e:
        print(bcolors.FAIL)
        print("*" * 80)
        print("file %s can not be parsed" % yaml_file)
        print(bcolors.ENDC)
        raise


def main(opts):
    if opts.yaml_file:
        print(check_yaml(opts).keys())


if __name__ == "__main__":
    usage = "check_yaml -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument(
        "-H",
        "--dbhost",
        action="store",
        dest="db_host",
        default="localhost",
        help="define db host default localhost",
    )

    parser.add_argument(
        "-p",
        "--port",
        action="store",
        dest="port",
        default=8069,
        help="define port default 8069",
    )

    parser.add_argument(
        "-pp",
        "--postgres-port",
        action="store",
        dest="postgres_port",
        default=5432,
        help="define postgres port default 5432",
    )

    parser.add_argument(
        "-d",
        "--db-name",
        action="store",
        dest="db_name",
        default="fsch_test",
        help="define dbname default 'fsch_test'",
    )

    parser.add_argument(
        "-u",
        "--user",
        action="store",
        dest="user",
        default="admin",
        help="define user default 'admin'",
    )

    parser.add_argument(
        "-pw",
        "--password",
        action="store",
        dest="password",
        default="admin",
        help="define password default 'admin'",
    )

    parser.add_argument(
        "-uo",
        "--use-odoo",
        action="store_true",
        dest="use_odoo",
        default=False,
        help="run odoo, default false",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=True,
        help="be verbose, default true",
    )

    parser.add_argument(
        "-y",
        "--yaml-file",
        action="store",
        dest="yaml_file",
        help="define yaml file to check",
    )

    opts = parser.parse_args()
    main(opts)

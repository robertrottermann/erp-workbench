#!/usr/bin/env python
# -*- coding: utf-8 -*-
# /home/robert/projects/odoo13/odoo13/downloads/odoo-13.0.post20210902/odoo/addons/account/models/account.py
"""
A script, that install odoo 14 with odoobuild modules
"""
import os, sys
import urllib.request, urllib.error, urllib.parse
from argparse import ArgumentParser, Namespace
import argparse
import getpass
import psycopg2
import psycopg2.extras
import datetime
import copy

class bcolors:
    """
    allow to colour the bash output
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


# make sure we are in a virtualenv
# robert: i usualy test in wingide
if not os.environ.get("VIRTUAL_ENV") and not os.environ.get("WINGDB_ACTIVE"):
    print(bcolors.WARNING)
    print("not running in a virtualenv")
    print("activate the worbench environment executing:")
    print("workon workbench or somthing similar")
    print("it has to have installed at least the foollowing libs:")
    print("OdooRPC")
    print("psycopg2")
    print(bcolors.ENDC)
    sys.exit()

try:
    import odoorpc
except ImportError:
    print(bcolors.WARNING + "please install odoorpc")
    print("execute bin/pip install -r install/requirements.txt" + bcolors.ENDC)
    sys.exit()


class MyNamespace(Namespace):
    # we need a namespace that just ignores unknown options
    def __getattr__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        return None
    # def __setattr__(self, key, val):
    #     if  key in self.__dict__.keys():
    #         self.__dict__[key] = val
    #     else:
    #         super().__setattr__(key, val)


class OdoobuildInstaller(object):
    """setup a fernuni installation se we can test it
    This means mostly install some modules and users
    and assign them roles
    """

    #db_name = "odoobuild"
    rpc_host = "localhost"
    rpc_port = 8069
    rpc_user = "admin"
    rpc_user_pw = "admin"
    db_user = getpass.getuser()
    db_host = "localhost"
    db_user_pw = "admin"
    postgres_port = 5432



    _odoo = None
    opts = MyNamespace()

    def __init__(self, args):
        """
            what parts should be done. List of a=all,l=languages,m=own-modules,M=odoo-modules,u=users.
            When empty Mmu is assumed.
        """
        self.opts = args
        # start wit importing file that declares data for this site
        # it is defined in the imp parameter
        import_file_name = args.import_file_name
        self.site_opts = __import__(import_file_name)
        param = args.what

    def _missing_o_message(self, what):
        print(bcolors.WARNING)
        print("*" * 80)
        print("no %s defined" % what)
        print(bcolors.ENDC)
        return
 
    @property
    def _contract_types(self):
        try:
            return self.site_opts.CONTRACT_TYPES
        except:
            return self._missing_o_message('CONTRACT_TYPES')
            
    @property
    def _groups(self):
        try:
            return self.site_opts.GROUPS
        except:
            return self._missing_o_message('GROUPS')

    @property
    def _mailhandlers(self):
        try:
            return self.site_opts.MAILHANDLERS
        except:
            return self._missing_o_message('MAILHANDLERS')

    @property
    def _my_dbname(self):
        try:
            return self.site_opts.MY_DBNAME
        except:
            return self._missing_o_message('MY_DBNAME')

    @property
    def _my_port(self):
        try:
            return site_opts.MY_PORT
        except:
            return self._missing_o_message('MY_PORT')

    @property
    def _my_host(self):
        try:
            return self.site_opts.MY_HOST
        except:
            return self._missing_o_message('MY_HOST')

    @property
    def _users(self):
        try:
            return self.site_opts.USERS
        except:
            return self._missing_o_message('USERS')

    @property
    def _staff(self):
        try:
            return self.site_opts.STAFF
        except:
            return self._missing_o_message('STAFF')

    @property
    def _site_addons(self):
        try:
            return self.site_opts.SITE_ADDONS
        except:
            return self._missing_o_message('SITE_ADDONS')

    # _own_addons is the list of addons_entries in the odoo config
    @property
    def _own_addons(self):
        try:
            return self.site_opts.SITE_ADDONS
        except:
            return self._missing_o_message('OWN_ADDONS')

    @property
    def _languages(self):
        try:
            return self.site_opts.LANGUAGES
        except:
            return self._missing_o_message('LANGUAGES')

    # ----------------------------------
    #  collects info on what modules are installed
    # or need to be installed
    # @req : list of required modules. If this is an empty list
    #         use any module
    # @uninstalled  : collect unistalled modules into this list
    # @to_upgrade   :collect modules that expect upgrade into this list
    def collect_info(
        self, cursor, req, installed, uninstalled, to_upgrade, all_list=[], apps=[]
    ):
        opts = self.opts
        s = "select * from ir_module_module"
        cursor.execute(s)
        rows = cursor.fetchall()
        all = not req
        updlist = []
        for r in rows:
            n = r.get("name")
            s = r.get("state")
            i = r.get("id")
            if n in req or all:
                if n in req:
                    req.pop(req.index(n))
                if s == "installed":
                    if r.get("application"):
                        apps.append([i, n])
                    if all or updlist == "all" or n in updlist:
                        installed.append((i, n))
                    continue
                elif s in ["uninstalled", "to install"]:
                    uninstalled.append((i, n))
                elif s == "to upgrade":
                    to_upgrade.append(n)
                else:
                    if not s == "uninstallable":
                        print(n, s, i)

    # ----------------------------------
    # get_cursor opens a connection to a database
    # on which we can execute sql statements
    def get_cursor(self, db_name=None, return_connection=None):
        """
        """
        dbuser = self.db_user
        dbhost = self.db_host
        dbpw = self.db_user_pw
        postgres_port = self.postgres_port
        if not db_name:
            db_name = self.opts.db_name

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
            if postgres_port:
                conn_string += " port=%s" % postgres_port
                conn = psycopg2.connect(conn_string)

        cursor_d = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if return_connection:
            return cursor_d, conn
        return cursor_d

    # ----------------------------------
    # get_odoo returns an "live" odoo object
    def get_odoo(self, no_db=False, verbose=False):
        if not self._odoo:
            """
            get_module_obj logs into odoo and then
            returns an object with which we can manage the list of modules
            bail out if we can not log into a running odoo site

            """
            verbose = verbose or self.opts.verbose
            db_name = self._my_dbname
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
                    try:
                        odoo.login(db_name, rpcuser, rpcpw)
                    except:
                        if verbose:
                            print("login failed, will retry with pw admin:")
                            print(
                                "dbname:%s, rpcuser:%s, rpcpw: admin"
                                % (db_name, rpcuser)
                            )
                            print("*" * 80)
                        odoo.login(db_name, rpcuser, "admin")
            except odoorpc.error.RPCError:
                print(
                    bcolors.FAIL
                    + "could not login to running odoo server host: %s:%s, db: %s, user: %s, pw: %s"
                    % (rpchost, rpcport, db_name, rpcuser, rpcpw)
                    + bcolors.ENDC
                )
                if verbose:
                    return odoo
                return
            except urllib.error.URLError:
                print(
                    bcolors.FAIL
                    + "could not login to odoo server host: %s:%s, db: %s, user: %s, pw: %s"
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
        return self._odoo

    def install_languages(self):
        """
        install all languages in the target
        languages: list of language codes like ['de_CH, 'fr_CH']

        return:
            dictonary {code : id, ..}

        like ["de_CH", "de_DE", "fr_CH"]
        """
        # what fields do we want to handle?
        # we get the source and target model
        languages = set(self._languages())
        if not languages:
            return {}
        odoo = self.get_odoo()
        if not odoo:
            print("oddo is not running")
            print("make sure odoo is running at the given address" + bcolors.ENDC)
            return
        langs = odoo.env["base.language.install"]
        result = {}
        lang_obj = odoo.env["res.lang"]
        for code in languages:
            if not langs.search([("lang", "=", code)]):
                # from pdb import set_trace
                # set_trace()
                #odoo.env['ir.translation']._load_module_terms(['base'], [code])
                langs.browse(langs.create({'lang': code})).lang_install()
                #lang_obj.load_lang(code)
            result[code] = langs.search([("lang", "=", code)])
        return result

    # ----------------------------------
    # get_module_obj returns the module.module object
    # on which we can install, uninstall and update modules
    def get_module_obj(self):
        """
            get the ir.module.module
        """
        odoo = self.get_odoo()
        if not odoo:
            return
        module_obj = odoo.env["ir.module.module"]
        return module_obj

    # ----------------------------------
    # install odoo modules
    # or install own modules depending on the parameter what
    def install_own_modules(self, what="site_addons", quiet=False):
        """
        Install either the odoo apps from site_addons
        or the "own" addons from provided by fernuni/OCA
        """
        module_obj = None
        req = []
        if what == "site_addons":
            # addons decalared in addons are the ones not available from odoo directly
            site_addons = self._site_addons
            req = site_addons
        elif what == "own_addons":
            # addons declared in the own_addons are from fernuni or OCA
            req = self._own_addons

        if req:
            installed = []
            uninstalled = []
            to_upgrade = []

            module_obj = self.get_module_obj()
            if not module_obj:
                # should not happen, means we have no contact to the erp site
                return
            # refresh the list of updatable modules within the erp site
            module_obj.update_list()

            try:
                cursor = self.get_cursor()
            except Exception as e:
                return
            self.collect_info(cursor, req, installed, uninstalled, to_upgrade, req[:])
            if req:
                print("*" * 80)
                print("the following modules where not found:", req)
                print("you probably have to download them")
                print("*" * 80)
            if uninstalled:
                print(
                    "the following modules need to be installed:",
                    [u[1] for u in uninstalled],
                )
                i_list = [il[0] for il in uninstalled]
                n_list = [il[1] for il in uninstalled]
                print("*" * 80)
                print(
                    bcolors.OKGREEN + "installing: " + bcolors.ENDC + ",".join(n_list)
                )
                load_demo = True
                if 0: #self.opts.single_step or 1:
                    for mname in i_list:
                        module = module_obj.browse([mname])
                        if load_demo:
                            module.demo = True
                        print(
                            "installing:%s%s%s"
                            % (bcolors.OKGREEN, module.name, bcolors.ENDC)
                        )
                        module.button_immediate_install()
                else:
                    modules = module_obj.browse(i_list)
                    #if load_demo:
                        #for m in modules:
                            #m.demo = True
                    modules.button_immediate_install()
                print(
                    bcolors.OKGREEN
                    + "finished installing: "
                    + bcolors.ENDC
                    + ",".join(n_list)
                )
                print("*" * 80)


    # ----------------------------------
    # install mail handlers
    # depending on the parameter do_incomming install both or only outgoing
    def install_mail_handler(self, do_incoming=True):
        # odoo 13, flags when external mailservers are used
        mailhandlers = self._mailhandlers
        if not mailhandlers:
            return
        odoo = self.get_odoo()
        res_config_settings = odoo.env["res.config.settings"]
        try:
            try:
                email_setting = res_config_settings.search(
                    [("external_email_server_default", "=", True)]
                )
            except:
                email_setting = []
            odoo.env.ref("base.res_config_settings_view_form").write(
                {"external_email_server_default": True}
            )
            if not email_setting:
                if not email_setting:
                    email_setting = res_config_settings.create(
                        {"external_email_server_default": True}
                    )  # .execute()
                    res_config_settings.external_email_server_default = True
        except:
            pass
        print(bcolors.OKGREEN, "*" * 80)
        if do_incoming:
            # write the incomming email server
            i_server = odoo.env["fetchmail.server"]
            # get the first server
            print("incomming email")
            i_ids = i_server.search([])
            i_id = 0
            i_data = mailhandlers.get('mail_incomming')
            if i_data:
                i_id = i_ids.create(i_data)
            else:
                print("no incomming mail handler found")
            print("*" * 80)
            if i_ids:
                i_id = i_ids[0]
            if i_id:
                incomming = i_server.browse([i_id])
                incomming.write(i_data)
            else:
                incomming = i_server.create(i_data)
            print(i_data)
        print("-" * 80)
        print("outgoing email")
        # now do the same for the outgoing server
        o_data = mailhandlers.get('mail_outgoing')
        if not o_data:
            print("no outgoing mail handler found")
            print("*" * 80, bcolors.ENDC)
            return
        o_server = odoo.env["ir.mail_server"]
        # get the first server
        o_ids = o_server.search([])
        o_id = 0
        if o_ids:
            o_id = o_ids[0]
        if o_id:
            outgoing = o_server.browse([o_id])
            outgoing.write(o_data)
        else:
            o_server.create(o_data)
        print(o_data)
        print("*" * 80, bcolors.ENDC)

    # ----------------------------------
    # create users
    # we do this in several steps
    # 1. we create the users, assigning them a name, login and password
    # 2. for the staff members, we create employees, check what groups they belong and add the user to the groups
    def create_users(self, force=False):
        odoo = self.get_odoo()
        if not odoo:
            return
        users_o = odoo.env["res.users"]
        users_ox = users_o.with_user(odoo.env.context, 1)
        users = self._users
        groups = self._groups
        # groups_o = odoo.env['res.groups']
        if users:
            for login, user_info in list(users.items()):
                user_data = {}
                user_data["name"] = login
                user_data["email"] = "%s@test.ch" % login
                user_data["login"] = login
                user_data["tz"] = "Europe/Zurich"
                user_data["password"] = "login"
                # check if user exists
                user_ids = users_o.search([("login", "=", login)])
                if user_ids:
                    try:
                        user = users_o.browse(user_ids)
                        if force:
                            user.write(user_data)
                    except:
                        pass
                else:
                    # user = odoo.env['res.users'].sudo().with_context().create(user_data)
                    user_id = users_o.create(user_data)
                    if user_id or isinstance(user_id, int):
                        user_ids = [user_id]

                # get groups to be assigned
                group_id = groups[user_info]
                group = odoo.env.ref(group_id)
                group.write({"users": [(4, user_ids[0])]})
        staff = self._staff
        if staff:
            for login, user_info in list(staff.items()):
                u_groups = user_info.pop("groups")
                user_data = user_info
                user_data["email"] = "%s@test.ch" % login
                user_data["tz"] = "Europe/Zurich"
                user_data["password"] = "login"
                # check if user exists
                user_ids = users_o.search([("login", "=", user_data['login'])])
                if user_ids:
                    try:
                        user = users_o.browse(user_ids)
                        if force:
                            user.write(user_data)
                    except:
                        pass
                else:
                    # user = odoo.env['res.users'].sudo().with_context().create(user_data)
                    user_id = users_o.create(user_data)
                    if user_id or isinstance(user_id, int):
                        user_ids = [user_id]
                for group_id in u_groups:
                    group = odoo.env.ref(group_id)
                    group.write({"users": [(4, user_ids[0])]})

    # ----------------------------------
    # _create_accounts auxiliary function that does the real creation of G/L accounts
    def _create_accounts(self, accounts):
        odoo = self.get_odoo()
        if not odoo:
            return
        acounts_o = odoo.env["account.account"]
        for acc in accounts:
            acounts_ex = acounts_o.search([('name', '=', acc['name'])]) # existing accounts
            acounts_ex_code = acounts_o.search([('code', '=', acc['code'])]) # existing accounts
            if not acounts_ex:
                if acounts_ex_code:
                    print(bcolors.OKBLUE)
                    print("account name for account %s differs" % acc['code'])
                    print(bcolors.ENDC)
                else:
                    acounts_o.create(acc)

    # ----------------------------------
    # create_accounts creates G/L accounts
    def create_accounts(self):
        try:
            accounts = self.site_opts.ACCOUNT_ACCOUNT
        except:
            pass
        if accounts:
            self._create_accounts(accounts)

    # ----------------------------------
    # install_objects creates objects in the database like users, contacts, etc
    # to do so we need to add a call to the respective method that creates the objects
    # only objects, that are listed in the imported "site_samples" file, are created
    def install_objects(self):
        odoo = self.get_odoo()
        if not odoo:
            return
        # create G/L accounts
        self.create_accounts()

        # install laguages
        self.install_languages()


parser = argparse.ArgumentParser(description='Setup a odoobuild site.')
parser.add_argument(
        "-w",
        "--what",
        action="store",
        dest="what",
        default="",
        help="""
            what parts should be done. List of a=all,l=languages,m=own-modules,M=odoo-modules,u=users.
            When empty Mmu is assumed.
        """,
    )
parser.add_argument(
        "-d",
        "--db_name",
        action="store",
        dest="db_name",
        default="odoobuild",
        help="""
            what db_name to use, by default odoobuild
        """,
    )
parser.add_argument(
        "-i",
        "--install-objects",
        action="store_true",
        dest="install_objects",
        default=False,
        help="""
            Install objects like installtypes, contract ..
        """,
    )

parser.add_argument(
        "-imp",
        "--import-file-name",
        action="store",
        dest="import_file_name",
        default="site_samples",
        help="""
            name of the file to import declaring objects to handle. Default site_samples.py
        """,
    )

if __name__ == "__main__":
    opts = parser.parse_args()
    installer = OdoobuildInstaller(opts)
    installer.get_odoo(verbose=True)
    installer.install_own_modules()
    installer.install_own_modules(what="own_addons")
    installer.install_mail_handler()
    installer.install_languages()
    installer.create_users()
    if 0: #installer.opts.languages:
        try:
        except:
            print(bcolors.red)
            print("could not install languages")
            print(bcolors.ENDC)
    if 1: #installer.opts.install_objects:
        installer.install_objects()

# bin/python
# -*- encoding: utf-8 -*-

# import warnings
import sys
import os
# import logging
import re
import socket
import subprocess
from subprocess import PIPE
from config import SITES, SITES_LOCAL, \
    NO_NEED_SERVER_IP, ODOO_VERSIONS, FLECTRA_VERSIONS, \
    DB_PASSWORD
#from config.config_data.base_info import BASE_DEFAULTS
from config.config_data.servers_info import REMOTE_SERVERS
from scripts.bcolors import bcolors
from scripts.name_completer import SimpleCompleter
import stat
import psycopg2
import psycopg2.extras
import urllib.request, urllib.error, urllib.parse
from pprint import pformat
from scripts.update_local_db import DBUpdater
from site_desc_handler.sdesc_utilities import _construct_sa
from scripts.utilities import collect_options, find_addon_names
from scripts.messages import SITE_HAS_NO_REMOTE_INFO, SITE_UNKNOW_IP, EXTRA_SCRIPT_NOT_EXISTING, \
    MODULE_MISSING, SITE_DESCRIPTION_RELOADED, ERP_NOT_RUNNING, ERP_NOT_RUNNING, ERP_NOT_RUNNING, \
    OWN_ADDONS_NO_DEVELOP, AMARKER, AMARKER, ABLOCK, AMARKER, AMARKER, ABLOCK, ALIAS_HEADER, \
    ALIAS_LINE, ALIAS_LINE, ALIAS_LINE_PULL, ALIAS_LENGTH, ALIAS_LENGTH, ALIAS_LINE, ALIAS_LINE, \
    ALIAS, WWB, WWLI, WWB, DOCKER_CLEAN, DOC_ET_ALL, ALIASC, ALIASOO, VIRTENV_D
import shutil
from docker_handler.docker_mixin import DockerHandlerMixin

# refactoring 
from site_desc_handler.sdesc_utilities import flatten_sites
from site_desc_handler.site_desc_handler_mixin import SiteDescHandlerMixin
#from site_desc_handler.handle_remote_data import collect_remote_info
from scripts.properties_mixin import PropertiesMixin


# the templatefile contains placeholder
# that will be replaced with real values
BASE_INFO_TEMPLATE = """base_info = %s"""
"""
create_new_project.py
---------------------
create a new erp-workbench project so we can easily maintain a local and a remote
set of configuration files and keep them in sync.

It knows enough about the erp to be able to treat some special values correctly

"""

class RPC_Mixin(object):
    _odoo = None

    # ---------------------------------------------------------------------
    # RPC stuff
    # ---------------------------------------------------------------------

    # ----------------------------------
    # get_connection opens a connection to a database
    def get_cursor(self, db_name=None, return_connection=None):
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

    # ----------------------------------
    # get_module_obj logs into odoo and then
    # returns an object with which we can manage the list of modules
    # bail out if we can not log into a running odoo site

    # the databse is access directly
    # the odoo server is accessed uding odoo's rpc_api.
    # read from either the config data or can be set using command line options.
    # --- database ---
    # - db_user : the user to access the servers database
    #   to check what modules are allready installed the servers database
    #   has to be accessed.
    #   option: "-dbu", "--dbuser".
    #   default: logged in user
    # - db_password
    #   option: "-p", "--dbpw".
    #   default: admin
    # - dbhost: the host on which the database is running
    #   option: "-dbh", "--dbhost"
    #   default: localhost.
    # --- user accessing the running odoo server ---
    # - rpcuser: the login user to access the odoo server
    #   option: "-rpcu", "--rpcuser"
    #   default: admin.
    # - rpcpw: the login password to access the odoo server
    #   option: "-P", "--rpcpw"
    #   default: admin.
    # - rpcport: the the odoo server is running at
    #   option: "-PO", "--port"
    #   default: 8069.

    def get_odoo(self, no_db=False, verbose=False):
        if not self._odoo:
            """
            get_module_obj logs into odoo and then
            returns an object with which we can manage the list of modules
            bail out if we can not log into a running odoo site

            the databse is access directly
            the odoo server is accessed uding odoo's rpc_api.
            read from either the config data or can be set using command line options.
            --- database ---
            - db_user : the user to access the servers database
              to check what modules are allready installed the servers database
              has to be accessed.
              option: "-dbu", "--dbuser".
              default: logged in user
            - db_password
              option: "-p", "--dbpw".
              default: admin
            - dbhost: the host on which the database is running
              option: "-dbh", "--dbhost"
              default: localhost.
            --- user accessing the running odoo server ---
            - rpcuser: the login user to access the odoo server
              option: "-rpcu", "--rpcuser"
              default: admin.
            - rpcpw: the login password to access the odoo server
              option: "-P", "--rpcpw"
              default: admin.
            - rpcport: the the odoo server is running at
              option: "-PO", "--port"
              default: 8069.
            """
            verbose = verbose or self.opts.verbose
            try:
                import odoorpc
            except ImportError:
                print(bcolors.WARNING + 'please install odoorpc')
                print(
                    'execute bin/pip install -r install/requirements.txt' + bcolors.ENDC)
                return
            try:
                # if we want to access a docker container, rpsuser and rpcpw has to be adjusted beforehand
                db_name = self.db_name
                rpchost = self.rpc_host
                rpcport = self.rpc_port
                rpcuser = self.rpc_user
                rpcpw = self.rpc_user_pw
                # login
                if verbose:
                    print('*' * 80)
                    print('about to open connection to:')
                    print('host:%s, port:%s, timeout: %s' %
                          (rpchost, rpcport, 1200))
                #rpchost und rpcort sind nich von docker!!!!!
                odoo = odoorpc.ODOO(rpchost, port=rpcport, timeout=1200)
                if not no_db:  # used when creating db
                    if verbose:
                        print('about to login:')
                        print('dbname:%s, rpcuser:%s, rpcpw: %s' %
                              (db_name, rpcuser, rpcpw))
                        print('*' * 80)
                    try:
                        odoo.login(db_name, rpcuser, rpcpw)
                    except:
                        if verbose:
                            print('login failed, will retry with pw admin:')
                            print('dbname:%s, rpcuser:%s, rpcpw: admin' %
                                  (db_name, rpcuser))
                            print('*' * 80)
                        odoo.login(db_name, rpcuser, 'admin')
 
            except odoorpc.error.RPCError:
                print(bcolors.FAIL + 'could not login to running odoo server host: %s:%s, db: %s, user: %s, pw: %s' %
                      (rpchost, rpcport, db_name, rpcuser, rpcpw) + bcolors.ENDC)
                if verbose:
                    return odoo
                return
            except urllib.error.URLError:
                print(bcolors.FAIL + 'could not login to odoo server host: %s:%s, db: %s, user: %s, pw: %s' %
                      (rpchost, rpcport, db_name, rpcuser, rpcpw))
                print('connection was refused')
                print('make sure odoo is running at the given address' + bcolors.ENDC)
                return
            self._odoo = odoo
        return self._odoo

    def get_module_obj(self):
        odoo = self.get_odoo()
        if not odoo:
            return
        module_obj = odoo.env['ir.module.module']
        return module_obj

    def get_erp_modules(self):
        from odoorpc.error import RPCError
        modules = self.get_module_obj()
        if not modules:
            return
        mlist = modules.search([('application', '=', True)])
        result = {}
        for mid in mlist:
            m = modules.browse(mid)
            result[m.name] = m.shortdesc
        mlist = modules.search([('application', '=', False)])
        result2 = {}
        for mid in mlist:
            try:
                m = modules.browse(mid)
                result2[m.name] = m.shortdesc
            except RPCError as e:
                print(str(e))

        return result, result2

    def install_languages(self, languages):
        """
        install all languages in the target
        args:
            languages: list of language codes like ['de_CH, 'fr_CH']

        return:
            dictonary {code : id, ..}     
        """
        # what fields do we want to handle?
        # we get the source and target model
        languages = set(languages)
        langs = self.get_odoo().env['base.language.install']
        result = {}
        for code in languages:
            if not langs.search([('lang', '=', code)]):
                langs.browse(langs.create({'lang': code})).lang_install()
            result[code] = langs.search([('lang', '=', code)])[0]
        return result


class InitHandler(RPC_Mixin, SiteDescHandlerMixin, DockerHandlerMixin, PropertiesMixin):
    # need_login_info will be set to false by local opperations
    # like --add-site that need no login
    need_login_info = True

    def __init__(self, opts, sites, parsername=''):
        if opts.name:
            self.site_names = [opts.name]
        else:
            self.site_names = []
        self.opts = opts
        if sites:
            self._sites = sites
        else:
            self._sites = SITES
        
        if callable(self._check_parsed):
            self._check_parsed()
        
        # #the following init stuff should be called from PropertiesMixin
        # #what about flatten site?
        # # set up values for proerties dealing with remote data
        # collect_remote_info(self, self.site)
        # # call the DockerHandlerMixin to setup the docker environment
        # self.setup_docker_env(self.site)
        # #self.check_name(no_completion=True, must_match=True)
        ## # resolve inheritance within sites
        #flatten_sites(self._sites)
        # # collect info on what parser and what options are selected
        parsername, selected, options = collect_options(opts)
        self.selections = selected
        if not selected:
            # when testing we migth start without a name
            if not opts.__dict__.get('skip_name'):
                self._complete_selection(
                    parsername, options, prompt='%s-options ?' % parsername)
            # check again if selected
            parsername, selected, options = collect_options(opts)
        self.parsername = parsername

        # now we can really check whether name is given and valid
        # while converting to workbench: I think wemake all options check 
        # themselfs whether they need a name
        # self.check_name()
        # when we want to drop the site, nothing more needs to be done
        if 'drop_site' in vars(opts):
            if opts.drop_site:
                return
                    

            
    def running_remote(self):
        # replace values that should be different when running remotely
        # this should be done in a mor systematic way.when I use massmailing, a click to the send button
        remote_info = self.site.get('remote_server', {})
        remote_url = remote_info.get('remote_url')

        def get_ipv4_address():
            """
            Returns IP address(es) of current machine.
            :return:
            """
            p = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE)
            ifc_resp = p.communicate()
            if ifc_resp:
                ifc_resp = ifc_resp[0].decode('utf8')
            patt = re.compile(
                r'inet\s*\w*\S*:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
            resp = patt.findall(ifc_resp)
            return resp

        return remote_url in get_ipv4_address()

    def execute_script(self):
        """
        execute externally defined script
        it must have a run command

        """
        import imp
        opts = self.opts
        extra_scripts_path = self.base_info.get(
            'extra_scripts_path', '%s/extra_scripts/' % self.default_values.get('sites_home'))
        script = opts.executescript
        run_fun = 'run'
        self.get_odoo() # set up connection
        full_path = '%s/%s' % (extra_scripts_path, script)
        if os.path.exists('%s.py' % full_path):
            full_path = '%s.py' % full_path
        if os.path.exists(full_path):
            print(full_path)
            mod_name = os.path.splitext(script)[0]
            py_mod = imp.load_source(mod_name, full_path)
            if hasattr(py_mod, run_fun):
                # do we have parameters to pass?
                params = self.opts.executescriptparameter
                pdic = {}
                if params:
                    parts = params.split(',')
                    for p in parts:
                        try:
                            n, v = p.split('=')
                            pdic[n] = v
                        except:
                            pass
                # we pass ourself to the method, so we can access all attributes
                result = getattr(py_mod, run_fun)(self=self, **pdic)

        else:
            print(EXTRA_SCRIPT_NOT_EXISTING % full_path)

    def rebuild_site(self):
        # reload a site after the sitedescription has been updated
        try:
            from reimport import reimport, modified
        except ImportError:
            print(MODULE_MISSING % 'reimport')
        s = list(self.sites.keys())
        mlist = [m for m in modified() if m in s]
        if mlist:
            print(SITE_DESCRIPTION_RELOADED %
                  (' '.join(mlist), self.opts.command_line))
            sys.exit()

    def show_config(self):
        for k, v in list(self.base_info.items()):
            print(bcolors.WARNING + k + bcolors.ENDC, v)

 
    # the user can start using different paths
    # - without selecting anything:
    #   the create parser will be preselected
    # - without providing a full site name
    #   a site name will be asked for. if an invalid or partial name
    #   has bee provided, it will be used as default
    # - with a set of valid options
    def _complete_selection(self, parsername, options, results_only=False, prompt=''):
        cmpl = SimpleCompleter(parsername, options, prompt=prompt)
        _o = cmpl.input_loop()
        if _o in options:
            if results_only:
                return _o
            if isinstance(self.opts._o.__dict__[_o], bool):
                self.opts._o.__dict__[_o] = True
            elif _o in ['updateown', 'removeown']:
                l = self.install_own_modules(quiet='listownmodules')
                cmpl = SimpleCompleter(l, options)
                _r = cmpl.input_loop()
                if _o:
                    self.opts._o.__dict__[_o] = _r
            else:
                self.opts._o.__dict__[_o] = input('value for %s:' % _o)

    # -------------------------------------------------------------------
    # check_name
    # check if name is in any of the sites listed in list_sites
    # or needed at all
    # @opts otion namespace
    # @no_completion: flag whether a vlid name should be selected for a
    #                 selection list
    # -------------------------------------------------------------------
    def check_name(self, need_names_dic={}):
        """
        check if name is in any of the sites listed in list_sites
        or needed at all
        @opts otion namespace
        @no_completion: flag whether a valid name should be selected for a
                        selection list
        need_names_dic is a dictonary with two lists:
        need_names_dic = {
            'need_name' : [], # we need a name
            'name_valid': [], # given name must be valid  
        }
          
        """
        opts = self.opts
        name = self.site_name
        if name:
            # if name == 'all':
            #     site_names = list(self.sites.keys())
            # else:
            #     if name.endswith('/'):
            #         name = name[:-1]
            #     site_names = [name]

            opts.name = name
            # if not isinstance(opts, basestring):
            #     if opts.add_site:
            #         return name
            if SITES.get(name):
                self.site_names = [name]
                return name
            if opts.subparser_name == 'support':
                if opts.add_site or opts.add_site_local:
                    self.site_names = [name]
                    return name
            if opts.subparser_name == 'migrate':
                if opts.migrate_remove_apps:
                    self.site_names = [name]
                    return name
        # no name
        if not name:
            name = ''  # make sure it is a string
        
        # if no_completion:
        #     # probably called at startup
        #     if must_match:
        #         matches = [k for k in list(SITES.keys()) if k.startswith(name)]
        #         if not matches:
        #             print(
        #                 bcolors.WARNING + ('%s does not match any site name, discarded!' % name) + bcolors.ENDC)
        #             opts.name = ''
        #             return ''
        #         if name:
        #             self.site_names = [name]
        #             return name
        #         return ''
        #     else:
        #         self.site_names = [name]
        #         return name
        if not self.name_needed(need_names_dic=need_names_dic):
            return
        done = False
        cmpl = SimpleCompleter('', 
            options=list(SITES.keys()), default=name or '', prompt='please provide a valid site name:')
        while not done:
            _name = cmpl.input_loop()
            if _name is None:
                print(bcolors.FAIL)
                print('no name provided')
                print(bcolors.ENDC)               
                sys.exit()
                #done = True
                #self.site_names = []
                #return ''
            if opts.subparser_name == 'support':
                if _name and (opts.add_site or opts.add_site_local):
                    if SITES.get(_name):
                        print("the site %s allready exists in sites.py" % _name)
                    else:
                        done = True
            if _name and SITES.get(_name):
                done = True
            else:
                print(
                    '%s is not defined in sites.py. You can add it with option --add-site' % _name)
            if done:
                opts.name = _name
                self.site_names = [_name]
                return _name

        
    # -------------------------------------------------------------------
    # name_needed
    # check if name needed
    # or needed at all
    # @opts otion namespace
    # @option : option to check
    #          if not provided check what option user has selected
    # -------------------------------------------------------------------
    def name_needed(self, option=None, need_names_dic={}):
        """
        check if name needed
        or needed at all
        @opts otion namespace
        @optin : option to check
                 if not provided check what option user has selected
        """
        opts = self.opts
        need_name = need_names_dic.get('need_name', [])
        name_valid = need_names_dic.get('name_valid', [])
        collected_opts = [item[0]
                          for item in list(opts.__dict__.items()) if item[1]]
        if not [opt for opt in collected_opts if opt in need_name]:
            return
        if opts.name == 'db' and opts.docker_show:
            return False
        # do not accept names with forbidden chars in it
        if not option:
            # only return False if all options need no name
            result = False
            options = self.selections
            for opt in options:
                if self.name_needed(opt[0], need_names_dic):
                    result = True
            return result

        # do we need a name
        # if an option is provide, check this one
        if option:
            if option not in need_name:
                return False
            if option in name_valid:
                return True
        return True

    # ----------------------------------
    # delete_site_local 
    # remove all local project files
    # but leave the site description as it is
    # ----------------------------------
    def delete_site_local(self):
        """
        remove all local project files
        """
        site_name = self.site_name
        if not site_name:
            print(bcolors.FAIL)
            print('no name provided')
            print(bcolors.ENDC)
            return
        cur_path = os.getcwd()
        # remove project data
        project_path = self.default_values['project_path']
        os.chdir(project_path)
        # ----------------------------------------
        rpath ='%s/%s' % (project_path, site_name)
        if os.path.exists(rpath):
            print(bcolors.WARNING)
            print('removing %s' % rpath)
            shutil.rmtree(rpath, True)
        addons_path = self.data_path
        # ----------------------------------------
        os.chdir(addons_path)
        if os.path.exists(site_name):
            print('removing %s' % site_name)
            shutil.rmtree(site_name)
        # ----------------------------------------
        print('dropping database %s' % site_name)
        db_updater = DBUpdater()
        try:
            db_updater.close_db_connections_and_delete_db(site_name)
        except:
            pass # already deleted?
        print('removing virtualenv %s' % site_name)
        self.remove_virtual_env(site_name)
        print(bcolors.OKGREEN)
        print('tuti palletti')
        print(bcolors.ENDC)
        os.chdir(cur_path)

    def copy_admin_pw(self):
        """
        copy admin password from one site to the other
        """
        opts = self.opts
        site_name = self.site_name
        source = opts.copy_admin_pw

        # first check whether the source is valid
        if source not in self.sites:
            print(bcolors.FAIL + '*' * 80)
            print('%s is not a valid source' % source)
            print('*' * 80 + bcolors.ENDC)
            return
        # create two connections
        target_cursor, t_connection = self.get_cursor(return_connection=True)
        source_cursor, s_connection = self.get_cursor(
            db_name=source, return_connection=True)
        s_sql = "SELECT password_crypt from res_users where login = 'admin'"
        t_sql = "UPDATE res_users set password_crypt = '%s'  where login = 'admin'"
        source_cursor.execute(s_sql)
        pw = source_cursor.fetchone()[0]
        target_cursor.execute(t_sql % pw)
        t_connection.commit()
        t_connection.close()
        s_connection.close()
        print(bcolors.OKGREEN + '*' * 80)
        print('copied admin pw from %s to %s' % (source, site_name))
        print('*' * 80 + bcolors.ENDC)

    def set_admin_pw(self):
        """
        set admin password for a site
        """
        site_name = self.site_name
        pw = self.db_password
        # create a connection
        target_cursor, t_connection = self.get_cursor(return_connection=True)
        t_sql = "UPDATE res_users set password = '%s'  where login = 'admin'"
        target_cursor.execute(t_sql % pw)
        t_connection.commit()
        t_connection.close()
        print(bcolors.OKGREEN + '*' * 80)
        print('set admin pw for %s to %s' % (site_name, pw))
        print('*' * 80 + bcolors.ENDC)

    def create_folders(self, path_name='', quiet=None):
        """
        create all folders needed
        path_name = path to parent folder. create if it does not exist
        """
        errors = False
        if not self.site_name:
            # we need a site to construct a data folder
            return
        if quiet is None:
            quiet = not self.opts.verbose
        if not path_name:
            path_name = self.site_name
        p = os.path.normpath('%s/%s' % (self.data_path, path_name))
        foldernames = self.default_values['foldernames']
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)
        elif not os.path.isdir(self.data_path):
            print(bcolors.FAIL + '%s exists but is not a folder. Plese eiter remove it, or set'
                  'new folder using option -set erp_server_data_path:/NEWPATH' + bcolors.ENDC)
        for pn in [''] + foldernames:
            try:
                pp = '%s/%s' % (p, pn)
                os.mkdir(pp)
            except:
                errors = True
                if not quiet:
                    print(bcolors.FAIL + 'could not create %s' %
                          pp + bcolors.ENDC)
        if not quiet:
            if errors:
                print(bcolors.WARNING +
                      'not all directories could be created' + bcolors.ENDC)
            else:
                print('directories for %s created' % self.check_name(self.opts))
        
        # now add folder content
        # handle_file_copy_move(self, source, target, filedata):
        skeleton_path = self.default_values['skeleton']
        from skeleton.files_to_copy import FILES_TO_COPY_FOLDER as files_to_copy
        for foldername in foldernames:
            file_path = '%s/%s' % (p, foldername)
            if files_to_copy.get(foldername):
                self.handle_file_copy_move(
                    '%s/%s' % (skeleton_path, foldername), file_path, files_to_copy[foldername])

    # ----------------------------------
    # update_install_serversetting
    # set the web.base.url and the google captcha keys
    def update_install_serversetting(self):
        site = self.site
        site_params = site.get('site_settings', {})

        odoo = self.get_odoo()
        if odoo:
            # -----------------------------------
            # config
            # -----------------------------------

            # get the config blocks
            # we start with setting the site
            # proto = site_params.get('proto', 'http://')
            configs = site_params.get('configs', {})

            # -----------------------------------
            # languages
            # -----------------------------------
            # 'languages' : ['de_CH', 'fr_CH', 'en_US'],
            lang_dic = {}
            languages = configs.pop('languages', [])
            if languages:
                lang_dic = self.install_languages(languages)

            # next we set the key web.base.url.freeze
            # this prevenst that the key is reset when login in as addmin
            if 'ir.config_parameter' in configs:
                # old structure like afbs
                for key, data in list(configs.items()):
                    try:
                        model = odoo.env[key]
                        records = data.get('records', [])
                        for s_info, values in records:
                            # [('key', 'support_branding.company_name'),  {'value'  : 'redO2oo GmbH'}],
                            s = model.search([(s_info[0], '=', s_info[1])])
                            if s:
                                model.browse(s).write(values)
                    except:
                        pass
            else:
                """
                'configs' : {
                    # the following sample values assume, that the module support branding is installed
                    'support_branding' : {
                        'model' : 'ir.config_parameter',
                        # list of (search-key, value), {'field' : vaue, 'filed' : value ..}
                        'records' : [
                            # list of (search-key, value), {'field' : vaue, 'filed' : value ..}
                            [('key', 'support_branding.company_name'),  {'value'  : 'redO2oo KLG'}],
                            ....
                         ]
                    },


                    website:
                    --------
                    {u'cdn_activated': False,
                    u'cdn_filters': u'^/[^/]+/static/\n^/web/(css|js)/\n^/web/image\n^/web/content\n^/website/image/',
                    u'cdn_url': False,
                    u'default_lang_id': 22,
                    u'favicon': '',
                    u'google_analytics_key': False,
                    'google_maps_api_key': False,
                    u'language_ids': [[6, False, [1, 22]]],
                    'module_website_form_editor': 0,
                    'module_website_version': 0,
                    u'social_facebook': False,
                    u'social_github': False,
                    u'social_googleplus': False,
                    u'social_linkedin': False,
                    u'social_twitter': False,
                    u'social_youtube': False,
                    u'website_id': 1,
                    u'website_name': u'My Website'}

                },
                """
                def repl_default_lang_code(data):
                    if isinstance(data, dict):
                        code = data.pop('default_lang_code', None)
                        if code:
                            data['default_lang_id'] = self.install_languages([code])[
                                code]
                for setting, values in list(configs.items()):
                    m = values['model']
                    model = odoo.env[m]
                    records = values['records']
                    for s_info, values in records:
                        # [('key', 'support_branding.company_name'),  {'value'  : 'redO2oo GmbH'}],
                        s = model.search([(s_info[0], '=', s_info[1])])
                        if s:
                            repl_default_lang_code(values)
                            model.browse(s).write(values)

            # -----------------------------------
            # companies
            # -----------------------------------
            """
            # data to be set on the remote server with
            # --set-site-data
            companies: {
                'main_company' : {
                    'company_data' : {
                        # use any number of fields you want to set on the main company
                        # this is normaly done after after all modules are installed
                        # so you can also use fields like firstname/lastname that are
                        # only available after the addons have been installed
                        'name' : 'Energy & Power Sarl',
                        'street' : 'Rue Marconi 19',
                        'zip'    : '1920',
                        'city'   : 'Martigny VS',
                        'phone'  : '+41 (0) 78 678 39 42',
                        'email' : 'info@eplusp.ch',
                        'url' : 'https://www.eplusp.ch',
                    },
                    'users' : {
                        # add users you want to be created
                        # for each user provide either an string with the email,
                        # or a dictionary with more data. In any case, the email must
                        # be provided
                        # the same rules as for the company apply
                        'bruno.cosandey@eplusp.ch' : {
                            'firstname' : 'Bruno',
                            'lastname' : 'Cosandey',
                            'street' : 'Rue Marconi 19',
                            'zip'    : '1920',
                            'city'   : 'Martigny VS',
                            'phone'  : '+41 (0) 78 678 39 42',
                            'email' : 'bruno.cosandey@eplusp.ch',
                        }
                    },
                },  # main_company
            },  # companies

            """
            companies = site_params.get('companies', {})
            main_company = companies.get('main_company')
            if main_company:
                # the main company always has id 1
                companies_o = odoo.env['res.company']
                mc = companies_o.browse([1])
                # do we have data for the main company
                mc_data = main_company.get('company_data')
                if mc_data:
                    mc.write(mc_data)
                # create related users
                users = main_company.get('users')
                if users:
                    users_o = odoo.env['res.users']
                    for login, user_data in list(users.items()):
                        firstname = user_data.get('firstname')
                        lastname = user_data.get('lastname')
                        language = user_data.get('name')
                        if language:
                            self.install_languages([language])
                        if firstname or lastname:
                            user_data['name'] = ('%s %s' %
                                                 (lastname, firstname)).strip()
                        else:
                            user_data['name'] = login
                        if not user_data.get('email'):
                            user_data['email'] = login
                        if not user_data.get('login'):
                            user_data['login'] = login
                        if not user_data.get('tz'):
                            user_data['tz'] = 'Europe/Zurich'
                        # check if user exists
                        user = users_o.search([('login', '=', login)])
                        if user:
                            users_o.browse(user).write(user_data)
                        else:
                            #user = odoo.env['res.users'].sudo().with_context().create(user_data)
                            users_o.create(user_data)
        else:
            print(ERP_NOT_RUNNING % self.site_name, {})

    # ----------------------------------
    # set_local_data
    # set local settings from the site description
    # use remote_settings is active when we change a dokerized odoo
    def set_local_data(self, use_remote_setting=False):
        odoo = self.get_odoo()
        if not odoo:
            print(bcolors.FAIL, ERP_NOT_RUNNING %
                  self.site_name, bcolors.ENDC)
            return
        # run set server data
        # this sets
        self.update_install_serversetting()
        site = self.site
        site_settings = site.get('site_settings', {})
        local_settings = site_settings.get('local_settings', {})
        if use_remote_setting:
            proto = site_settings.get('proto', 'https://')
            base_url = '%s%s' % (proto, site.get('apache', {}).get(
                'vservername', local_settings.get('base_url', '')))
        else:
            base_url = local_settings.get('base_url', '')
        admin_mail = local_settings.get('admin_mail', '')
        if admin_mail.find('%(local_user_mail)s') > -1:
            admin_mail = self.base_info.get('local_user_mail', 'robert@redO2oo.ch')
        # if admin_mail:
            #users = odoo.env['res.users']
            #u = users.search([('id', '=', 1)])
            #admin = users.browse(u)
            #admin.write({'email' : admin_mail})
            #print(bcolors.OKGREEN, 'setting admin email to:%s' % admin_mail, bcolors.ENDC)

        # do we have to install / uninstall anything
        addons = local_settings.get('addons', {})
        to_install = addons.get('install', [])
        # there are modules, like mailblocker, we want to have installed only locally
        if to_install:
            self.install_own_modules(info_dic={'local_install': to_install})
        # set the site configuration, that allways needs to be set
        # set the base url
        if odoo:
            config = odoo.env['ir.config_parameter']
        if base_url:
            base_url_obj = config.browse(
                config.search([('key', '=', 'web.base.url')]))
            base_url_obj.write({'value': base_url})
            print(bcolors.OKGREEN, 'setting base_url to:%s' %
                  base_url, bcolors.ENDC)
        # set other config stuff
        # if there is additional site configuration, set them now
        more_params = local_settings.get('site_settings')
        if more_params:
            config_params = more_params.get('configs', {}).get(
                'ir.config_parameter', {}).get('records', [])
            if self.running_remote():
                # we to replace values that should be different when running remotely
                # this should be done in a mor systematic way.when I use massmailing, a click to the send button
                remote_info = self.site.get('remote_server', {})
                if remote_info.get('redirect_emil_to'):
                    self._default_values['local_user_mail'] = remote_info.get(
                        'redirect_emil_to')
            for c_param in config_params:
                # list of (search-key-name, value), {'field' : value, 'field' : value ..}
                # [('key', 'red_override_email_recipients.override_to'),
                    # {'value'  : '%(local_user_mail)s'}],
                c_key = c_param[0][0]
                c_k_val = c_param[0][1]
                vals = c_param[1]
                c_obj = config.browse(config.search([(c_key, '=', c_k_val)]))
                if c_obj:
                    for k, v in list(vals.items()):
                        if isinstance(v, str):
                            vals[k] = v % self.default_values
                    c_obj.write(vals)
                print(bcolors.OKGREEN, 'setting %s to:%s' %
                      (c_k_val, vals), bcolors.ENDC)

    # ----------------------------------
    # set null server
    def set_null_mail_server(self):
        """
        replace outgoing mail server with a local null smtp server
        that intercepts all outgoing mail
        """
        data = {'active': True,
                'name': 'localost',
                'sequence': 10,
                'smtp_debug': False,
                'smtp_encryption': 'none',
                'smtp_host': 'localhost',
                'smtp_pass': '',
                'smtp_port': 2525,
                'smtp_user': ''}
        data_in = {
            'active': True,
            'attach': True,
            'is_ssl': True,
            'name': 'mailhandler@o2oo.ch',
            'object_id': False,
            'original': False,
            'password': '',
            'port': 993,
            'priority': 5,
            'server': 'mail.redcor.ch',
            'state': 'draft',
            'type': 'imap',
            'user': 'mailhandler@o2oo.ch.ch'}

        s_data = {
            'erp_settings' : {
                'mail_outgoing' : data,
                #'mail_incomming' : data_in,
            },
        }
        return self.set_erp_settings(s_data=s_data)


    # ----------------------------------
    # set_erp_settings
    # set odoo settings from the site description
    # like the email settings and such
    # we try to find out what our ip is and the get the data
    # according to that ip.
    # if our ip is not in the servers list, we take 127.0.0.1
    def set_erp_settings(self, use_docker=False, local=True, s_data={}):
        import socket
        import fcntl
        import struct
        SITES_PW = {}

        def get_ip_address(ifname):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                return socket.inet_ntoa(fcntl.ioctl(
                    s.fileno(),
                    0x8915,  # SIOCGIFADDR
                    struct.pack('256s', ifname[:15])
                )[20:24])
            except:
                # we have no etho
                # https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ipl = s.getsockname()
                if ipl:
                    return ipl[0]
        odoo = self.get_odoo()
        if not odoo:
            print(ERP_NOT_RUNNING % self.site_name)
            return
        site = self.site
        remote_servers = site.get('remote_servers', {})
        # if the site runs on a virtual server behind a NAT we do
        # not know its real address
        if self.opts.use_ip:
            my_ip = self.opts.use_ip
        elif use_docker and self.opts.use_ip_docker:
            my_ip = self.opts.use_ip_docker
        elif local:
            my_ip = '127.0.0.1'
        else:
            my_ip = get_ip_address('eth0')
        # if we do not have s_data passed to us
        do_incoming = True
        if not s_data:
            s_data = remote_servers.get(my_ip)
        else:
            if not s_data.get('erp_settings', {}).get('mail_incomming'):
                do_incoming = False
        # use proxy on development server
        proxy = ''
        if not s_data:
            s_data = remote_servers.get(remote_servers.get('proxy'))
            proxy = remote_servers.get('proxy')
            print(bcolors.FAIL + 'no erp_settings for (local) id:%s found' %
                  my_ip + bcolors.ENDC)
            print(bcolors.WARNING + 'using proxy (%s) to calculate site settings' %
                  my_ip + bcolors.ENDC)
        if not s_data:
            print(bcolors.WARNING + 'no erp_settings for id:%s found' %
                  my_ip + bcolors.ENDC)
            return
        # get passwords
        try:
            from sites_pw import SITES_PW
            email_pws = SITES_PW.get(self.site_name, {}).get(
                'email', SITES_PW.get(self.site_name, {}).get('email_settings', {}))
        except ImportError:
            email_pws = {}
            pass

        print(bcolors.OKGREEN, '*' * 80)
        if do_incoming:
            # write the incomming email server
            i_server = odoo.env['fetchmail.server']
            # get the first server
            print('incomming email')
            i_ids = i_server.search([])
            i_id = 0
            i_data = s_data.get('erp_settings', {}).get('mail_incomming')
            if not i_data and s_data.get('odoo_settings', {}).get('mail_incomming'): # bb
                i_data = s_data.get('odoo_settings', {}).get('mail_incomming')
            # do we have a password
            if not local:
                i_data['password'] = email_pws.get('email_pw_incomming', '')
            if i_ids:
                i_id = i_ids[0]
            if i_id:
                incomming = i_server.browse([i_id])
                incomming.write(i_data)
            else:
                incomming = i_server.create(i_data)
            print(i_data)
        print('-' * 80)
        print('outgoing email')
        # now do the same for the outgoing server
        o_data = s_data.get('erp_settings', {}).get('mail_outgoing')
        if not o_data and s_data.get('odoo_settings', {}).get('mail_outgoing'):
            o_data = s_data.get('odoo_settings', {}).get('mail_outgoing')
        if not local:
            o_data['smtp_pass'] = email_pws.get('email_pw_outgoing', '')
        o_server = odoo.env['ir.mail_server']
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
        print('*' * 80, bcolors.ENDC)

    # ----------------------------------
    # run_tests
    # run tests listed on the command line
    # run all, if list of tests is "all"
    def run_tests(self):
        """
        tests are run, when we start odoo with the --test-enable parameter
        We therfore start odoo
        bin/start_openerp --test-enable -u redmail2bill --stop-after-init --test-file /home/robert/odoo_projects_data/redo2oo/addons/redmail2bill/tests/test_redmail2bill_generate.py
        """
        pass

    # ----------------------------------
    # install_own_modules
    # or install erp_moduls
    def install_own_modules(self, quiet=False, info_dic={}):
        """
        Install either the odoo apps listed under the key erp_addons
        or the "own" addons listed under the key addons in the site description
        quiet can get the value "listownmodules" to only list the modules
        or listownapps to list the erp_apps from the site description
        """
        opts = self.opts
        is_create = opts.subparser_name == 'create'
        is_docker = not is_create
        default_values = self.default_values

        site = self.site
        # addons decalared in addons are the ones not available from odoo directly
        site_addons = self.site_addons
        # addons declared in the erp_addons stanza are the ones we can get from odoo
        erp_addons = self.erp_addons
        local_install = info_dic.get('local_install', [])
        req = []
        module_obj = None
        if not (is_create and opts.install_erp_modules) and not (is_docker and opts.dinstall_erp_modules):
            # opts.installown or opts.updateown or opts.removeown or opts.listownmodules or quiet: # what else ??
            # collect the names of the modules declared in the addons stanza
            # idealy their names are set, if not, try to find them out
            for a in (site_addons or []):
                names = find_addon_names(a)
                for name in names:
                    if local_install and name not in local_install:
                        continue
                    if name:
                        if (is_create and opts.listownmodules):
                            req.append((name, a.get('url')))
                        else:
                            req.append(name)
                    else:
                        if a and not quiet:
                            print('could not detect name for %s' %
                                  a.get('url', ''))

        # if we only want the list to install, no need to be wordy
        if (is_create and opts.listownmodules) or quiet == 'listownmodules':
            if quiet:
                return req
            sn = self.site_name
            print('\nthe following modules will be installed for %s:' % sn)
            print('---------------------------------------------------')
            for n, url in req:
                temp_target = os.path.normpath(
                    '%s/%s/%s/%s_addons/%s' % (self.base_info['project_path'], sn, sn, sn, n))
                if os.path.exists(temp_target):
                    print(bcolors.OKBLUE, '    %s %s (devel mode)' %
                          (n, temp_target), bcolors.ENDC)
                else:
                    print('    ', n, url)
            print('---------------------------------------------------')
            return

        # do we want to install odoo modules
        if (is_docker and opts.dinstall_erp_modules) or (is_create and opts.install_erp_modules):
            erp_apps_info, erp_modules_info = self.get_erp_modules()

            erp_apps = list(erp_apps_info.keys())
            erp_apps_names = list(erp_apps_info.values())
            erp_apps_map = {}
            for k, v in list(erp_apps_info.items()):
                erp_apps_map[v] = k

            erp_modules = list(erp_modules_info.keys())
            erp_module_names = list(erp_modules_info.values())
            erp_module_map = {}
            for k, v in list(erp_modules_info.items()):
                erp_module_map[v] = k
            for o in (erp_addons or []):
                o = str(o)
                if o in erp_apps_names:
                    name = erp_module_map[o]
                    if name not in req:
                        req.append(name)
                elif o in erp_apps:
                    if o not in req:
                        req.append(o)
                elif o in erp_module_names:
                    name = erp_module_map[o]
                    if name not in req:
                        req.append(name)
                elif o in erp_modules:
                    if o not in req:
                        req.append(o)
                else:
                    # we will never come here ???
                    if o not in req:
                        req.append(o)

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

            cursor = self.get_cursor()
            skiplist = self.site.get('skip', {}).get('addons', [])[
                :]  # we do not want to change the original
            skip_upd_list = self.site.get('skip', {}).get('updates', [])
            skip2 = opts.__dict__.get('skipown', [])
            if skip2:
                skip2 = skip2.split(',')
            # remove elements in the local_install from the skip lists
            skiplist = [e for e in skiplist if e not in local_install]
            skip2 = [e for e in skip2 if e not in local_install]

            for a in (skiplist) + skip2:
                if a in req:
                    req.pop(req.index(a))
            self.collect_info(cursor, req, installed,
                              uninstalled, to_upgrade, skiplist, req[:])
            if req:
                print('*' * 80)
                print('the following modules where not found:', req)
                print('you probably have to download them')
                print('*' * 80)
            if uninstalled:
                print('the following modules need to be installed:',
                      [u[1] for u in uninstalled])
                i_list = [il[0] for il in uninstalled]
                n_list = [il[1] for il in uninstalled]
                print('*' * 80)
                print(bcolors.OKGREEN + 'installing: ' +
                      bcolors.ENDC + ','.join(n_list))
                load_demo = False
                modules = module_obj.browse(i_list)
                if load_demo:
                    for m in modules:
                        m.demo = True
                if opts.single_step:
                    for module in modules:
                        print('installing:%s%s%s' % (bcolors.OKGREEN, module.name, bcolors.ENDC))
                        module.button_immediate_install()
                else:
                    modules.button_immediate_install()
                print(bcolors.OKGREEN + 'finished installing: ' +
                      bcolors.ENDC + ','.join(n_list))
                print('*' * 80)
            if installed and (
                (is_create and (opts.updateown or opts.removeown)) 
                    or (is_docker and (opts.dupdateown or opts.dremoveown))):
                if (is_create and opts.updateown) or (is_docker and opts.dupdateown):
                    i_list = [il[0]
                              for il in installed if (il[1] not in skip_upd_list)]
                    n_list = [il[1]
                              for il in installed if (il[1] not in skip_upd_list)]
                    print('*' * 80)
                    print(bcolors.OKGREEN + 'upgrading: ' +
                          bcolors.ENDC + ','.join(n_list))
                    print('-' * 80)
                    modules = module_obj.browse(i_list)
                    load_demo = False
                    if load_demo:
                        for m in modules:
                            m.demo = True
                    if opts.single_step:
                        for module in modules:
                            # todo do not install every single feature that are in the same module
                            # but do it module wise
                            print('upgrading: %s' % module.name)
                            module.button_immediate_upgrade()
                    else:
                        modules.button_immediate_upgrade()
                    print(bcolors.OKGREEN + 'finished upgrading: ' +
                          bcolors.ENDC + ','.join(n_list))
                    print('*' * 80)
                else:  # uninstall ..
                    print('the following modules will be uninstalled:',
                          [u[1] for u in installed])
                    for i, n in installed:
                        print('*' * 80)
                        print('unistalling: ' + n)
                        module_obj.browse(i).button_immediate_uninstall()
                        print('finished unistalling: ' + n)
                        print('*' * 80)

    # # ----------------------------------
    # # set_erp_settings
    # # set odoo settings from the site description
    # # like the email settings and such
    # # we try to find out what our ip is and the get the data
    # # according to that ip.
    # # if our ip is not in the servers list, we take 127.0.0.1
    # def set_erp_settings(self, use_docker=False, local=True):
    #     import socket
    #     import fcntl
    #     import struct
    #     SITES_PW = {}

    #     def get_ip_address(ifname):
    #         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #         try:
    #             return socket.inet_ntoa(fcntl.ioctl(
    #                 s.fileno(),
    #                 0x8915,  # SIOCGIFADDR
    #                 struct.pack('256s', ifname[:15])
    #             )[20:24])
    #         except:
    #             # we have no etho
    #             # https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
    #             s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #             s.connect(("8.8.8.8", 80))
    #             ipl = s.getsockname()
    #             if ipl:
    #                 return ipl[0]
    #     odoo = self.get_odoo()
    #     if not odoo:
    #         print(ODOO_NOT_RUNNING % self.site_name)
    #         return
    #     site = self.site
    #     remote_servers = site.get('remote_servers', {})
    #     # if the site runs on a virtual server behind a NAT we do
    #     # not know its real address
    #     if self.opts.use_ip:
    #         my_ip = self.opts.use_ip
    #     elif use_docker and self.opts.use_ip_docker:
    #         my_ip = self.opts.use_ip_docker
    #     elif local:
    #         my_ip = '127.0.0.1'
    #     else:
    #         my_ip = get_ip_address('eth0')
    #     # check whether the address in in
    #     s_data = remote_servers.get(my_ip)
    #     # use proxy on development server
    #     proxy = ''
    #     if not s_data:
    #         s_data = remote_servers.get(remote_servers.get('proxy'))
    #         proxy = remote_servers.get('proxy')
    #         print(bcolors.FAIL + 'no odoo_settings for (local) id:%s found' %
    #               my_ip + bcolors.ENDC)
    #         print(bcolors.WARNING + 'using proxy (%s) to calculate site settings' %
    #               my_ip + bcolors.ENDC)
    #     if not s_data:
    #         print(bcolors.WARNING + 'no odoo_settings for id:%s found' %
    #               my_ip + bcolors.ENDC)
    #         return
    #     # get passwords
    #     try:
    #         from sites_pw import SITES_PW
    #         email_pws = SITES_PW.get(self.site_name, {}).get(
    #             'email', SITES_PW.get(self.site_name, {}).get('email_settings', {}))
    #     except ImportError:
    #         email_pws = {}
    #         pass

    #     # write the incomming email server
    #     i_server = odoo.env['fetchmail.server']
    #     # get the first server
    #     print(bcolors.OKGREEN, '*' * 80)
    #     print('incomming email')
    #     i_ids = i_server.search([])
    #     i_id = 0
    #     i_data = s_data.get('odoo_settings', {}).get('mail_incomming')
    #     # do we have a password
    #     if not local:
    #         i_data['password'] = email_pws.get('email_pw_incomming', '')
    #     if i_ids:
    #         i_id = i_ids[0]
    #     if i_id:
    #         incomming = i_server.browse([i_id])
    #         incomming.write(i_data)
    #     else:
    #         incomming = i_server.create(i_data)
    #     print(i_data)
    #     print('-' * 80)
    #     print('outgoing email')
    #     # now do the same for the outgoing server
    #     o_data = s_data.get('odoo_settings', {}).get('mail_outgoing')
    #     if not local:
    #         o_data['smtp_pass'] = email_pws.get('email_pw_outgoing', '')
    #     o_server = odoo.env['ir.mail_server']
    #     # get the first server
    #     o_ids = o_server.search([])
    #     o_id = 0
    #     if o_ids:
    #         o_id = o_ids[0]
    #     if o_id:
    #         outgoing = o_server.browse([o_id])
    #         outgoing.write(o_data)
    #     else:
    #         o_server.create(o_data)
    #     print(o_data)
    #     print('*' * 80, bcolors.ENDC)

    # ----------------------------------
    # remove_apps
    # remove erp_moduls
    def remove_apps(self):
        opts = self.opts
        to_remove = opts.removeapps.split(',')
        apps = self.listapps(return_apps=True)
        module_obj = self.get_module_obj()
        app_dic = {key: value for (value, key) in apps}
        if module_obj:
            print(bcolors.green)
            print('*' * 80)
            print('The following app(s) will be uninstalled')
            for app_name in to_remove:
                if app_dic.get(app_name):
                    print(app_name)                    
                    module_obj.browse(app_dic.get(
                        app_name)).button_immediate_uninstall()
            print(bcolors.ENDC)
        else:
            print(bcolors.WARNING)
            print('*' * 80)
            print('odoo seems not to be running')
            print(bcolors.ENDC)


    # listapps
    # --------
    # list what apps are installed in a running odoo site
    # mark the ones listed in the site description
    def listapps(self, return_apps = False):
        installed = []
        uninstalled = []
        to_upgrade = []
        req = []
        apps = []
        cursor = self.get_cursor()
        site = self.site
        # addons decalared in addons are the ones not available from odoo directly
        site_addons = self.site_addons
        # addons declared in the erp_addons stanza are the ones we can get from odoo
        erp_addons = self.erp_addons

        self.collect_info(cursor, req, installed, uninstalled, to_upgrade, skip_list=[], apps=apps)
        if return_apps:
            return apps
        app_names = [a[1] for a in apps]
        for name in erp_addons:
            print(name, name in app_names and '+' or '')

    # ----------------------------------
    #  collects info on what modules are installed
    # or need to be installed
    # @req : list of required modules. If this is an empty list
    #         use any module
    # @uninstalled  : collect unistalled modules into this list
    # @to_upgrade   :collect modules that expect upgrade into this list
    def collect_info(self, cursor, req, installed, uninstalled, to_upgrade, skip_list, all_list=[], apps=[]):
        opts = self.opts
        s = 'select * from ir_module_module'
        cursor.execute(s)
        rows = cursor.fetchall()
        all = not req
        updlist = []
        if opts.subparser_name == 'create':
            if opts.updateown:
                updlist = opts.updateown.split(',')
            elif opts.removeown:
                updlist = opts.removeown.split(',')
            elif opts.removeapps:
                updlist = opts.removeapps
        if opts.subparser_name == 'docker':
            if opts.dupdateown:
                updlist = opts.dupdateown.split(',')
            elif opts.dremoveown:
                updlist = opts.dremoveown.split(',')
            elif opts.dremoveapps:
                updlist = opts.dremoveapps
        if 'all' in updlist:
            updlist = all_list
        if 'dev' in updlist or 'develop' in updlist:
            dev_list = self.site.get('develop')
            if dev_list:
                dev_list = dev_list.get('addons')
            if not dev_list:
                print(OWN_ADDONS_NO_DEVELOP % self.site_name)
                return
            updlist = dev_list
        for r in rows:
            n = r.get('name')
            s = r.get('state')
            i = r.get('id')
            if n in req or all:
                if n in req:
                    req.pop(req.index(n))
                if s == 'installed':
                    if r.get('application'):
                        apps.append([i, n])
                    if all or updlist == 'all' or n in updlist:
                        installed.append((i, n))
                    continue
                elif s in ['uninstalled', 'to install']:
                    uninstalled.append((i, n))
                elif s == 'to upgrade':
                    to_upgrade.append(n)
                else:
                    if not s == 'uninstallable':
                        print(n, s, i)
        # now clean all list from any modules we want to skip
        # x.pop(x.index(2))
        if skip_list:
            if uninstalled:
                for n in skip_list:
                    for u in uninstalled:
                        if u[1] == n:
                            uninstalled.pop(uninstalled.index(u))
            if to_upgrade:
                for n in skip_list:
                    try:
                        to_upgrade.pop(to_upgrade.index(n))
                    except:  # was not there ..
                        pass

    # =============================================================
    # handle docker stuff
    # =============================================================
 
    def run_commands(self, cmd_lines, user='', pw='', shell=True):
        """
        """
        opts = self.opts
        if not pw:
            pw = self.db_password  # B_PASSWORD
        if not user:
            user = self.db_user  # B_USER
        counter = 0
        is_builtin = False
        for cmd_line in cmd_lines:
            counter += 1
            if isinstance(cmd_line, dict):
                is_builtin = cmd_line['is_builtin']
                cmd_line = cmd_line['cmd_line']
            if opts.verbose:
                print('counter:', counter)
            if not cmd_line:
                continue
            if opts.verbose:
                print('-' * 80)
                print(cmd_line)
            if is_builtin:
                p = subprocess.Popen(
                    cmd_line,
                    stdout=PIPE)
            else:
                p = subprocess.Popen(
                    cmd_line,
                    stdout=PIPE,
                    stderr=PIPE,
                    env=dict(os.environ, PGPASSWORD=pw, PATH='/usr/bin:/bin'),
                    shell=shell)
            if opts.verbose:
                output, errors = p.communicate()
                if output:
                    print(output.decode('utf8'))              
            else:
                output, errors = p.communicate()
            if p.returncode:
                print(bcolors.FAIL)
                print('*' * 80)
                print(cmd_line)
                print('resulted in an error or warning')
                print(errors.decode('utf8'))
                print('*' * 80)
                print(bcolors.ENDC)          

    def run_commands_run(self, cmd_lines, user='', pw='', shell=True):
        """
        similar like run_commands, but use run instead of popen
        """
        opts = self.opts
        if not pw:
            pw = self.db_password  # B_PASSWORD
        if not user:
            user = self.db_user  # B_USER
        counter = 0
        is_builtin = False
        for cmd_line in cmd_lines:
            counter += 1
            if opts.verbose:
                print('counter:', counter)
            if not cmd_line:
                continue
            if opts.verbose:
                print('-' * 80)
                print(cmd_line)
            p = subprocess.run(cmd_line)
                #cmd_line,
                #stdout=PIPE,
                #stderr=PIPE,
                #shell=shell)
            output = p.stdout
            errors = p.stderr
            if opts.verbose:
                if output:
                    print(output.decode('utf8'))
            if p.returncode:
                print(bcolors.FAIL)
                print('*' * 80)
                print(cmd_line)
                print('resulted in an error or warning')
                if errors:
                    print(errors.decode('utf8'))
                print('*' * 80)
                print(bcolors.ENDC)

    def add_aliases_to_git_exclude(self):
        """
        exclude site folders from beeing handled by git
        less .git/info/exclude 
        """
        names = list(SITES.keys())
        names.sort()
        marker_start = AMARKER % 'start'
        marker_end = AMARKER % 'end'
        exclude_f_path = '%s/.git/info/exclude' % self.sites_home
        if not os.path.exists(exclude_f_path):
            # we are propably in a test
            return
        with open(exclude_f_path, 'r') as f:
            data = f.read()
        data = data.split('\n')
        alias_str = ''
        # loop over data and add lines to the result until we see the marker
        # then we loop untill we get the endmarker or the end of the file
        start_found = False
        for line in data:
            if not start_found:
                if line.strip() == marker_start:
                    start_found = True
                    continue
                alias_str += '%s\n' % line
            else:
                if line.strip() == marker_end:
                    end_found = True
                    start_found = False
        # we no have all lines without the constucted alias in alias_str
        # we add a new block of lines to it
        alias_str += ABLOCK % {
            'aliasmarker_start': marker_start,
            'aliasmarker_end': marker_end,
            'alias_list': '\n'.join(names),
            'alias_header': '',
        }
        with open(exclude_f_path, 'w') as f:
            f.write(alias_str)

    def add_aliases(self):
        """
        construct aliases to access the workbench directories easily
        """
        if not self.site_name:
            # we need a sitename to do anything sensible
            return
        pp = self.base_info['erp_server_data_path']
        oop = self.sites_home
        marker_start = AMARKER % 'start'
        marker_end = AMARKER % 'end'
        # where do we want to add our aliases?
        alias_script = "bash_aliases"
        if sys.platform == 'darwin':
            alias_script = "bash_profile"
        else:
            try:
                dist = open("/etc/lsb-release").readline()
                dist = dist.split("=")
                print(dist[1])
                if dist[1].strip("\n") == "LinuxMint":
                    alias_script = "bashrc"
                elif dist[1].strip("\n") == "Ubuntu":
                    alias_script = "bash_aliases"
            except:
                print('could not determine linux distribution')
                pass
        home = os.path.expanduser("~")
        alias_path = '%s/.%s' % (home, alias_script)
        try:
            data = open(alias_path, 'r').read()
        except:
            data = ''
        data = data.split('\n')
        alias_str = ''
        # loop over data and add lines to the result untill we see the marker
        # then we loop untill we get the endmarker or the end of the file
        start_found = False
        end_found = False
        for line in data:
            if not start_found:
                if line.strip() == marker_start:
                    start_found = True
                    continue
                alias_str += '%s\n' % line
            else:
                if line.strip() == marker_end:
                    end_found = True
                    start_found = False
        # we no have all lines without the constucted alias in alias_str
        # we add a new block of aliases to it
        alias_str += ABLOCK % {
            'aliasmarker_start': marker_start,
            'aliasmarker_end': marker_end,
            'alias_list': self.create_aliases(),
            'alias_header': ALIAS_HEADER % {'pp': pp},
            'ppath': pp,
        }
        with open(alias_path, 'w') as f:
            f.write(alias_str)

        # now write stings to git excluse file
        self.add_aliases_to_git_exclude()

    def _get_shortest(self, name, names, min_len=2):
        """get stortes string uniqe beginnin name
        
        Arguments:
            name {strin} -- name we want to find shortes elemen
            names {list of strings} -- strings we test against
            min_len {int} -- minimum length of string returned
        """
        for n in names:
            if n == name:
                continue
            while min_len < len(name):
                if not n.startswith(name[:min_len]):
                    break
                min_len += 1
        return name[:min_len]


    def create_siteslist_aliases(self):
        """create one alias per siteslist, to easily cd into it
        """
        sitelist_names = []
        sites_list_path = self.base_info.get('sitesinfo_path')
        siteinfos = self.siteinfos
        alias_line = ALIAS_LINE
        sitelist_names = list(siteinfos.keys())
        result = ''
        for sitelist_name, sites_list_url in list(siteinfos.items()):
            running_path = os.path.normpath('%s/%s' % (sites_list_path, sitelist_name))
            s = self._get_shortest(sitelist_name, sitelist_names)
            result += ALIAS_LINE % { 'sname' : "wwli%s" % s, 'path' : running_path}
            result += ALIAS_LINE_PULL % { 'sname' : "wwli%spull" % s, 'path' : running_path}
        return result

    def create_aliases(self):
        """
        """
        pp = self.base_info['project_path']
        dp = self.data_path
        oop = self.sites_home
        # shortnamesconstruct
        alias_names = [n for n in list(SITES.keys()) if len(n) <= ALIAS_LENGTH]
        names = list(SITES.keys())
        names.sort()
        long_names = alias_names
        for n in names:
            if n in alias_names:
                continue  # the  short ones
            try_length = ALIAS_LENGTH
            while n[:try_length] in alias_names:
                try_length += 1
                # we will for sure find a key ..
            alias_names.append(n[:try_length])
            long_names.append(n)
        result = ALIAS_LINE % {'sname': 'pro', 'path': pp}
        result += ALIAS_LINE % {'sname': 'wwb', 'path': oop}
        for i in range(len(alias_names)):
            if os.path.exists('%s/%s' % (pp, long_names[i])):
                result += ALIAS % {
                    'sname': alias_names[i],
                    'lname': long_names[i],
                    'ppath': pp,
                    'dpath': dp,
                }
        # wwb cd to erp_workbench
        result += WWB % self.sites_home
        result += WWLI % self.base_info['sitesinfo_path']
        result += WWB % self.base_info['erp_server_data_path']
        result += DOCKER_CLEAN
        result += DOC_ET_ALL % {'user_home': os.path.expanduser("~/")}
        result += ALIASC
        result += ALIASOO
        result += VIRTENV_D
        # add aliases for the siteslists
        result += self.create_siteslist_aliases()
        return result

    def do_updates(self):
        """
        we want to git pull erp_workbench and sites_list
        """
        # first we change to erp_workbench main folder
        adir = os.getcwd()
        for t in self.sites_home, self.sitesinfo_path:
            os.chdir(t)
            # pull erp_workbench
            cmd_line = ['git', 'pull']
            p = subprocess.Popen(cmd_line, stdout=PIPE, stderr=PIPE)
            if self.opts.verbose:
                print(t, ':',)
                result = p.communicate()
                print(result[0])
                if result[1]:
                    print(result[1])
            else:
                p.communicate()
        os.chdir(adir)

    def do_rebuild(self):
        # we want to call bin/dosetup.py -f;bin/buildout in the buildout directory
        adir = os.getcwd()
        pp = self.base_info['project_path']
        f = '%s/%s/%s' % (pp, self.site_name, self.site_name)
        if os.path.exists(f):
            os.chdir(f)
            cmd_lines = (['bin/dosetup.py', '-f'], ['bin/buildout'])
            for cmd_line in cmd_lines:
                print(bcolors.WARNING)
                print('processing:', f, cmd_line)
                print(bcolors.ENDC)
                p = subprocess.Popen(cmd_line, stdout=PIPE, stderr=PIPE)
                result = p.communicate()
                print(result[0])
                if result[1]:
                    print(result[1])

    def handle_file_copy_move(self, source, target, filedata):
        opts = self.opts
        # if overwrite is set, existing files are overwritten
        # if make_links is set links to dosetup.py and update_localdb.py are created, otherwise the files are copied
        try:
            overwrite = opts.overwrite
            make_links = not opts.update_nolinks
        except AttributeError as e:
            overwrite = True
            make_links = False
        o_overwrite = overwrite
        for fname, tp in list(filedata.items()):
            # O = File, always overwrite
            # F = File
            # X = File set executable bit, allways overwrite
            # L = Linkpath)

            # D = Folder
            # T = Touch
            # R = copy and rename
            # U = Update, these files can have updatable content in the form of %(XXX)s
            # '$FILE$' link to the source
            overwrite = o_overwrite
            try:
                cmd = ''
                spath = fname
                if source:
                    spath = '%s/%s' % (source, fname)
                tpath = '%s/%s' % (target, fname)
                if isinstance(tp, tuple):
                    tp, cmd = tp
                    if cmd:
                        if cmd == '$FILE$':
                            if make_links:
                                if os.path.exists(tpath):
                                    os.remove(tpath)
                                os.symlink(spath, tpath)
                                continue
                            else:
                                # copy like normal file
                                # allways overwrite
                                if os.path.exists(tpath):
                                    os.remove(tpath)
                                shutil.copyfile(spath, tpath)
                    if tp == 'L':
                        # does the target exist and do we want to overwrite it?
                        if os.path.exists(tpath) and not os.path.islink(tpath) and make_links:
                            # we want to make links, but target is not a link
                            # so we remove it
                            os.remove(tpath)
                        elif os.path.exists(tpath) and overwrite:
                            # target exist, but we want to renew it
                            os.remove(tpath)
                        # cmd is the link
                        # change to the target
                        if not os.path.exists(tpath):
                            # link was not copied yet or has been remove due to the overwrite flag
                            adir = os.getcwd()
                            os.chdir(target)
                            try:
                                os.symlink(cmd, tpath)
                            except OSError as e:
                                print('*' * 80)
                                print(str(e))
                                print('cmd:', cmd)
                                print('tpath:', tpath)
                                print('*' * 80)
                            os.chdir(adir)
                    if tp == 'R':
                        # copy and rename
                        # cmd is the name of the new file
                        tpath = '%s/%s' % (target, cmd)
                        # only overwrite if overwrite is set
                        if overwrite and os.path.exists(tpath):
                            os.remove(tpath)
                        if overwrite or (not os.path.exists(tpath)):
                            shutil.copyfile(spath, tpath)
                    if tp == 'U':
                        # update the content of the file by replacing variables
                        if os.path.exists(tpath):
                            os.remove(tpath)
                        if overwrite or (not os.path.exists(tpath)):
                            open(tpath, 'w').write(
                                open(spath, 'r').read() % self.default_values)
                        if cmd == 'X':
                            # set executable
                            st = os.stat(tpath)
                            os.chmod(tpath, st.st_mode | stat.S_IEXEC)
                elif isinstance(tp, dict):
                    # new directory
                    newsource = '%s/%s' % (source, fname)
                    newtarget = '%s/%s' % (target, fname)
                    if not os.path.exists(newtarget):
                        os.mkdir(newtarget)
                    self.handle_file_copy_move(newsource, newtarget, tp)
                else:
                    # this is just a simple command ..
                    if tp in ['F', 'O', 'U']:
                        if tp in ('O', 'U'):
                            overwrite = True
                        # a normal file
                        # only overwrite if overwrite is set
                        if overwrite and os.path.exists(tpath):
                            os.remove(tpath)
                        if overwrite or (not os.path.exists(tpath)):
                            if tp == 'O':
                                try:
                                    # make sure all placeholders are replaced
                                    data = open(spath, 'r').read(
                                    ) % self.default_values
                                    open(tpath, 'w').write(data)
                                except TypeError:
                                    shutil.copyfile(spath, tpath)
                            elif tp == 'U':
                                open(tpath, 'w').write(
                                    open(spath, 'r').read() % self.default_values)
                            else:
                                shutil.copyfile(spath, tpath)
                    elif tp == 'X':
                        # a normal file, but set execution flag
                        # only overwrite if overwrite is set
                        overwrite = True  # X always overwrites
                        if overwrite and os.path.exists(tpath):
                            os.remove(tpath)
                        if overwrite or (not os.path.exists(tpath)):
                            shutil.copyfile(spath, tpath)
                        # set executable
                        st = os.stat(tpath)
                        os.chmod(tpath, st.st_mode | stat.S_IEXEC)
                    elif tp == 'L':
                        if overwrite and os.path.exists(tpath):
                            os.remove(tpath)
                        # a link
                        if not os.path.exists(tpath):
                            shutil.copyfile(spath, tpath)
                    elif tp == 'D':
                        # a folder to create
                        # f overwrite and os.path.exists(tpath):
                            # hutil.rmtree(tpath, True)
                        if not os.path.exists(tpath):
                            os.mkdir(tpath)
                    elif tp == 'T':
                        # just touch to create
                        open(tpath, 'a').close()
            except IOError as e:
                print(str(e))
            except Exception as e:
                if self.opts.verbose:
                    print(str(e))
                    

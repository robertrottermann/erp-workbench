import os
from copy import deepcopy
from config import BASE_PATH, PROJECT_DEFAULTS, BASE_INFO, DOCKER_DEFAULTS
from site_desc_handler.sdesc_utilities import _construct_sa
import re
import shutil
import subprocess
from scripts.properties_mixin import PropertiesMixin

class SiteDescHandlerMixin(PropertiesMixin):
    """This class holds the site descriptions and
    knows how to handle them
    
    Arguments:
        object {[type]} -- [description]
    """

    # -------------------------------------------------------------
    # set properties for users and passwords
    # -------------------------------------------------------------
    # the setings of the DEFAULT_XX properties must be done beforehand
    def set_passwords(self, running_site):
        """set all passwords that are needed

        these are:

        # docker hub

        - dockerhub pw
        
        # running without docker
            login to odoo:
                rpc_user
                rpc_user_pw / rpc_pw ???
            db user:
                db_user
                db_password
        # running as docker container
            login to odoo:
                docker_rpc_user
                docker_rpc_user_pw
            db user:
                docker_db_user / docker_db_user which one ??
                docker_db_admin_pw why admin???

        # remote user:
            we log in as this user into the remote machine:
                remote_user
                _remote_user_pw

        """

        # -------------------------------------------------------------
        # merge passwords
        # -------------------------------------------------------------

        # the site description normally does not contain passwords
        # they are collected from a utility called sites_pw.SITES_PW
        # and then merged into the site description

        DEFAULT_PWS = {
            'odoo_admin_pw': '',
            'docker_hub_pw': ''  # ??
            #'email_pw_incomming' : '',
            #'email_pw_outgoing' : '',
        }
        # read passwords
        SITES_PW = {}  # no passwords, if we can not import them
        try:
            from sites_pw import SITES_PW
        except ImportError:
            pass
        # old setting
        if 'site_name' in running_site.keys():

            # get passwords from the password store
            site_name = running_site['site_name']
            # get a dict with pw info
            kDic = SITES_PW.get(site_name, {})

            # get the  odoo main password
            self._erp_admin_pw = kDic.get('odoo_admin_pw', '')

            # the db_user is read from the config.yaml and user as a default user
            self._db_user = self.base_info.get('db_user')
            db_password = self.base_info.get('db_password')
            self._db_user_pw = self.opts.__dict__.get(
                'db_password', db_password)

            self._rpc_user =  self.opts.__dict__.get(
                'rpc_user', db_user)

            self._rpc_user_pw = self.opts.__dict__.get(
                'rpc_password', db_password)

            @property
            def docker_db_user(self):
                return self.login_info.get('docker_db_user') or self.opts.db_user

            @property
            def db_password(self):
                if self.subparser_name == 'docker':
                    return self.docker_db_admin_pw
                return self.login_info.get('db_password')

            @property
            def db_user(self):
                if self.subparser_name == 'docker':
                    return self.docker_db_admin
                return self.login_info.get('db_user') or self.opts.__dict__.get('db_user', self.base_info['db_user'])

            self._remote_user = remote_server.get('remote_user', '')

            # -----------------
            # local
            # -----------------
            
            login_info['db_password'] = self.opts.__dict__.get(
                'db_password', db_password)
            login_info['db_user'] = self.opts.__dict__.get('db_user', db_user)
            # access to the locally running odoo
            login_info['rpc_user'] 
            login_info['rpc_pw']

            # -----------------
            # remote
            # -----------------
            # remote user depends which server the site is running on
            server = self.site and self.remote_servers.get(
                site_server_ip, {}) or {}
            login_info['remote_user'] = server.get('remote_user') or ''
            login_info['remote_user_pw'] = self.site and server.get(
                'remote_pw') or ''
            login_info['remote_db_password'] = self.opts.__dict__.get(
                'db_password', db_password)
            login_info['remote_db_user'] = self.opts.__dict__.get(
                'db_user', db_user)
            # docker
            # while docker opts are not yet loaded
            try:
                login_info['remote_docker_db_user'] = self.opts.remotedockerdbuser
                login_info['remote_docker_db_pw'] = self.opts.remotedockerdbpw
            except:
                login_info['remote_docker_db_user'] = ''
                login_info['remote_docker_db_pw'] = ''

    def prepare_properties(self, running_site):
        """collect information from yaml files and the site description
        
        Arguments:
            running_site {dict} -- site description
        """

        # old setting
        if 'site_name' in running_site.keys():
            remote_server = site['remote_server']
            self._remote_server_ip = remote_server.get('remote_url', '')
            self._remote_data_path = remote_server.get('remote_data_path', '')
            self._remote_sites_home = remote_server.get('remote_sites_home', '')
            self._redirect_email_to = remote_server.get('redirect_emil_to', '')

            # apache & nginx
            apache = site['apache']
            self._remote_http_url = apache.get('vservername', 'no vserver')



        else:
            # need to group the servers that are accessible on the same ip
            # in a "parent" structure
            pass



    def _parse_site(self, site):
        self._erp_minor = site.get('erp_minor', self.project_defaults.get('erp_minor', '12'))
        self._erp_nightly = site.get(
            'erp_nightly', self.project_defaults.get('erp_nightly', '12'))
        self._erp_version = site.get('erp_version', self.project_defaults.get(
            'erp_version', self.project_defaults.get('odoo_version', '12')))
        self._erp_provider = site.get('erp_provider', self.project_defaults.get(
            'erp_provider', self.project_defaults.get('erp_provider', '12')))

    # ----------------------------------
    # construct_defaults
    # construct defaultvalues for a site
    # @site_name        : name of the site
    # ----------------------------------
    #  the parent class must have the
    # _sites <- all sites
    # _sites_local <- local sites
    # class variables 
    def construct_defaults(self, site_name):
        """
        construct defaultvalues for a site
        @site_name        : name of the site
        """
        # construct a dictonary with default values
        # some of the values in the imported default_values are to be replaced
        # make sure we can do this more than once
        from templates.default_values import default_values as d_v
        self._default_values = deepcopy(d_v)
        default_values = self.default_values
        default_values['sites_home'] = BASE_PATH
        # first set default values that migth get overwritten
        # local sites are defined in local_sites and are not added to the repository
        is_local = site_name and not(self.sites_local.get(site_name) is None)
        default_values['is_local'] = is_local
        default_values['db_user'] = self.db_user
        # the site_name is defined with option -n and was checked by check_name
        default_values['site_name'] = site_name
        default_values.update(BASE_INFO)
        if site_name and isinstance(site_name, str) and self.sites.get(site_name):
            default_values.update(self.sites.get(site_name))
        # now we try to replace the %(xx)s element with values we connected from 
        # the yaml files
        tmp_dic = {}
        for td in [DOCKER_DEFAULTS, PROJECT_DEFAULTS]:
            tmp_dic.update(td)
        for k,v in self.default_values.items():
            try:
                if v: # if empty or noe, there is nothing to replace
                    self.default_values[k] = v % tmp_dic
            except:
                pass
        # we need nightly to construct an url to download the software 
        if not self.default_values.get('erp_nightly'):
            self.default_values['erp_nightly'] = PROJECT_DEFAULTS.get(
                'erp_nightly') or '%s%s' % (self.default_values['erp_version'], self.default_values['erp_minor'])
        if not self.default_values.get('erp_provider'):
            self.default_values['erp_provider'] = PROJECT_DEFAULTS.get(
                'erp_provider', 'odoo')
        # now make sure we have a minor version number
        if not default_values.get('erp_minor'):
            default_values['erp_minor'] = PROJECT_DEFAULTS.get('erp_minor', '')
        site_base_path = os.path.normpath(os.path.expanduser(
            '%(project_path)s/%(site_name)s/' % default_values))
        # /home/robert/projects/afbsecure/afbsecure/parts/odoo
        default_values['base_path'] = site_base_path
        default_values['data_dir'] = "%s/%s" % (
            self.erp_server_data_path, self.site_name)
        default_values['db_name'] = site_name
        default_values['outer'] = '%s/%s' % (
            BASE_INFO['project_path'], site_name)
        default_values['inner'] = '%(outer)s/%(site_name)s' % default_values
        default_values['addons_path'] = '%(base_path)s/parts/odoo/openerp/addons,%(base_path)s/parts/odoo/addons,%(data_dir)s/%(site_name)s/addons' % default_values
        # if we are using docker, the addon path is very different
        default_values['addons_path_docker'] = '/mnt/extra-addons,/usr/lib/python2.7/dist-packages/openerp/addons'
        default_values['skeleton'] = '%s/skeleton' % self.sites_home
        # add modules that must be installed using pip
        _s = {}
        if is_local:
            _s = self._sites_local.get(site_name)
        else:
            if self._sites.get(site_name):
                _s = self._sites.get(site_name)
        site_addons = _s.get('addons', [])
        pip_modules = _s.get('extra_libs', {}).get('pip', [])
        skip_list = _s.get('skip', {}).get('addons', [])
        # every add on module can have its own pip module that must be used
        for addon in _s.get('addons', []):
            pip_modules += addon.get('pip_list', [])
        pm = '\n'
        if pip_modules:
            pip_modules = list(set(pip_modules)) # make them uniqu
            for m in pip_modules:
                pm += '%s\n' % m
        default_values['pip_modules'] = pm
        # the site addons will only contain paths to download
        # if from one of the downloaded addon folders more than one addon should be installed ??????
        default_values['site_addons'] = _construct_sa(
            site_name, deepcopy(site_addons), skip_list)

        default_values['skip_list'] = skip_list

        # make sure that all placeholders are replaced
        m = re.compile(r'.*%\(.+\)s')
        for k, v in list(self.default_values.items()):
            if isinstance(v, str):
                counter = 0
                while m.match(v) and counter < 10:
                    v = v % self.default_values
                    self.default_values[k] = v
                    counter += 1  # avoid endless loop
        if not self.default_values.get('erp_version'):
            if 'erp_version' in vars(self.opts).keys():
                erp_version = self.opts.erp_version
            else:
                erp_version = PROJECT_DEFAULTS.get('erp_version', '12.0')
            self.default_values['erp_version'] = erp_version

    def remove_virtual_env(self, site_name):
        """remove an existing virtual env
         
         Arguments:
             site_name {string} -- the name of the virtual env to remove
        """
        virtualenvwrapper = shutil.which('virtualenvwrapper.sh')
        commands = """
        export WORKON_HOME=%(home)s/.virtualenvs\n
        export PROJECT_HOME=/home/robert/Devel\n
        source %(virtualenvwrapper)s\n
        rmvirtualenv  %(site_name)s       
        """ % {
            'home': os.path.expanduser("~"),
            'virtualenvwrapper': str(virtualenvwrapper),
            'site_name': site_name
        }
        p = subprocess.Popen(
            '/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate(commands.encode())

    def do_collect_addon_paths(self):
        from scripts.utilities import collect_addon_paths
        self._addpath_collected = True
        collect_addon_paths(self)

    #_did_run_create_login = False
    def _create_login_info(self, login_info):
        # ----------------------------------
        # what login do we need
        # local:
        #    local user
        #    odoo rpc
        #    odoo admin
        #    docker db user
        #    docker db password
        #    docker admin pw
        #    docker master pw
        # remote:
        #    remote usercreate_virtual_env
        #    # no password, as only key allowed
        #    odoo rpc
        #    odoo admin
        #    docker db user
        #    docker db password
        #    docker admin pw
        #    docker master pw

        # -----------------
        # local
        # -----------------
        # actual user
        if self.opts.__dict__.get('delete_site_local') or self.opts.__dict__.get('drop_site'):
            return
        if self.site:
            p = '%s/sites_global/%s.py' % (
                self.base_info['sitesinfo_path'], self.site_name)
            if not self.site.get('remote_server'):
                print(SITE_HAS_NO_REMOTE_INFO %
                      (self.site_name, os.path.normpath(p)))
                site_server_ip = 'localhost'
            else:
                site_server_ip = self.site['remote_server']['remote_url']
            try:
                site_server_ip = socket.gethostbyname(site_server_ip)
            except:
                pass
            # robert restructure
            #if site_server_ip == 'xx.xx.xx.xx':
                #if self.default_values['is_local']:
                #p = '%s/sites_local/%s.py' % (
                #self.base_info['sitesinfo_path'], self.site_name)
                #print(SITE_NOT_EDITED % (self.site_name, os.path.normpath(p)))
                #selections = self.selections
                #must_exit = True
                #if selections:
                #for s in selections:
                #if s[0] in NO_NEED_SERVER_IP:
                #must_exit = False
                #if must_exit:
                #sys.exit()
            if self.site and not self.remote_servers.get(site_server_ip):
                selections = self.selections
                must_exit = True
                if selections:
                    for s in selections:
                        if s[0] in NO_NEED_SERVER_IP:
                            must_exit = False
                if must_exit:
                    print(SITE_UNKNOW_IP % (site_server_ip,
                                            self.site_name, self.user, site_server_ip))
                    sys.exit()
            login_info['user'] = self.user
            # access to the local database
            # access to the local docker

    def create_virtual_env(self, target, python_version='python2.7', use_workon=True):
        """
        """
        "create a virtual env within the new project"
        adir = os.getcwd()
        os.chdir(target)
        # here we have to decide whether we run flectra or odoo
        if 1:  # erp_provider == 'flectra' or use_workon:
            # need to find virtualenvwrapper.sh
            virtualenvwrapper = shutil.which('virtualenvwrapper.sh')
            os.chdir(self.default_values['inner'])
            cmd_list = [
                'export WORKON_HOME=%s/.virtualenvs' % os.path.expanduser("~"),
                'export PROJECT_HOME=/home/robert/Devel',
                'source %s' % virtualenvwrapper,
                'mkvirtualenv -a %s -p %s %s' % (
                    self.default_values['inner'],
                    python_version,
                    self.site_name
                )
            ]
            commands = b'$$'.join([e.encode() for e in cmd_list])
            commands = commands.replace(b'$$', b'\n')
            #p = subprocess.call(commands, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            p = subprocess.Popen(
                '/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=os.environ.copy())
            out, err = p.communicate(input=commands)
            if not self.opts.quiet:
                print(out)
                print(err)
        else:
            # create virtual env
            cmd_line = ['virtualenv', '-p', python_version, 'python']
            p = subprocess.Popen(cmd_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if self.opts.verbose:
                print(os.getcwd())
                print(cmd_line)
                print(p.communicate())
            else:
                p.communicate()
        os.chdir(adir)

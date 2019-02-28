import os
import sys
from copy import deepcopy
from site_desc_handler.sdesc_utilities import _construct_sa
import re
import shutil
import subprocess
from scripts.properties_mixin import PropertiesMixin
from scripts.bcolors import bcolors 
from argparse import Namespace
from scripts.messages import SITE_NOT_EXISTING, SITE_HAS_NO_REMOTE_INFO, SITE_UNKNOW_IP
from site_desc_handler.sdesc_utilities import flatten_sites

class DummyNamespace(Namespace):
    # we need a namespace that just ignores unknow options
    def __getattr__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        return ''

class SiteDescHandlerMixin(PropertiesMixin):
    """This class holds the site descriptions and
    knows how to handle them
    
    Arguments:
        object {[type]} -- [description]
    """

    # provide opts, so we can survive the very first call
    # later opts will be replace by the one presented to the user
    opts = DummyNamespace()
    
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
                rpc_user_pw
            db user:
                db_user
                db_password
        # running as docker container
            login to odoo:
                docker_rpc_user
                docker_rpc_user_pw
            db user:
                docker_db_user 
                docker_db_user_pw 

        # remote user:
            we log in as this user into the remote machine:
                remote_user
                remote_user_pw

        """

        if not running_site:
            running_site = {} # to be sure ..
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
        
        # -------------------------------------------------------------
        # old setting
        # -------------------------------------------------------------
        if 1: #'site_name' in running_site.keys():

            # get passwords from the password store
            site_name = running_site.get('site_name', self.opts.name and self.opts.name.split(':')[0] or '')
            # get a dict with pw info
            kDic = SITES_PW.get(site_name, {})

            # get the  odoo main password
            self._erp_admin_pw = kDic.get('odoo_admin_pw', '')
            
            # ----------
            # local
            # ----------
            # the db_user is read from the config.yaml and is used as a default user
            db_user = self.base_info['db_user']
            self._db_user = self.opts.__dict__.get(
                'db_user', db_user)

            db_user_pw = self.base_info.get('db_user_pw')
            self._db_user_pw = self.opts.__dict__.get(
                'db_user_pw', db_user_pw)

            self._rpc_user =  self.opts.__dict__.get(
                'rpc_user', db_user)

            self._rpc_user_pw = self.opts.__dict__.get(
                'rpc_password', db_user_pw)

            self._rpc_port = self.opts.__dict__.get(
                'rpc_port', '8069')

            self._rpc_host = self.opts.__dict__.get(
                'rpc_host', 'localhost')
            
            # ----------
            # docker
            # ----------
            # docker_db_user is aliased to db_user
            self._docker_db_user = ((self.subparser_name == 'docker' and self.opts.docker_db_user) 
                 or self.docker_defaults.get('docker_db_user', ''))
            self._docker_db_user_pw = ((self.subparser_name == 'docker' and self.opts.docker_db_user_pw) 
                 or self.docker_defaults.get('docker_db_user_pw', ''))

            docker_rpc_user = ''
            if self.subparser_name == 'docker':
                docker_rpc_user = self.opts.drpcuser
            if not docker_rpc_user:
                docker_rpc_user = self.docker_defaults.get('docker_rpc_user', '')
            self._docker_rpc_user = docker_rpc_user
            docker_rpc_user_pw = ''
            if self.subparser_name == 'docker':
                docker_rpc_user_pw = self.opts.drpcuserpw
            if not docker_rpc_user_pw:
                # no password was provided by an option
                docker_rpc_user_pw = self.erp_admin_pw
                if not docker_rpc_user_pw:
                    docker_rpc_user_pw = self.docker_defaults.get('docker_rpc_user_pw', '')
            self._docker_rpc_user_pw = docker_rpc_user_pw

            # ------------------------------------
            # database
            # ------------------------------------
            db_container_name = ''
            if self.subparser_name == 'docker':
                db_container_name = self.opts.dockerdbname
            if not db_container_name:
                db_container_name = self.docker_defaults.get('dockerdb_container_name', 'db')
            self._docker_db_container_name = db_container_name
            
            # get the dbcontainer
            docker_db_container = ''
            if self.subparser_name == 'docker':
                docker_db_container_name = self.docker_db_container_name
                db_container_list = self.docker_containers(filters = {'name' : docker_db_container_name})
                if db_container_list:
                    docker_db_container = db_container_list[0]
                else:
                    try:
                        # as this is a docker handler instance, try to create it
                        # but not if we are executing the command -dcdb to create a db container
                        if not self.opts.docker_create_db_container:
                            self.check_and_create_container(container_name='db')
                            db_container_list = self.docker_containers(filters = {'name' : docker_db_container_name})
                            if db_container_list:
                                docker_db_container = db_container_list[0]                        
                    except Exception as e:
                        print(bcolors.FAIL)
                        print('*' * 80)
                        print('either the db container was missing and could not be created or some other problem')
                        print(str(e))
                        sys.exit()
                self._docker_db_container = docker_db_container
            
            if self.subparser_name == 'docker':
                # try to read the output of the command docker inspect containername
                # and collect the ip address of its first network interface
                registry = self.docker_registry.get(self.docker_container_name)
                try:
                    docker_rpc_host = registry['NetworkSettings']['IPAddress']
                except:
                    docker_rpc_host = 'localhost'
                self._docker_rpc_host = docker_rpc_host

            # make sure that within a docker container no "external" paths are used
            self._docker_path_map =  (os.path.expanduser('~/'), '/root/')

            # ------------------------------------
            # odoo version, minor, nightly
            # ------------------------------------
            # version
            erp_version = running_site.get('erp_version', running_site.get('odoo_version'))
            if not erp_version:
                erp_version = self.project_defaults.get('erp_version', '12')
            self._erp_version = erp_version
            # minor
            erp_minor = running_site.get('erp_minor')
            if not erp_minor:
                erp_minor = self.project_defaults.get('erp_minor', '.0')
            self._erp_minor = erp_minor
            # make sure version has no minor
            try:
                self._erp_version = str(int(float(self._erp_version)))
            except ValueError:
                pass
            # nightly
            erp_nightly = running_site.get('erp_nightly')
            if not erp_nightly:
                erp_nightly = '%s%s' % (self.erp_version, self.erp_minor)
            self._erp_nightly = erp_nightly
            # provider
            self._erp_provider = running_site.get('erp_provider',  'odoo')

            # ------------------------------------
            # docker stuff
            # ------------------------------------
            docker_hub = running_site.get('docker_hub', {}).get('docker_hub', {})
            docker = running_site.get('docker', {})
            # docker hub
            self._docker_hub_name = docker_hub.get(
                'user', self.docker_defaults.get('docker_hub_name', ''))
            self._docker_hub_pw = docker_hub.get('docker_hub_pw', '' )
            
            # docker
            self._docker_base_image = docker.get('base_image', 'camptocamp/odoo-project:%s-latest' % self.erp_version)
            erp_image_version = docker.get('erp_image_version', docker.get('odoo_image_version'))
            if not erp_image_version:
                erp_image_version = self.docker_defaults.get('erp_image_version', 'no-erp_image_version-defined')
            self._docker_image_version = erp_image_version
            self._docker_container_name = docker.get('container_name', self.site_name)
            self._docker_rpc_port = docker.get(
                'erp_port', docker.get('odoo_port'))
            docker_long_polling_port = docker.get('erp_longpoll', docker.get('odoo_longpoll'))
            if not docker_long_polling_port:
                if self.docker_rpc_port:
                    docker_long_polling_port = int(self.docker_rpc_port) + 10000
                
            self._docker_long_polling_port = docker_long_polling_port     
            self._docker_external_user_group_id = docker.get('external_user_group_id', '104:107')

            # ------------------------------------
            # remote
            # ------------------------------------
            remote_server = running_site.get('remote_server', {})
            self._remote_server_ip = remote_server.get('remote_url', '')
            self._remote_data_path = remote_server.get('remote_data_path', '')
            self._remote_sites_home = remote_server.get('remote_sites_home', '')
            self._redirect_email_to = remote_server.get('redirect_emil_to', '')

            # ------------------------------------
            # apache & nginx
            # ------------------------------------
            apache = running_site.get('apache', {})
            self._remote_http_url = apache.get('vservername', 'no vserver')

            # ------------------------------------
            # db
            # ------------------------------------
            if self.subparser_name == 'docker':
                self._db_host = running_site.get('db_host', self._remote_server_ip)
            else:
                self._db_host = 'localhost'
                
            # ------------------------------------
            # docker db
            # ------------------------------------
            self._docker_db_container_name = self.docker_defaults.get('docker_db_container_name', '')

            if self.subparser_name == 'docker':
                self._docker_db_user = self.opts.docker_db_user or self.docker_defaults.get('docker_db_user', '')
            else:
                self._docker_db_user = self.docker_defaults.get('docker_db_user', '')

    def collect_extra_libs(self):
        """
        collect apt modules and pip libraries needed to construct image with expected capabilities
        we collect them from the actual site, and all sites named with the option -sites
        """
        extra_libs = self.site.get('extra_libs', {})
        if 0:
            # this is not yet re-implemented
            if self.opts.use_collect_sites:
                erp_version = self.erp_version
                more_sites = []
                for k, v in list(self.sites.items()):
                    if v.get('erp_version') == erp_version:
                        more_sites.append(k)
            else:
                more_sites = (self.opts.use_sites or '').split(',')
        more_sites = []
        # libraries we need to install using apt
        apt_list = extra_libs.get(self.apt_command, [])
        # libraries we need to install using pip
        pip_list = extra_libs.get(self.pip_command, [])
        for addon in self.site.get('addons', []):
            pip_list += addon.get('pip_list', [])
            apt_list += addon.get('apt_list', [])
        for s in more_sites:
            if not s:
                continue
            site = self.sites.get(s)
            if not site:
                print((SITE_NOT_EXISTING % s))
                continue
            apt_list += site.get('extra_libs', {}).get(self.apt_command, [])
            pip_list += site.get('extra_libs', {}).get(self.pip_command, [])
            for addon in self.site.get('addons', []):
                pip_list += addon.get('pip_list', [])
                apt_list += addon.get('apt_list', [])

        if apt_list:
            apt_list = list(set(apt_list))
        if pip_list:
            pip_list = list(set(pip_list))
        if self.opts.verbose:
            print(bcolors.WARNING)
            print('*' * 80)
            print('apt_list:%s' % apt_list)
            print('pip_list:%s' % pip_list)
            print(bcolors.ENDC)
        return apt_list, pip_list

    def handle_addons(self):
        """read the list of addons from the site description
        """
        site_addons = self.site.get('addons', [])
        _construct_sa(
            self.site_name, deepcopy(site_addons), self.site_skip_list)
        
        self._site_addons = site_addons        

    def handle_pip_modules(self):
        """read the list of pip modules from the site description
        """
        _, pip_modules = self.collect_extra_libs()
        #pip_modules = self.site.get('extra_libs', {}).get('pip', [])
        # every add on module can have its own pip module that must be used
        for addon in self._site_addons:
            pip_modules += addon.get('pip_list', [])
        if pip_modules:
            pip_modules = list(set(pip_modules))  # make them unique
        self._site_pip_modules = pip_modules

    def handle_apt_modules(self):
        """read the list of apt libraries to instll in the base image from the site description
        """
        apt_modules, _ = self.collect_extra_libs()
        # apt_modules = self.site.get('extra_libs', {}).get('apt', [])
        # every add on module can have its own pip module that must be used
        for addon in self._site_addons:
            apt_modules += addon.get('apt_list', [])
        self._site_apt_modules = apt_modules

    def handle_skip_list(self):
        """read the list of addons from the site description
        """
        skip_list = self.site.get('skip', {}).get('addons', [])
        self._site_skip_list = skip_list

    def collect_addons(self):
        """
        go trough the addons in syte.py and collect
        addon_path info for the actual site. 
        """
        addons = self.site.get('addons', [])
        apps = []
        for addon in addons:
            elem = addon.get('add_path', addon.get('group'))
            if elem:
                apps.append(elem)
        return apps

    def prepare_properties(self, running_site):
        """collect information from yaml files and the site description
        
        Arguments:
            running_site {dict} -- site description
        """
        self.set_passwords(running_site)
        # # resolve inheritance within sites
        flatten_sites(self._sites)        
        # construct the addons path
        self._site_addons_list = self.collect_addons() 
        self.handle_skip_list()
        self.handle_apt_modules()
        self.handle_pip_modules()
        self.handle_addons()
        
    # ----------------------------------
    # construct_defaults
    # construct defaultvalues for a site
    # @site_name        : name of the site
    # ----------------------------------
    #  the parent class must have the
    # _sites <- all sites
    # _sites_local <- local sites
    # class variables 
    def construct_defaults(self):
        """
        construct default values for a site
        these values are used to replace the placeholders
        within templates with actual values
        """
        # construct a dictonary with default values
        default_values = self._default_values
        default_values['sites_home'] = self.sites_home
        # first set default values that migth get overwritten
        # local sites are defined in local_sites and are not added to the repository
        default_values['is_local'] = self.site.get('is_local')
        default_values['db_user'] = self.db_user
        default_values['site_name'] = self.site_name
        default_values.update(self.base_info)
        # make sure site descriptions with odoo instead of erp ar fixed
        if self.site.get('odoo_version'):
            # hoppalla, we need to adapt this
            print(bcolors.BOLD, bcolors.OKBLUE)
            print('*' * 80)
            print('the site %s uses "odoo_version" but should use "erp_version", please fix' % self.site_name)
            print(bcolors.ENDC)
            self.site['erp_version'] = self.site.get('odoo_version')
        default_values.update(self.site)
        # now we try to replace the %(xx)s element with values we connected from 
        # the yaml files
        tmp_dic = {}
        for td in [self.docker_defaults, self.project_defaults]:
            tmp_dic.update(td)
        for k,v in self.default_values.items():
            try:
                if v: # if empty or none, there is nothing to replace
                    self.default_values[k] = v % tmp_dic
            except:
                pass
        # we need nightly to construct an url to download the software 
        if not self.default_values.get('erp_nightly'):
            self.default_values['erp_nightly'] = self.erp_nightly
        if not self.default_values.get('erp_provider'):
            self.default_values['erp_provider'] = self.erp_provider
        # now make sure we have a minor version number
        if not default_values.get('erp_minor'):
            default_values['erp_minor'] = self.erp_minor
        default_values['base_path'] = self.sites_home
        default_values['data_dir'] = self.site_data_dir
        default_values['db_name'] = self.site_name
        default_values['outer'] = self.outer_path
        default_values['inner'] = self.inner_path
        default_values['local_site_addons_path'] = self.local_site_addons_path
        # if we are using docker, the addon path is very different
        default_values['addons_path_docker'] = '/mnt/extra-addons,/usr/lib/python2.7/dist-packages/openerp/addons'
        default_values['skeleton'] = self.skeleton_path

        # modules we have to deal with in a special way
        default_values['site_addons'] = self.site_addons
        default_values['docker_site_addons_path'] = self.docker_site_addons_path        
        default_values['local_site_addons_path'] = self.local_site_addons_path        
        default_values['skip_list'] = self.site_skip_list
        default_values['pip_modules_str'] = '\n'.join(self.site_pip_modules)
        default_values['apt_modules'] = self.site_apt_modules
        default_values['skip_list'] = self.site_skip_list
        default_values['inner_path'] = self.inner_path
        default_values['site_data_dir'] = self.site_data_dir

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
                erp_version = self.project_defaults.get('erp_version', '12.0')
            self.default_values['erp_version'] = erp_version

        self.default_values['base_sites_home'] = '/home/%s/erp_workbench' % self.user
        self.default_values['base_url'] = ('%s.ch' % self.site_name)
        self.default_values['marker'] = '\n' + self.marker
        self.default_values['remote_server'] = self.remote_server_ip
        self.default_values['docker_hub_name'] = self.docker_hub_name
        self.default_values['erp_image_version'] = self.erp_image_version
        self.default_values['docker_port'] = self.docker_defaults.get('docker_port', 9000)
        self.default_values['docker_long_poll_port'] = self.docker_defaults.get('docker_long_poll_port', 19000)
        self.default_values['username'] = self.user
        self.default_values['db_host'] = self.db_host
        self.default_values['db_password'] = self.db_user_pw
        self.default_values['log_db_level'] = self.docker_defaults.get('docker_log_db', False)
        self.default_values['erp_admin_pw'] = self.erp_admin_pw
        self.default_values['create_database'] = True
        self.default_values['foldernames'] = self.foldernames
        self.default_values['projectname'] = self.projectname

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
        #self._addpath_collected = True
        return collect_addon_paths(self)

    #_did_run_create_login = False
    def XX_create_login_info(self, login_info):
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
            os.chdir(self.inner_path)
            cmd_list = [
                'export WORKON_HOME=%s/.virtualenvs' % os.path.expanduser("~"),
                'export PROJECT_HOME=/home/robert/Devel',
                'source %s' % virtualenvwrapper,
                'mkvirtualenv -a %s -p %s %s' % (
                    self.inner_path,
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

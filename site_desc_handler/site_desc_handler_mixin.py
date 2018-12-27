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

    def _merge_pw(self, site):
        # merge passwords
        # -------------------------------------------------------------
        DEFAULT_PWS = {
            'odoo_admin_pw': '',
            #'email_pw_incomming' : '',
            #'email_pw_outgoing' : '',
        }
        # read passwords
        SITES_PW = {}
        try:
            from sites_pw import SITES_PW
        except ImportError:
            pass
        # merge them
        for key in list(self.sites.keys()):
            kDic = SITES_PW.get(key, DEFAULT_PWS)
            for k in list(DEFAULT_PWS.keys()):
                self.sites[key][k] = kDic.get(k, '')
            pass # so we can stop the debugger here

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

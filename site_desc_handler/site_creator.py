import os
import sys
import shutil
import subprocess
from scripts.update_local_db import DBUpdater
from scripts.bcolors import bcolors
from scripts.create_handler import InitHandler
from config import LOGIN_INFO_FILE_TEMPLATE, REQUIREMENTS_FILE_TEMPLATE, MODULES_TO_ADD_LOCALLY

LOGIN_INFO_TEMPLATE_FILE = '%s/login_info.cfg.in'

class SiteCreator(InitHandler, DBUpdater):
    
    def __init__(self, opts, sites):
        super(SiteCreator, self).__init__(opts, sites)

    _subparser_name = 'create'
    @property
    def subparser_name(self):
        return self._subparser_name     

    # ------------------------------------
    # get_value_from_config
    # gets a value from etc/open_erp.conf
    # ------------------------------------
    def get_value_from_config(self, path, key=''):
        """
        gets a value from etc/open_erp.conf
        """
        res = {}
        for l in open(path):
            if l and l.find('=') > -1:
                parts = l.split('=', 1)
                res[parts[0].strip()] = parts[1].strip()
        if key:
            return res.get(key)
        else:
            return res

    # =============================================================
    # create site stuff
    # =============================================================
    def create_or_update_site(self):
        # read and update the data from which login_info.cfg.in will be created
        config_info = self.get_config_info()
        # check if the project in the project folder defined in the configuration exists
        # if not create the project structure and copy all files from the skeleton folder
        existed = False
        if self.site_name:
            existed = self.check_project_exists()
            # construct list of addons read from site
            open(LOGIN_INFO_FILE_TEMPLATE % self.default_values['inner'], 'w').write(
                config_info % self.default_values)
            # overwrite requrements.txt with values from systes.py
            data = open(REQUIREMENTS_FILE_TEMPLATE %
                        self.default_values['inner'], 'r').read()
            # we want to preserve changes in the requirements.txt
            data = '\n'.join(list(dict(enumerate([d for d in data.split('\n') if d] +
                                            self.default_values['pip_modules'].split('\n'))).values()))
            # MODULES_TO_ADD_LOCALLY are allways added to a local installation
            # these are tools to help testing and such
            s = data.split('\n') + (MODULES_TO_ADD_LOCALLY and MODULES_TO_ADD_LOCALLY or [])
            s = set(s)
            open(REQUIREMENTS_FILE_TEMPLATE % self.default_values['inner'], 'w').write(
                '\n'.join(s))  # 25.7.17 robert % self.default_values)
        return existed

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
        erp_provider = self.site.get('erp_provider', 'odoo')
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
            p = subprocess.Popen(cmd_line, stdout=PIPE, stderr=PIPE)
            if self.opts.verbose:
                print(os.getcwd())
                print(cmd_line)
                print(p.communicate())
            else:
                p.communicate()
        os.chdir(adir)

    def get_config_info(self):
        """
        collect values needed to put into the openerp.cfg file
        """
        default_values = self.default_values
        default_values['projectname'] = self.projectname
        # only set when creating or editing the site
        default_values['erp_version'] = self.site.get('erp_version', self.site.get('odoo_version', ''))
        # read the login_info.py.in
        # in this file, all variables are of the form $(VARIABLENAME)$
        # replace_dic is constructed in get_user_info_base->build_replace_info
        # the names to replace are defined globaly as REPLACE_NAMES
        p2 = LOGIN_INFO_TEMPLATE_FILE % default_values['skeleton']
        return open(p2, 'r').read() % default_values

    def check_project_exists(self):
        """
        check if a project exists, if not create it
        """
        opts = self.opts
        default_values = self.default_values
        existed = True
        # we only create a site, if we have a site_name
        if self.site_name:
            # check if project exists
            skeleton_path = default_values['skeleton']
            outer_path = default_values['outer']
            inner_path = default_values['inner']
            if not os.path.exists(inner_path):
                self.create_new_project()
                existed = False
            self.do_copy(skeleton_path, outer_path, inner_path)
            # make sure virtual env exist
            python_version = 'python2.7'
            st = self.erp_provider
            if st == 'odoo':
                try:
                    if float(self.version) > 10:
                        python_version = 'python3'
                except:
                    python_version = 'python3'
            elif st == 'flectra':
                python_version = 'python3'
            self.create_virtual_env(inner_path, python_version=python_version)
        return existed

    def create_new_project(self):
        """ create a new project with all the substructures
            These are:
            - a project structure in procects
            - a folder with a predefined set of folders in
              the data directory
            - a virtual environment (done by the calling method)
        """

        opts = self.opts
        default_values = self.default_values
        "ask for project info, create the structure and copy the files"
        skeleton = default_values['skeleton']
        outer = default_values['outer']
        inner = default_values['inner']
        # create project folders
        # create sensible error message
        # check whether projects folder exists
        pp = default_values['project_path']
        if not os.path.exists(pp) and not os.path.isdir(pp):
            # try to create it
            try:
                os.makedirs(pp)
            except OSError:
                print('*' * 80)
                print('could not create %s' % pp)
                sys.exit()
        for p in [outer, inner]:
            if not os.path.exists(p):
                os.mkdir(p)
        ppath_ini = '%s/__init__.py' % outer
        if not os.path.exists(ppath_ini):
            open(ppath_ini, 'w').close()
        # reate virtualenv
        # copy files
        # reate_virtual_env(inner)

    def do_copy(self, source, outer_target, inner_target):
        opts = self.opts
        # now copy files
        if not(self.site and self.version):
            print(bcolors.WARNING)
            print('*' * 80)
            print('Hoppalla, seems that %s is not a valid name' % self.site_name)
            print(bcolors.ENDC)
            sys.exit()            
        from skeleton.files_to_copy import FILES_TO_COPY, FILES_TO_COPY_FLECTRA, FILES_TO_COPY_ODOO
        if self.site.get('erp_provider', 'odoo') == 'flectra':
            FILES_TO_COPY.update(FILES_TO_COPY_FLECTRA)
        elif 1:  # self.version != '9.0':
            FILES_TO_COPY.update(FILES_TO_COPY_ODOO)
        from pprint import pprint
        # pprint(FILES_TO_COPY)
        # odules_update = False # only copy some files so we can rerun dosetup
        self.handle_file_copy_move(
            source, inner_target, FILES_TO_COPY['project'])
        # create directories and readme in the project home
        if outer_target:
            self.handle_file_copy_move(
                '', outer_target, FILES_TO_COPY['project_home'])
            # now create a versions file
            from templates.versions import VERSIONS, VERSIONS_FLECTRA
            if self.site.get('erp_provider', 'odoo') == 'flectra':
                open('%s/versions.cfg' % outer_target,
                     'w').write(VERSIONS_FLECTRA[self.version])
            else:
                open('%s/versions.cfg' % outer_target,
                     'w').write(VERSIONS[self.version])

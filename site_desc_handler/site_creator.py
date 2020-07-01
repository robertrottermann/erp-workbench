import os
import sys
import shutil
from scripts.update_local_db import DBUpdater
from scripts.bcolors import bcolors
from scripts.create_handler import InitHandler
from config import (
    LOGIN_INFO_FILE_TEMPLATE,
    REQUIREMENTS_FILE_TEMPLATE,
    MODULES_TO_ADD_LOCALLY,
)
from site_desc_handler.site_desc_handler_mixin import SiteDescHandlerMixin


class SiteCreator(InitHandler, DBUpdater, SiteDescHandlerMixin):
    def __init__(self, opts, sites):
        super().__init__(opts, sites)

    _subparser_name = "create"

    @property
    def subparser_name(self):
        return self._subparser_name

    # ------------------------------------
    # get_value_from_config
    # gets a value from etc/open_erp.conf
    # ------------------------------------
    def get_value_from_config(self, path, key=""):
        """
        gets a value from etc/open_erp.conf
        """
        res = {}
        for l in open(path):
            if l and l.find("=") > -1:
                parts = l.split("=", 1)
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
        config_info = self.get_config_info(reset=True)
        # check if the project in the project folder defined in the configuration exists
        # if not create the project structure and copy all files from the skeleton folder
        existed = False
        if self.site_name:
            existed = self.check_project_exists()
            # construct list of addons read from site
            with open(LOGIN_INFO_FILE_TEMPLATE % self.inner_path, "w") as f:
                f.write(config_info)  # % self.default_values)
            # overwrite requrements.txt with values we collected from the site descrition
            # but we want to preserve changes in the requirements.txt
            data = open(REQUIREMENTS_FILE_TEMPLATE % self.inner_path, "r").read()
            data = "\n".join(
                list(
                    dict(
                        enumerate(
                            [d for d in data.split("\n") if d] + self.site_pip_modules
                        )
                    ).values()
                )
            )
            # MODULES_TO_ADD_LOCALLY are allways added to a local installation
            # these are tools to help testing and such
            s = data.split("\n") + (
                MODULES_TO_ADD_LOCALLY and MODULES_TO_ADD_LOCALLY or []
            )
            s = set(s)  # make them unique
            open(REQUIREMENTS_FILE_TEMPLATE % self.inner_path, "w").write(
                "\n".join(s)
            )  # 25.7.17 robert % self.default_values)
        return existed

    def get_config_info(self, reset=False):
        """
        collect values needed to put into the openerp.cfg file
        """
        if reset:
            self.reset_values()
        default_values = self.default_values
        p2 = "%s/login_info.cfg.in" % self.skeleton_path
        with open(p2, "r") as f:
            return f.read() % default_values

    def check_project_exists(self):
        """
        check if a project exists, if not create it
        """
        existed = True
        # we only create a site, if we have a site_name
        if self.site_name:
            virtualenvwrapper = shutil.which("virtualenvwrapper.sh")
            if not virtualenvwrapper:
                print(bcolors.FAIL)
                print("*" * 80)
                print("Can not construct virtualenv for %s" % self.site_name)
                print("Please make sure, that virtualenvwrapper.sh is found in your execution path")
                print("Test by executing: which virtualenvwrapper.sh")
                sys.exit()
            # check if project exists
            skeleton_path = self.skeleton_path
            outer_path = self.outer_path
            inner_path = self.inner_path
            if not os.path.exists(inner_path):
                self.create_new_project()
                existed = False
            self.do_copy(skeleton_path, outer_path, inner_path)
            # make sure virtual env exist
            python_version = "python2.7"
            st = self.erp_provider
            if st == "odoo":
                try:
                    if float(self.erp_version) > 10:
                        python_version = "python3"
                except:
                    python_version = "python3"
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

        "ask for project info, create the structure and copy the files"
        outer_path = self.outer_path
        inner_path = self.inner_path
        # create project folders
        # create sensible error message
        # check whether projects folder exists
        pp = self.project_path
        if not os.path.exists(pp) and not os.path.isdir(pp):
            # try to create it
            try:
                os.makedirs(pp)
            except OSError:
                print("*" * 80)
                print("could not create %s" % pp)
                sys.exit()
        for p in [outer_path, inner_path]:
            if not os.path.exists(p):
                os.mkdir(p)
        ppath_ini = "%s/__init__.py" % outer_path
        if not os.path.exists(ppath_ini):
            open(ppath_ini, "w").close()

    def do_copy(self, source, outer_target, inner_target):
        # now copy files
        if not (self.site and self.erp_version):
            print(bcolors.WARNING)
            print("*" * 80)
            print("Hoppalla, seems that %s is not a valid name" % self.site_name)
            print(bcolors.ENDC)
            sys.exit()
        from skeleton.files_to_copy import FILES_TO_COPY, FILES_TO_COPY_ODOO

        FILES_TO_COPY.update(FILES_TO_COPY_ODOO)
        self.handle_file_copy_move(source, inner_target, FILES_TO_COPY["project"])
        # create directories and readme in the project home
        if outer_target:
            self.handle_file_copy_move("", outer_target, FILES_TO_COPY["project_home"])
            # now create a versions file
            from templates.versions import VERSIONS

            open("%s/versions.cfg" % outer_target, "w").write(
                VERSIONS[self.erp_version]
            )

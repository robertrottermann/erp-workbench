#!bin/python
# -*- encoding: utf-8 -*-

#https://www.digitalocean.com/community/tutorials/how-to-set-up-a-private-docker-registry-on-ubuntu-14-04
from config import ODOO_VERSIONS
#from config.handlers import InitHandler, DBUpdater
from scripts.create_handler import InitHandler
from scripts.update_local_db import DBUpdater
import os
import re
import sys
import shutil
from site_desc_handler.handle_remote_data import get_remote_server_info
from scripts.bcolors import bcolors

from scripts.messages import DOCKER_DB_MISSING #, DOCKER_DB_MISSING, DOCKER_INVALID_PORT, \
#       DOCKER_INVALID_PORT, DOCKER_IMAGE_PULLED, DOCKER_IMAGE_PULL_FAILED, DOCKER_IMAGE_NOT_FOUND, \
#       DOCKER_IMAGE_PUSH_MISING_HUB_INFO, SITE_NOT_EXISTING, DOCKER_IMAGE_CREATE_ERROR, \
#       DOCKER_IMAGE_CREATE_MISING_HUB_INFO, DOCKER_IMAGE_CREATE_MISING_HUB_USER, ERP_VERSION_BAD, \
#       DOCKER_IMAGE_CREATE_MISING_HUB_USER, DOCKER_IMAGE_CREATE_PLEASE_WAIT, DOCKER_IMAGE_CREATE_FAILED, \
#       DOCKER_IMAGE_CREATE_DONE


class MigrationHandler(InitHandler, DBUpdater):
    master = '' # possible master site from which to copy
    def __init__(self, opts, sites = {}):
        """
        """
        super().__init__(opts, sites)

        
    _subparser_name = 'migrate'
    @property
    def subparser_name(self):
        return self._subparser_name 

    _migration_tokens = ''
    @property
    def migration_tokens(self):
        """migration token is a list of names we want to collect values for
        
        Returns:
            list -- list of strings
        """

        return self._migration_tokens
    
    def collect_installed(self, cursor):
        """collect installed apps and modules
        
        Arguments:
            cursor {sql cursor} -- cursor returned by get_cursor
        """
        sql = 'select * from ir_module_module'
        cursor.execute(sql)
        rows = cursor.fetchall()
        result = {}
        for row in rows:
            name = row.get('name')
            state = row.get('state')
            app_id = row.get('id')
            if state == 'installed':
                result[name] = app_id
        return result    

    def collect_migration_info(self):
        """read the migration values for the running sit
        to do so, we collect the values for the tokens we read from
        config/migration.yaml
        """
        pass

    def migrate_remove_apps(self):
        """read a list of apps and modules to delete
        and remove them
        """
        file_with_apps = self.opts.migrate_remove_apps
        cursor = self.get_cursor()
        module_obj = self.get_module_obj()
        
        if not os.path.exists(file_with_apps):
            print(bcolors.FAIL)
            print('*' * 80)
            print('%s does not exist' % file_with_apps)
            print(bcolors.ENDC)
            return
        with open(file_with_apps, 'r') as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        for line in lines:
            if line:
                installed = self.collect_installed(cursor)
                app_id = installed.get(line)
                if app_id:
                    print(bcolors.FAIL)
                    print('*' * 80)
                    print('about to uninstall %s' % line)
                    print(bcolors.ENDC)
                    module_obj.browse(app_id).button_immediate_uninstall()






#!bin/python
# -*- encoding: utf-8 -*-

#https://www.digitalocean.com/community/tutorials/how-to-set-up-a-private-docker-registry-on-ubuntu-14-04
from docker import Client
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
import docker
import datetime
from datetime import date
from requests.exceptions import HTTPError
import shlex

from scripts.messages import DOCKER_DB_MISSING #, DOCKER_DB_MISSING, DOCKER_INVALID_PORT, \
#       DOCKER_INVALID_PORT, DOCKER_IMAGE_PULLED, DOCKER_IMAGE_PULL_FAILED, DOCKER_IMAGE_NOT_FOUND, \
#       DOCKER_IMAGE_PUSH_MISING_HUB_INFO, SITE_NOT_EXISTING, DOCKER_IMAGE_CREATE_ERROR, \
#       DOCKER_IMAGE_CREATE_MISING_HUB_INFO, DOCKER_IMAGE_CREATE_MISING_HUB_USER, ERP_VERSION_BAD, \
#       DOCKER_IMAGE_CREATE_MISING_HUB_USER, DOCKER_IMAGE_CREATE_PLEASE_WAIT, DOCKER_IMAGE_CREATE_FAILED, \
#       DOCKER_IMAGE_CREATE_DONE


class MigrationHandler(InitHandler, DBUpdater):
    master = '' # possible master site from which to copy
    def __init__(self, opts, sites = {}, url='unix://var/run/docker.sock', use_tunnel=False):
        """
        """
        super().__init__(opts, sites)
        try:
            from docker import Client
        except ImportError:
            print('*' * 80)
            print('could not import docker')
            print('please run bin/pip install -r install/requirements.txt')
            return
        self.url = url

        if not self.site:
            return # when we are creating the db container
        # collect data from the site description
        self.setup_docker_env(self.site)
        # make sure the registry exists
        self.update_docker_info()
        # ----------------------
        # get the db container
        # ----------------------
        # the name of the database container is by default db

        # update the docker registry so we get info about the db_container_name
        self.update_container_info()
        
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
    

    def collet_migration_info(self):
        """read the migration values for the running sit
        to do so, we collect the values for the tokens we read from
        config/migration.yaml
        """




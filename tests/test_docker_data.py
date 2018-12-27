import os
import sys
import getpass
import shutil
import unittest
import random
import string
from importlib import reload

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, '.')

try:
    from sites_list_killer import SitesListKiller
    from name_space import MyNamespace
except ImportError:
    from tests.sites_list_killer import SitesListKiller
    from tests.name_space import MyNamespace
    
from scripts import construct_defaults
import sites_list

"""
run it with:
bin/python -m unittest discover tests
"""


class TestGetDockerData(SitesListKiller):
    """I want to refactor how the docker data is stored in
    the site description
    
    Arguments:
        unittest {[type]} -- [description]
    """
    _use_site_name = 'demo_global'

    def setUp(self):
        super().setUp()
        from config.handlers import DockerHandler, SupportHandler

        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'docker'
        args.skip_name = True
        args.quiet = True
        args.name = self._use_site_name
        self.args = args
        self.dHandler = DockerHandler(args, sites_list.SITES_G)

    def test_get_docker_info(self):
        """ 
        get_docker_info is the method, that collects docker info form the
        site description
        """
        import sites_list
        self.dHandler.setup_docker_env(sites_list.SITES_G[self._use_site_name])
        docker_info = self.dHandler.docker_container_name
        self.assertTrue(docker_info==self._use_site_name)
        print(docker_info)

    def test_get_docker_erp_image_version(self):
        # make sure the sites_pw.py provides the following pw for the new site
        self.assertTrue(self.dHandler.docker_rpc_user_pw == 'demo_global$odoo_admin_pw')

    def test_create_docker_composer_dict(self):
        self.dHandler.create_docker_composer_dict()

    def test_create_docker_composer_file(self):
        self.dHandler.create_docker_composer_file()
        

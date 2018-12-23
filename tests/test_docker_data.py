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


class TesGetDockerData(SitesListKiller):
    """I want to refactor how the docker data is stored in
    the site description
    
    Arguments:
        unittest {[type]} -- [description]
    """

    def setUp(self):
        super().setUp()
        from config.handlers import DockerHandler, SupportHandler

        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'docker'
        args.skip_name = True
        args.quiet = True
        self.args = args
        self.dHandler = DockerHandler(args, {})
        self.sHandler = SupportHandler(args, {})
        r_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.new_name = 'new_site_' + r_string
        self.args.add_site = True
        self.args.name = self.new_name + ':localhost'
        result = self.sHandler.add_site_to_sitelist()
        self.kill_sites_list()

    def tearDown(self):
        super().tearDown()
        # remove sites we added
        result = self.sHandler.drop_site()

    def test_get_docker_info(self):
        """ 
        get_docker_info is the method, that collects docker info form the
        site description
        """
        import sites_list
        self.dHandler.setup_docker_env(sites_list.SITES_G[self.new_name])
        docker_info = self.dHandler.docker_container_name
        self.assertTrue(docker_info==self.new_name)
        print(docker_info)

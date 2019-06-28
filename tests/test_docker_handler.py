import os
import sys
import getpass
import shutil
import unittest
import random
import string
from importlib import reload

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .sites_list_killer import SitesListKiller
from .name_space import MyNamespace

"""
run it with:
bin/python -m unittest discover tests
"""



class TestDockerHandler(SitesListKiller):
    """
    """

    def tearDown(self):
        super().tearDown()

    def setUp(self):
        from config.handlers import DockerHandler
        args = MyNamespace()
        args.subparser_name = 'docker'
        args.skip_name = True
        args.quiet = True
        args.docker_create_container = True
        args.name = 'demo_global'
        #args.erp_image_version = ''
        #self.handler.site_names = ['demo_global']
        self.args = args
        self.handler = DockerHandler(args)
   
    def test_check_and_create_container(self):
        self.handler.check_and_create_container()
        self.handler.check_and_create_container(delete_container=True)

    def XXtest_build_image(self):
        self.handler.build_image()

#class TestCreateDB(unittest.TestCase):
    #def setUp(self):
        #from config.handlers import DockerHandler
        #args = MyNamespace()
        #args.subparser_name = 'docker'
        #args.skip_name = True
        #args.quiet = True
        ##args.docker_create_container = True
        #args.name = 'db'
        ##args.erp_image_version = ''
        ##self.handler.site_names = ['demo_global']
        #self.args = args
        #self.handler = DockerHandler(args)

    def test_create_delete_db_container(self):
        result = self.handler.update_docker_info(name='db', required=False, start=False)
        if result:
            self.handler.check_and_create_container(container_name = 'db', delete_container=True)
        result = self.handler.update_docker_info(name='db', required=False, start=False)
        self.assertFalse(result)
        self.handler.check_and_create_container(container_name = 'db')
        result = self.handler.update_docker_info(name='db', required=False, start=False)
        self.assertTrue(result)

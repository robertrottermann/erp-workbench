import os
import sys
import getpass
import shutil
import unittest
import random
import string
import glob
from importlib import reload
import unittest
from tests.name_space import MyNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')


"""
run it with:
bin/python -m unittest discover tests
test_kuber_handler.TestKuberHandler2Data
"""


class TestKuberHandler2Data(unittest.TestCase):
    """I want to refactor how the docker data is stored in
    the site description
    
    Arguments:
        unittest {[type]} -- [description]
    """
    
    def do_setUp(self, config_data={}):
        #from config.handlers import KuberHandler
        #from kuber_handler.kuber_handler import KuberHandlerHelm
        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'docker'
        args.skip_name = True
        args.quiet = True
        args.name = 'demo_global'
        args.docker_use_bitnami = True
        self.args = args
        #self.kHandler = KuberHandlerHelm(args, sites_list.SITES_G, config_data=config_data)
        #helm_target = self.kHandler.helm_target
        #if helm_target and os.path.exists(helm_target):
            #if helm_target.endswith('/helm'):
                #shutil.rmtree('%s/*' % helm_target, ignore_errors = True)

    def test_get_create_main(self):
        """ we want to get the handler that was selected
        """
        self.do_setUp()
        from scripts.create_site import main
        args = self.args
        args.create = True
        need_names_dic = {}
        handler = main(args, args.subparser_name, need_names_dic, return_handler=1)
        self.assertTrue(hasattr(handler, 'chart_name'))

    def test_prepare_build_image(self):
        self.do_setUp()
        from scripts.create_site import main
        args = self.args
        args.create = True
        need_names_dic = {}
        handler = main(args, args.subparser_name, need_names_dic, return_handler=1)
        handler.build_image()
        
    def test_install_chart(self):
        """ 
        the download folder is:
        ~/workbench/demo_global/helm/odoo
        """
        self.do_setUp()
        from scripts.create_site import main
        args = self.args
        args.create = True
        need_names_dic = {}
        handler = main(args, args.subparser_name,
                       need_names_dic, return_handler=1)
        handler.create_binami_container()

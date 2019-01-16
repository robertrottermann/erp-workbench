import os
import sys
import getpass
import shutil
import unittest
import random
import string
from importlib import reload
import unittest
from tests.name_space import MyNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')


"""
run it with:
bin/python -m unittest discover tests
TestGetBitnamiData.test_build_bitnami_dockerfile
"""


class TestGetBitnamiData(unittest.TestCase):
    """I want to refactor how the docker data is stored in
    the site description
    
    Arguments:
        unittest {[type]} -- [description]
    """
    _use_site_name = 'demo_global'

    def setUp(self):
        super().setUp()
        from config.handlers import DockerHandler, SupportHandler
        import sites_list
        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'docker'
        args.skip_name = True
        args.quiet = True
        args.name = self._use_site_name
        self.args = args
        self.dHandler = DockerHandler(args, sites_list.SITES_G)

    def test_build_bitnami_dockerfile(self):
        """ create a docker image according to the gospel of bitnami
        here we just create it and check whether it exists
        
        """
        self.dHandler.build_image_bitnami()


class TestKuberHandler(unittest.TestCase):

    _chart = ''
    def setUp(self):
        super().setUp()
        from kuber_handler.kuber_handler import KuberHandler
        config_data = {'port' : 8069}
        if self._chart:
            config_data['chart'] = self._chart
        self.kHandler = KuberHandler(config_data)

    def test_get_tiller(self):
        """ create a docker image according to the gospel of bitnami
        here we just create it and check whether it exists
        
        """
        self.assertTrue(self.kHandler.tserver)
        
class TestKuberHandler2(unittest.TestCase):

    _chart = ('https://kubernetes-charts.storage.googleapis.com/', 'mariadb')
    def setUp(self):
        super().setUp()
        from kuber_handler.kuber_handler import KuberHandler
        config_data = {'port' : 8069}
        if self._chart:
            config_data['chart'] = self._chart
        self.kHandler = KuberHandler(config_data)
        
    def test_get_chart(self):
        """ create a docker image according to the gospel of bitnami
        here we just create it and check whether it exists
        
        """
        self.assertFalse(self.kHandler.install())

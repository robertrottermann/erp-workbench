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
        self.kHandler = KuberHandler(MyNamespace(), sites={}, config_data=config_data)

    def XXtest_get_tiller(self):
        """ create a docker image according to the gospel of bitnami
        here we just create it and check whether it exists
        
        """
        self.assertTrue(self.kHandler.tserver)
        
class TestKuberHandlerInstall(unittest.TestCase):
    
    #_chart = 'https://github.com/bitnami/bitnami-docker-odoo'
    _chart = ('https://kubernetes-charts.storage.googleapis.com/', 'mariadb')
    def setUp(self):
        super().setUp()
        from kuber_handler.kuber_handler import KuberHandler
        config_data = {'port' : 8069}
        if self._chart:
            config_data['chart'] = self._chart
        self.kHandler = KuberHandler(xx, config_data)
        
    def xtest_get_chart(self):
        """ create a docker image according to the gospel of bitnami
        here we just create it and check whether it exists
        
        """
        self.assertFalse(self.kHandler.install())

class TestKuberHandler2_fetch(unittest.TestCase):
    
    def do_setUp(self, config_data={}):
        from kuber_handler.kuber_handler import KuberHandlerHelm
        import sites_list
        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'docker'
        args.skip_name = True
        args.quiet = True
        args.name = 'demo_global'
        self.args = args
        self.kHandler = KuberHandlerHelm(args, sites_list.SITES_G, config_data=config_data)
        helm_target = self.kHandler.helm_target
        if helm_target and os.path.exists(helm_target):
            if helm_target.endswith('/helm'):
                shutil.rmtree('%s/*' % helm_target, ignore_errors = True)
        
        
    def do_tearDown(self, result={}):
        helm_target = result.get('helm_target')
        if helm_target and os.path.exists(helm_target):
            if helm_target.endswith('/helm'):
                shutil.rmtree(helm_target, ignore_errors = True)
        
    def test_crete_handler(self):
        """ create a docker image according to the gospel of bitnami
        this test just creates the handler
        """
        self.do_setUp()
        self.assertTrue(self.kHandler)

    def test_fetch_chart(self):
        """ create a docker image according to the gospel of bitnami
        downloads the default chart which is odoo and downloads it
        to the default server which is localhost and checks whether 
        it was downloaded
        the download folder is:
        ~/workbench/demo_global/helm
        """
        self.do_setUp()
        result = self.kHandler.fetch()
        self.assertTrue(result)
        self.assertTrue(glob.glob(result.get('helm_target')))
        self.do_tearDown(result)
        
    def test_fetch_chart_untar(self):
        """ create a docker image according to the gospel of bitnami
        downloads the default chart which is odoo and downloads it
        to the default server which is localhost and checks whether 
        it was downloaded and unpacked
        the download folder is:
        ~/workbench/demo_global/helm/odoo
        """
        self.do_setUp(config_data={'untar' : True})
        result = self.kHandler.fetch()
        self.assertTrue(glob.glob('%s/odoo/' % result.get('helm_target')))
        self.do_tearDown(result)
        

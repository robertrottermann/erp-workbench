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

from .sites_list_killer import SitesListKiller
from .name_space import MyNamespace

from scripts import construct_defaults

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
        from config.handlers import SupportHandler

        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'support'
        args.skip_name = True
        args.quiet = True
        self.args = args
        self.sHandler = SupportHandler(args, {})


    def tearDown(self):
        super().tearDown()
        # remove sites we added
        result = self.sHandler.drop_site()

 
    def test_support_add_drop_site(self):
        """ run the create -c command 
        """
        import sites_list
        r_string = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=4))
        new_name = 'new_site_' + r_string
        print('------->', new_name)
        self.new_name = new_name
        # self.sHandler.site_names = [new_name]
        # self.sHandler.name = new_name
        self.args.add_site = True
        self.args.name = new_name + ':localhost'
        result = self.sHandler.add_site_to_sitelist()
        reload(sites_list.localhost.sites_global)
        from sites_list.localhost.sites_global import SITES_G as S_XX
        self.assertTrue(new_name in list(S_XX.keys()))
        # un-import the sites list
        self.kill_sites_list()

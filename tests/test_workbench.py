import os
import random
import string
import sys
import unittest
from argparse import Namespace
from importlib import reload
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
run it with:
bin/python -m unittest discover tests
"""
class MyNamespace(Namespace):
    # we need a namespace that just ignores unknow options
    def __getattr__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        return None

class TestCreate(unittest.TestCase):

    def setUp(self):
        from config.handlers import SiteCreator
        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'create'
        args.skip_name = True
        args.quiet = True
        self.patcher = patch.dict('os.environ', {'UNIT_TESTING': 'True'})  
        self.mock_foo = self.patcher.start()
        self.args = args
        self.handler = SiteCreator(args, {})
        self.addCleanup(self.patcher.stop) # add this line

    def test_create_create(self):
        """ run the create -c command 
        """
        self.handler.site_names = [list(self.handler.sites.keys())[0]]
        result = self.handler.create_or_update_site()
        self.assertTrue(result)

    def test_create_create_main(self):
        """ run the create -c command 
        using the scripts.create_site main method
        """
        from scripts.create_site import main
        args = self.args
        args.create = True
        args.name = list(self.handler.sites.keys())[0]
        need_names_dic = {}
        main(args, args.subparser_name, need_names_dic)
        pass

    def test_create_ls(self):
        """ run the create -ls command 
        """
        from scripts.utilities import list_sites
        list_sites(self.handler.sites, quiet = True)

    def test_create_ls_main(self):
        """ run the create -ls command 
        """
        from scripts.create_site import main
        args = self.args
        args.list_sites = True
        need_names_dic = {}
        main(args, args.subparser_name, need_names_dic)

    def test_create_parse_args(self):
        """ run the create parse_args command 
        """
        from scripts.create_site import parse_args
        parse_args()

class TestSupportNewSites(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.patcher = patch('sys.exit')
        self.mock_foo = self.patcher.start()
        self.addCleanup(self.patcher.stop) # add this line
        self._get_sites()
        from config.handlers import SupportHandler
        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'support'
        args.skip_name = True
        args.quiet = True
        self.args = args
        self.handler = SupportHandler(args, {})

    def _get_sites(self):
        # old_exit = sys.exit
        # monkey patch sys.exit not 
        # def exit(arg=0):
        #     print('monkey patched sys exit executed')
        # sys.exit = exit
        try:
            # if the sites_list does not exist yet
            # the following import will create it
            # but call exit afterwards, which we have monkeypatched
            from config import sites_list
            self.sites_list_path = os.path.dirname(sites_list.__file__)
            self.SITES_G = sites_list.SITES_G
            self.SITES_L = sites_list.SITES_L
        except:
            # 
            try:
                from config import BASE_INFO
                sys.path.append(os.path.dirname(BASE_INFO.get('sitesinfo_path')))
                import sites_list
                self.sites_list_path = os.path.dirname(sites_list.__file__)
                self.SITES_G = sites_list.SITES_G
                self.SITES_L = sites_list.SITES_L
            except:
                raise
        finally:
            # sys.exit = old_exit
            pass

    def tearDown(self):
        super().tearDown()
        # remove sites we added
        for n, existing in [('sites_global',self.SITES_G)  , ('sites_local', self.SITES_L)]:
            site_list_names = set()
            [site_list_names.add(e['site_list_name'])  for e in list(existing.values())]
            keys = list(existing.keys())
            for site_list_name in site_list_names:
                temp_path = os.path.normpath('%s/%s/%s' % (self.sites_list_path, site_list_name, n))
                files = os.listdir(temp_path)
                for file_name in files:
                    try:
                        fn, fe = file_name.split('.')
                    except:
                        continue
                    if fn != '__init__' and fe == 'py':
                        if fn not in keys:
                            os.unlink('%s/%s' % (temp_path, file_name))
        pass

    def test_support_add_drop_site(self):
        """ run the create -c command 
        """
        import sites_list
        r_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        new_name = 'new_site_' + r_string
        # self.handler.site_names = [new_name]
        # self.handler.name = new_name
        self.args.add_site = True
        self.args.name = new_name + ':localhost'
        result = self.handler.add_site_to_sitelist()
        reload(sites_list.localhost.sites_global)
        from sites_list.localhost.sites_global import SITES_G as S_XX
        self.assertTrue(new_name in list(S_XX.keys()))
        # now delete the site again
        # we have to reload all modules that where tainted by creating the module
        keys = list(sys.modules.keys())
        for key in keys:
            if key.startswith('config') or key.startswith('sites_list'):
                del sys.modules[key]
        import config
        result = self.handler.drop_site()
        self.assertTrue(result)


class TestSupport(unittest.TestCase):

    def setUp(self):
        from config.handlers import SupportHandler
        args = MyNamespace()
        args.name = ''
        args.subparser_name = 'support'
        args.skip_name = True
        args.quiet = True
        self.args = args
        self.handler = SupportHandler(args, {})
   
    def test_editor(self):
        from config import BASE_INFO
        self.assertEqual(BASE_INFO.get('site_editor'), self.handler.editor)

class TestDocker(unittest.TestCase):

    def setUp(self):
        from config.handlers import DockerHandler
        args = MyNamespace()
        args.subparser_name = 'docker'
        args.skip_name = True
        args.quiet = True
        args.docker_create_container = True
        args.name = 'demo_global'
        #self.handler.site_names = ['demo_global']
        self.args = args
        self.handler = DockerHandler(args)
   
    def test_check_and_create_container(self):
        self.handler.check_and_create_container()

    def test_build_image(self):
        self.handler.build_image()

if __name__ == '__main__':
    unittest.main()

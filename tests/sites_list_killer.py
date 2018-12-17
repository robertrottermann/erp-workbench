import unittest
import sys
import os

class SitesListKiller(unittest.TestCase):
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
                sys.path.append(os.path.dirname(
                    BASE_INFO.get('sitesinfo_path')))
                import sites_list
                self.sites_list_path = os.path.dirname(sites_list.__file__)
                self.SITES_G = sites_list.SITES_G
                self.SITES_L = sites_list.SITES_L
            except:
                raise
        finally:
            # sys.exit = old_exit
            pass

    def kill_sites_list(self):
        # we have to reload all modules that where tainted by creating the module
        keys = list(sys.modules.keys())
        for key in keys:
            if key.startswith('config') or key.startswith('sites_list'):
                del sys.modules[key]
        import config

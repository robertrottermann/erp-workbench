import os
from scripts.properties_mixin import PropertiesMixin

#from config import DOCKER_DEFAULTS


class DockerHandlerMixin(PropertiesMixin):
    #----------------------------------------------

    def setup_docker_env(self, site):
        """collect docker info from the site description
        Arguments:
            sites {dict} -- site description
        """
        if isinstance(site, str):
            site = self.sites.get(site)
        #collect_docker_info(self, site)

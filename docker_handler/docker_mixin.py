import os
import docker
from docker import Client
from scripts.properties_mixin import PropertiesMixin

#from config import DOCKER_DEFAULTS


def collect_docker_info(self, site):
    """collect docker info from the site description
    
    Arguments:
        site {dict} -- site description
    """

    # old setting
    if 'docker_hub' in site.keys():
        docker_hub = site.get('docker_hub', {}).get('docker_hub', {})
        docker = site.get('docker', {})
        # docker hub
        if docker_hub.get('user', ''):
            self._docker_hub_name = docker_hub.get('user', '')
        self._docker_hub_pw = docker_hub.get('docker_hub_pw')
        
        # docker
        self._docker_base_image = docker.get('base_image', 'camptocamp/odoo-project:%s-latest' % self.erp_version)
        erp_image_version = docker.get('erp_image_version', docker.get('odoo_image_version'))
        if not erp_image_version:
            erp_image_version = 'no-erp_image_version-defined'
        self._docker_image_version = erp_image_version
        self._docker_container_name = docker.get('container_name', self.site_name)
        self._docker_rpc_port = docker.get(
            'erp_port', docker.get('odoo_port'))
        docker_long_polling_port = docker.get('erp_longpoll', docker.get('odoo_longpoll'))
        if not docker_long_polling_port:
                docker_long_polling_port = int(self.docker_rpc_port) + 10000
        self._docker_long_polling_port = docker_long_polling_port     
        self._docker_external_user_group_id = docker.get('external_user_group_id', '104:107')
        if self.subparser_name == 'docker':
            self._docker_db_admin = self.opts.dockerdbuser or self.docker_defaults.get('dockerdbuser', '')
        else:
            self._docker_db_admin = self.docker_defaults.get('dockerdbuser', '')                                                                                 
    else:
        pass

    # ------------------------------------
    # data not from site_description
    # ------------------------------------
    docker_rpc_user = ''
    if self.subparser_name == 'docker':
        docker_rpc_user = self.opts.drpcuser
    if not docker_rpc_user:
        docker_rpc_user = self.docker_defaults.get('dockerrpcuser', '')
    self._docker_rpc_user = docker_rpc_user
#    self._docker_rpc_user_pw = docker_rpc_user
    docker_rpc_user_pw = ''
    if self.subparser_name == 'docker':
        docker_rpc_user_pw = self.opts.drpcuserpw
    if not docker_rpc_user_pw:
        # no password was provided by an option
        # we try whether we can learn it from the site itself
        docker_rpc_user_pw = self.site.get('docker_erp_admin_pw', '')
        if not docker_rpc_user_pw:
            docker_rpc_user_pw = self.docker_defaults.get('dockerrpcuserpw', '')
    self._docker_rpc_user_pw = docker_rpc_user_pw
    
    db_container_name = ''
    if self.subparser_name == 'docker':
        db_container_name = self.opts.dockerdbname
    if not db_container_name:
        db_container_name = self.docker_defaults.get('dockerdb_container_name', 'db')
    self._docker_db_container_name = db_container_name
    
    # get the dbcontainer
    docker_db_container = ''
    if self.subparser_name == 'docker':
        db_container_list = self.docker_containers(filters = {'name' : self.docker_db_container_name})
        if db_container_list:
            docker_db_container = db_container_list[0]
        else:
            raise Exception('either db container was missing or some other problem') # provide error
        self._docker_db_container = docker_db_container
    
    if self.subparser_name == 'docker':
        # try to read the output of the command docker inspect containername
        # and collect the ip address of its first network interface
        registry = self.docker_registry.get(self.docker_container_name)
        try:
            docker_rpc_host = registry['NetworkSettings']['IPAddress']
        except:
            docker_rpc_host = 'localhost'
        self._docker_rpc_host = docker_rpc_host

    # make sure that within a docker container no "external" paths are used
    self._docker_path_map =  (os.path.expanduser('~/'), '/root/')
    

class DockerHandlerMixin(PropertiesMixin):
    #----------------------------------------------

    def setup_docker_env(self, site):
        """collect docker info from the site description
        
        Arguments:
            sites {dict} -- site description
        """
        if isinstance(site, str):
            site = self.sites.get(site)
        collect_docker_info(self, site)
        
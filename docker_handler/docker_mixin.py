import os
import docker
from docker import Client
#from config import DOCKER_DEFAULTS


def collect_docker_info(self, site):
    """collect docker info from the site description
    
    Arguments:
        sites {dict} -- site description
    """

    # old setting
    if 'docker_hub' in site.keys():
        docker_hub = site['docker_hub']
        docker = site.get('docker', {})
        # docker hub
        self._docker_hub_user = docker_hub.get('hub_name', '')
        self._docker_hub_user_pw = docker_hub.get('docker_hub_pw')
        
        # docker
        self._docker_base_image = docker.get('base_image', 'camptocamp/odoo-project:%s-latest' % self.erp_version),
        erp_image_version = docker.get('erp_image_version', docker.get('odoo_image_version'))
        if not erp_image_version:
            erp_image_version = 'no-erp_image_version-defined'
        self._docker_image_version = erp_image_version
        self._docker_container_name = docker.get('container_name', self.site_name)
        self._docker_rpc_port = docker.get(
            'erp_port', docker.get('odoo_port'))
        docker_long_polling_port = docker.get('erp_longpoll', docker.get('odoo_longpoll'))
        if not docker_long_polling_port:
                long_polling_port = int(self.docker_rpc_port) + 10000
        self._docker_long_polling_port = docker_long_polling_port     
        self._docker_external_user_group_id = docker.get('external_user_group_id', '104:107')
        self._docker_hub_name =  docker.get('docker_hub_name', '')
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

    self._docker_rpc_user_pw = docker_rpc_user
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
            xxx # provide error
            return # either db container was missing or some other problem
        self._docker_db_container = docker_db_container
    
    if self.subparser_name == 'docker':
        registry = self.docker_registry.get(self.container_name)
        try:
            docker_rpc_host = registry['NetworkSettings']['IPAddress']
        except:
            docker_rpc_host = 'localhost'
        self._docker_rpc_host = docker_rpc_host

    # make sure that within a docker container no "external" paths are used
    self._docker_path_map =  (os.path.expanduser('~/'), '/root/')
    


class DockerHandlerMixin(object):
    docker_registry = None

    def setup_docker_env(self, site):
        """collect docker info from the site description
        
        Arguments:
            sites {dict} -- site description
        """
        if isinstance(site, str):
            site = self.sites.get(site)
        collect_docker_info(self, site)

    # ----------------------
    # get the sites container
    # ----------------------
    _docker_db_container = ''
    @property
    def docker_db_container(self):
        return _docker_db_container
        
    @property
    def docker_db_ip(self):
        # the ip address to access the db container
        return self.db_container['NetworkSettings']['Networks']['bridge']['IPAddress']
        
    _docker_rpc_host = 'localhost'
    @property
    def docker_rpc_host(self):
        return self._docker_rpc_host
          
    _docker_path_map = ''       
    @property
    def docker_path_map(self):
        return self._docker_path_map
          
    # --------------------------------------------------
    # get the credential to log into the sites container
    # --------------------------------------------------
    _docker_rpc_user = ''
    @property
    def docker_rpc_user(self):
        return self._docker_rpc_user
        
    _docker_rpc_user_pw = ''    
    @property
    def docker_rpc_user_pw(self):
        return self._docker_rpc_user_pw
        
    _db_container_name = ''    
    @property
    def docker_db_container_name(self):
        return self._docker_db_container_name
      
    # --------------------------------------------------
    # get the credential to log into the db container
    # --------------------------------------------------
    # by default the odoo docker user db is 'odoo'
    _docker_db_admin = ''
    @property
    def docker_db_admin(self):
        return self._docker_db_admin

    @property
    def docker_db_admin_pw(self):
        # by default the odoo docker db user's pw is 'odoo'
        #self.docker_db_admin_pw = DOCKER_DEFAULTS['dockerdbpw']
        return self.opts.dockerdbpw or self.docker_defaults.get('dockerdbpw', '')

    _docker_registry = {}
    @property
    def docker_registry(self):
        return self._docker_registry

    @property
    def docker_containers(self):
        if self.subparser_name == 'docker':
            # update the docker registry so we get info about the db_container_name 
            self.update_container_info()

            # get the list of containers
            return self.docker_client.containers
        return {}
    
    _cli = {}
    @property
    def docker_client(self):
        if not self._cli:
            from docker import Client
            cli = Client(base_url=self.url)
            self._cli = cli
        return self._cli

    _docker_container_name = ''
    @property
    def docker_container_name(self):
        return self._docker_container_name

    _docker_image_version = ''
    @property
    def docker_image_version(self):
        return self._docker_image_version
    erp_image_version = docker_image_version
        
    @property
    def db_container_ip(self):
        if self.parsername == 'docker':
            return self.db_ip
        # does it make sense to return a default at all??
        return 'localhost'
    
    @property
    def docker_default_port(self):
        # must be defined in the parent class
        return self.project_defaults.get('docker_default_port', 9000)

    #@property
    #def docker_info(self):
        #return self.site.get('docker', {})
    
    _docker_base_image = ''
    @property
    def docker_base_image(self):
        return self._docker_base_image 

    _docker_hub_name = ''
    @property
    def docker_hub_name(self):
        return self._docker_hub_name 
        
    _docker_hub_user = ''
    @property
    def docker_hub_user(self):
        return self._docker_hub_user 
        
    _docker_external_user_group_id = ''
    @property
    def docker_external_user_group_id(self):
        return self._docker_external_user_group_id 
        
    _docker_hub_user_pw = ''
    @property
    def docker_hub_user_pw(self):
        return self._docker_hub_user_pw 
        
    _docker_rpc_port = ''
    @property
    def docker_rpc_port(self):
        return self._docker_rpc_port 

    _docker_long_polling_port = ''
    @property
    def docker_long_polling_port(self):
        return self._docker_long_polling_port

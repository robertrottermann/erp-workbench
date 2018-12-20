import docker
from docker import Client
from config import DOCKER_DEFAULTS


def collect_docker_info(self, site):
    """collect docker info from the site description
    Store the data in a instance variable _docker_info
    
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
    docker_rpc_user_pw = ''
    if self.subparser_name == 'docker':
        docker_rpc_user_pw = self.opts.drpcuserpw
    if not docker_rpc_user_pw:
        # no password was provided by an option
        # we try whether we can learn it from the site itself
        docker_rpc_user_pw = self.site.erp_admin_pw
        if not docker_rpc_user_pw:
            docker_rpc_user_pw = DOCKER_DEFAULTS['dockerrpcuserpw']
    self._docker_rpc_user_pw = docker_rpc_user_pw
    
    docker_info = self.docker_info  # self.site['docker']
    if self.subparser_name == 'docker':
        db_container_name = self.opts.dockerdbname
    if not db_container_name:
        db_container_name = docker_info.get('db_container_name', DOCKER_DEFAULTS['dockerdb_container_name'])
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

@property
def docker_postgres_port(self):
    # the db container allows access to the postgres server running within
    # trough a port that has been defined when the container has been created
    return BASE_INFO.get('docker_postgres_port')
    # todo should we check whether the postgres port is accessible??
    
@property
def docker_rpc_host(self):
    registry = self.docker_registry.get(self.container_name)
    try:
        docker_rpc_host = registry['NetworkSettings']['IPAddress']
    except:
        docker_rpc_host = 'localhost'
    return docker_rpc_host
        
@property
def docker_path_map(self):
    # make sure that within a docker container no "external" paths are used
    return (os.path.expanduser('~/'), '/root/')
      
# --------------------------------------------------
# get the credential to log into the sites container
# --------------------------------------------------
@property
def docker_rpc_user(self):
    docker_rpc_user = self.opts.drpcuser
    if not docker_rpc_user:
        docker_rpc_user = DOCKER_DEFAULTS['dockerrpcuser']
    return docker_rpc_user
    
_docker_rpc_user_pw = ''    
@property
def docker_rpc_user_pw(self):
    return self._docker_rpc_user_pw
    
_db_container_name = ''    
@property
def docker_db_container_name(self):
    return self._docker_db_container_name
  

class DockerHandlerMixin(object):
    docker_registry = None

    def setup_docker_env(self, site):
        """collect docker info from the site description
        Store the data in a instance variable _docker_info
        
        Arguments:
            sites {dict} -- site description
        """
        if isinstance(site, str):
            site = self.sites.get(site)
        self._docker_info = collect_docker_info(self, site)

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
        return self.opts.dockerdbpw or DOCKER_DEFAULTS['dockerdbpw']

    _docker_registry = {}
    @property
    def docker_registry(self):
        return self._docker_registry
    
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
    def docker_postgres_port(self):
        # why self... ?? and not like the other props
        if self.parsername == 'docker':
            return self.postgres_port
        # does it make sense to return a default at all??
        return '8069'

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

from config import BASE_PATH, BASE_INFO, PROJECT_DEFAULTS, DOCKER_DEFAULTS, FOLDERNAMES, ACT_USER, REMOTE_SERVERS
class PropertiesMixin(object):
    @property
    def docker_db_user(self):
        return self.login_info.get('docker_db_user') or self.opts.db_user

    @property
    def db_name(self):
        return self.site.get('db_name', self.site_name)

    @property
    def db_password(self):
        if self.parsername == 'docker':
            return self.docker_db_admin_pw
        return self.login_info.get('db_password')

    @property
    def db_user(self):
        if self.parsername == 'docker':
            return self.docker_db_admin
        return self.login_info.get('db_user') or self.opts.__dict__.get('db_user', self.base_info['db_user'])

    @property
    def db_host(self):
        if self.parsername == 'docker':
            return self.docker_db_ip
        return self._db_host

    @property
    def postgres_port(self):
        return self.base_info.get('postgres_port', 5342)

    # ----------------------
    # get the sites container
    # ----------------------
    _docker_db_container = ''
    @property
    def docker_db_container(self):
        self._cp
        return self._docker_db_container

    @property
    def docker_db_ip(self):
        self._cp
        # the ip address to access the db container
        return self.docker_db_container['NetworkSettings']['Networks']['bridge']['IPAddress']

    _docker_rpc_host = 'localhost'
    @property
    def docker_rpc_host(self):
        self._cp
        return self._docker_rpc_host

    _docker_path_map = ''
    @property
    def docker_path_map(self):
        self._cp
        return self._docker_path_map

    # --------------------------------------------------
    # get the credential to log into the sites container
    # --------------------------------------------------
    _docker_rpc_user = ''

    @property
    def docker_rpc_user(self):
        self._cp
        return self._docker_rpc_user

    _docker_rpc_user_pw = ''

    @property
    def docker_rpc_user_pw(self):
        self._cp
        return self._docker_rpc_user_pw

    _db_container_name = ''

    @property
    def docker_db_container_name(self):
        self._cp
        return self._docker_db_container_name

    # --------------------------------------------------
    # get the credential to log into the db container
    # --------------------------------------------------
    # by default the odoo docker user db is 'odoo'
    _docker_db_admin = ''

    @property
    def docker_db_admin(self):
        self._cp
        return self._docker_db_admin

    @property
    def docker_db_admin_pw(self):
        # by default the odoo docker db user's pw is 'odoo'
        #self.docker_db_admin_pw = DOCKER_DEFAULTS['dockerdbpw']
        return self.opts.dockerdbpw or self.docker_defaults.get('dockerdbpw', '')

    _docker_registry = {}

    @property
    def docker_registry(self):
        self._cp
        return self._docker_registry

    @property
    def docker_containers(self):
        self._cp
        if self.subparser_name == 'docker':
            # update the docker registry so we get info about the db_container_name
            self.update_container_info()

            # get the list of containers
            return self.docker_client.containers
        return {}

    _cli = {}

    @property
    def docker_client(self):
        self._cp
        if not self._cli:
            from docker import Client
            url = 'unix://var/run/docker.sock'
            cli = Client(base_url=url)
            self._cli = cli
        return self._cli

    _docker_container_name = ''
    @property
    def docker_container_name(self):
        self._cp
        return self._docker_container_name

    _docker_image_version = ''
    @property
    def docker_image_version(self):
        self._cp
        return self._docker_image_version
    erp_image_version = docker_image_version

    @property
    def db_container_ip(self):
        self._cp
        if self.parsername == 'docker':
            return self.db_ip
        # does it make sense to return a default at all??
        return 'localhost'

    @property
    def docker_default_port(self):
        self._cp
        # must be defined in the parent class
        return self.project_defaults.get('docker_default_port', 9000)

    #@property
    #def docker_info(self):
        #return self.site.get('docker', {})

    _docker_base_image = ''
    @property
    def docker_base_image(self):
        self._cp
        return self._docker_base_image

    _docker_hub_name = ''
    @property
    def docker_hub_name(self):
        self._cp
        if not self._docker_hub_name:
            return self.docker_defaults.get('docker_hub_name')
        return self._docker_hub_name

    # _docker_hub_user = ''
    # @property
    # def docker_hub_user(self):
    #     return self._docker_hub_user

    _docker_external_user_group_id = ''
    @property
    def docker_external_user_group_id(self):
        self._cp
        return self._docker_external_user_group_id

    # _docker_hub_user_pw = ''
    # @property
    # def docker_hub_user_pw(self):
    #     return self._docker_hub_user_pw

    _docker_rpc_port = ''
    @property
    def docker_rpc_port(self):
        self._cp
        return self._docker_rpc_port

    _docker_long_polling_port = ''
    @property
    def docker_long_polling_port(self):
        self._cp
        return self._docker_long_polling_port

    # we must have parsed the site description at least once
    _site_parsed = False
    _docker_parsed = False
    @property
    def _check_parsed(self):
        if not self._site_parsed:
            self._site_parsed = True
            self._parse_site(self.site)
        if self.subparser_name == 'docker' and not self._docker_parsed:
            self._docker_parsed = True
            self.setup_docker_env(self.site)
            
    _cp = _check_parsed

    _erp_nightly = ''
    @property
    def erp_nightly(self):
        self._cp
        return self._erp_nightly

    _erp_provider = ''
    @property
    def erp_provider(self):
        self._cp
        return self._erp_provider

    _erp_version = ''
    @property
    def erp_version(self):
        self._cp
        return self._erp_version

    _erp_minor = ''

    @property
    def erp_minor(self):
        self._cp
        return self._erp_minor

    _rpc_host = ''
    @property
    def rpc_host(self):
        return self._rpc_host

    _rpc_port = ''
    @property
    def rpc_port(self):
        if self.parsername == 'docker':
            return self.docker_rpc_port
        return self._rpc_port

    @property
    def rpc_user(self):
        if self.parsername == 'docker':
            return self.docker_rpc_user
        return self.login_info.get('rpc_user', '')

    @property
    def rpc_pw(self):
        if self.parsername == 'docker':
            return self.docker_rpc_user_pw
        return self.login_info.get('rpc_pw', '')
   # -----------------------------------------------------
    # property declarations
    # -----------------------------------------------------

    # -----------------------------------------------------
    # base data read from the yaml files

    @property
    def base_info(self):
        return BASE_INFO

    @property
    def docker_defaults(self):
        return DOCKER_DEFAULTS

    @property
    def project_defaults(self):
        return PROJECT_DEFAULTS

    @property
    def foldernames(self):
        return FOLDERNAMES

    # -----------------------------------------------------
    # properties from remote block

    _remote_url = ''

    @property
    def remote_url(self):
        return self._remote_url

    _remote_data_path = ''

    @property
    def remote_data_path(self):
        return self._remote_data_path

    _remote_user = ''

    @property
    def remote_user(self):
        return self._remote_user

    _remote_sites_home = ''

    @property
    def remote_sites_home(self):
        return self._remote_sites_home

    _redirect_email_to = ''

    @property
    def redirect_email_to(self):
        return self._redirect_email_to

    # -----------------------------------------------------
    # base data read from the yaml files

    _default_values = {}

    @property
    def default_values(self):
        return self._default_values

    _login_info = {}

    @property
    def login_info(self):
        return self._login_info

    @property
    def projectname(self):
        return self.site.get('projectname', self.site.get('site_name', ''))

    @property
    def project_type(self):
        return self.project_defaults.get('erp_provider', 'odoo')
    erp_provider = project_type

    @property
    def is_local(self):
        return self.default_values.get('is_local')

    @property
    def erp_server_data_path(self):
        return self.base_info['erp_server_data_path']
    data_path = erp_server_data_path

    @property
    def sitesinfo_path(self):
        return self.base_info['sitesinfo_path']

    _sites_local = {}

    @property
    def sites_local(self):
        return self._sites_local

    _sites = {}

    @property
    def sites(self):
        return self._sites

    @property
    def siteinfos(self):
        return self.base_info.get('siteinfos')

    @property
    def site(self, site_name=''):
        """return a dictonary with a site description
        
        Keyword Arguments:
            site_name {str} -- name of the site to loock up (default: {''})
        
        Returns:
            dict -- dictionary with the site description
        """

        if site_name:
            name = site_name
        else:
            name = self.site_name
        if name:
            return self.sites.get(name, {})
        else:
            return {}

    @property
    def site_name(self):
        return self.site_names and self.site_names[0] or ''

    @site_name.setter
    def site_name(self, v):
        self.site_names = [v]

    @property
    def sites_home(self):
        return BASE_PATH

    @property
    def use_postgres_version(self):
        return self.docker_defaults.get('use_postgres_version')

    @property
    def version(self):
        """return the value of the version key of the site description
        
        Returns:
            string -- version of the erp system
        """

        if self.site:
            return self.erp_version

    #@property
    #def minor(self):
        #"""minor version of the running erp

        #Returns:
            #string -- the minor version like '.0'
        #"""

        #if self.site:
            #return self.site.get('erp_minor', self.default_values['erp_minor'])

    #@property
    #def nightly(self):
        #"""what directory on the nightly server to use

        #Returns:
            #string -- 'directory name'
            #example -- 'master'
        #"""

        #if self.site:
            #return self.site.get('erp_nightly', '%s%s' % (self.version, self.erp_minor))

    # remote servers are construced from
    # config/servers.yaml into dictonary entries like:
    # '88.198.51.174': {'local_user_email': 'robert@redcor.ch',
    #                 'remote_data_path': '/root/odoo_instances',
    #                 'remote_pw': '', # the password ist patched in at runtime
    #                 'remote_user': 'root',
    #                 'server_ip': '88.198.51.174',
    #                 'server_name': 'lisa'}}
    #
    # the remote server stanza from a site description
    # 'remote_server': {
    #     'remote_url': 'localhost',  # please adapt
    #     'remote_data_path': '/root/erp_workbench',
    #     'remote_user': 'root',
    #     # where is sites home on the remote server for non root users
    #     'remote_sites_home': '/home/robert/erp_workbench',
    #     'redirect_emil_to': '',  # redirect all outgoing mail to this account
    #     # needs red_override_email_recipients installed
    # },

    @property
    def remote_servers(self):
        return REMOTE_SERVERS

    @property
    def user(self):
        return ACT_USER

    # @property
    # def remote_url(self):
    #     # remote_url is the key in the list of remote servers
    #     return self.remote_servers.get(
    #         # get the one we find in the remote_server stanza
    #         # of the running site description
    #         self.site.get('remote_server', {}).get(
    #             # from this stanza get the url
    #             # that is used as key into the list of retome servers
    #             'remote_url', ''))

    @property
    def remote_user(self):
        # from the list of remote servers
        return self.remote_servers.get(
            # find as what user we access that remote server
            self.remote_url, {}).get('remote_user', '')

    @property
    def remote_user_pw(self):
        # from the list of remote servers
        return self.remote_servers.get(
            # and finally find what pw to use on the remote server
            # this pw is patched in at runtime
            self.remote_url, {}).get('remote_pw', '')

    @property
    def remote_data_path(self):
        # refacture the following as the above props
        # we first check whether config/localdata.py has an remote path set.
        remote_dic = self.remote_server
        remote_data_path = remote_dic.get(
            'remote_data_path', remote_dic.get('remote_path'))
        if remote_data_path:
            return remote_data_path
        # then we check whether config/localdata.py has an remote path set.
        remote_data_path = self.remote_servers.get(
            # and finally find what pw to use on the remote server
            # this pw is patched in at runtime
            self.remote_url, {}).get('remote_data_path', '')
        return remote_data_path

    # @property
    # def remote_user_data_path(self):
    #     remote_dic = self.remote_servers.get(self.remote_url, {})
    #     remote_data_path = remote_dic.get(
    #         'remote_data_path', remote_dic.get('remote_path', self.remote_sites_home))
    #     return remote_data_path

    # was an alias to remote_url
    @property
    def remote_server(self):
        return self.site.get('remote_server', {})

    @property
    def remote_sites_home(self):
        return self.site.get('sites_home', '/root/erp_workbench')

    @property
    def remote_url(self):
        return self.remote_server.get('remote_url', '')

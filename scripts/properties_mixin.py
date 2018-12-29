from config import BASE_PATH, BASE_INFO, PROJECT_DEFAULTS, DOCKER_DEFAULTS, FOLDERNAMES, ACT_USER, REMOTE_SERVERS

class PropertiesMixin(object):
    _login_info = {}

    # login_info
    # dict with values about local and remote login credentials
    # {'db_password': 'admin',
    #  'db_user': 'robert',
    #  'remote_db_password': 'admin',
    #  'remote_db_user': 'robert',
    #  'remote_docker_db_pw': None,
    #  'remote_docker_db_user': None,
    #  'remote_user': 'robert',
    #  'remote_user_pw': '',
    #  'rpc_pw': 'admin',
    #  'rpc_user': 'robert',
    #  'user': 'robert'}    
    # @property
    # def login_info(self):
    #     return self._login_info

    # -------------------------------------------------------------
    # values read from the yaml files
    # -------------------------------------------------------------

    @property
    def base_info(self):
        return BASE_INFO

    @property
    def docker_defaults(self):
        return DOCKER_DEFAULTS

    @property
    def foldernames(self):
        return FOLDERNAMES

    @property
    def project_defaults(self):
        return PROJECT_DEFAULTS

    @property
    def remote_servers(self):
        return REMOTE_SERVERS

    # ----------
    # db
    # ----------
    @property
    def db_host(self):
        if self.subparser_name == 'docker':
            return self.docker_db_ip
        return self._db_host

    @property
    def postgres_port(self):
        return self.base_info.get('postgres_port', 5342)

    @property
    def db_name(self):
        return self.site.get('db_name', self.site_name)

    # -------------------------------------------------------------
    # credentials
    # -------------------------------------------------------------

    # odoo main password
    @property
    def erp_admin_pw(self):
        return self._erp_admin_pw  # by set_passwords

    # --------------------------------------------------
    # get the credential to log into the db container
    # --------------------------------------------------
    # by default the odoo docker user db is 'odoo'

    # where is it ??

    # ----------
    # local
    # ----------
    @property
    def db_user(self):
        if self.subparser_name == 'docker':
            return self.docker_db_user
        return self._db_user

    @property
    def db_user_pw(self):
        if self.subparser_name == 'docker':
            return self.docker_db_user_pw
        return self._db_user_pw
    db_password = db_user_pw

    @property
    def rpc_user(self):
        if self.subparser_name == 'docker':
            return self.docker_rpc_user
        return self._rpc_user

    @property
    def rpc_user_pw(self):
        if self.subparser_name == 'docker':
            return self.docker_rpc_user_pw
        return self._rpc_user_pw

    # ----------
    # docker
    # ----------
    @property
    def docker_db_user(self):
        return self._db_user

    # by default the odoo docker db user's pw is 'odoo'
    @property
    def docker_db_user_pw(self):
        return self._docker_db_user_pw

    # --------------------------------------------------
    # get the credential to log into the sites container
    # --------------------------------------------------
    @property
    def docker_rpc_user(self):
        self._cp
        return self._docker_rpc_user

    @property
    def docker_rpc_user_pw(self):
        self._cp
        return self._docker_rpc_user_pw

    # ----------------------
    # get the sites container
    # ----------------------
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

    _db_container_name = ''

    @property
    def docker_db_container_name(self):
        self._cp
        return self._docker_db_container_name

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
        if self.subparser_name == 'docker':
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
    # _site_parsed = False
    # _docker_parsed = False
    # _pw_parsed = False
    # _addpath_collected = False
    # _sites_flattened = False
    # _remote_info_collected = False
    # _defaults_constructed = False
    # _login_info_created = False
    _all_done = False
    @property
    def _check_parsed(self):
        if not self._all_done:
            self._all_done = True
            self.prepare_properties(self.site)
        # _not_yet = False
        # if self._all_done:
        #     # make sure that construct_defualts is the last, so it can use all values
        #     if not self._defaults_constructed:
        #         self._defaults_constructed = True
        #         self.construct_defaults(self.site_name)
        #     return
        # if not self._sites_flattened:
        #     self._sites_flattened = True
        #     from site_desc_handler.sdesc_utilities import flatten_sites
        #     flatten_sites(self.sites)
        # if not self._remote_info_collected:
        #     self._remote_info_collected = True
        #     from site_desc_handler.handle_remote_data import collect_remote_info          
        #     collect_remote_info(self, self.site)
        # if not self._docker_parsed:
        #     if hasattr(self, 'setup_docker_env'):
        #         self._docker_parsed = True
        #         self.setup_docker_env(self.site)
        #     else:
        #         _not_yet = True
        # if not self._pw_parsed:
        #     if hasattr(self, '_merge_pw'):
        #         self._pw_parsed = True
        #         self._merge_pw(self.site)
        #     else:
        #         _not_yet = True
        # if not self._site_parsed:
        #     if hasattr(self, '_parse_site'):
        #         self._site_parsed = True
        #         self._parse_site(self.site)
        #     else:
        #         _not_yet = True
        # if not self._login_info_created:
        #     if hasattr(self, '_create_login_info'):
        #         self._login_info_created = True            
        #         self._create_login_info(self.login_info)
        #     else:
        #         _not_yet = True
        # if not self._addpath_collected:
        #     try:
        #         from scripts.utilities import collect_addon_paths
        #         self._addpath_collected = True
        #         collect_addon_paths(self)
        #     except ImportError:
        #         _not_yet = True
        # if not _not_yet:
        #     self._all_done = True
        
    _cp = _check_parsed

    @_check_parsed.setter
    def set_check_parsed(self, value):
        self._check_parsed = value

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
        if self.subparser_name == 'docker':
            return self.docker_rpc_port
        return self._rpc_port

    _docker_local_user_id = ''
    @property
    def docker_local_user_id(self):
        self._cp
        self._docker_local_user_id = self.docker_defaults.get('docker_local_user_id', 999)
        return self._docker_local_user_id

    _docker_db_maxcon = ''
    @property
    def docker_db_maxcon(self):
        self._cp
        self._docker_db_maxcon = self.docker_defaults.get('docker_db_maxcon', 64)
        return self._docker_db_maxcon

    _docker_limit_memory_hard = ''
    @property
    def docker_limit_memory_hard(self):
        self._cp
        self._docker_limit_memory_hard = self.docker_defaults.get('docker_limit_memory_hard', 2684354560)
        return self._docker_limit_memory_hard

    _docker_limit_memory_soft = ''
    @property
    def docker_limit_memory_soft(self):
        self._cp
        self._docker_limit_memory_soft = self.docker_defaults.get('docker_limit_memory_soft', 2147483648)
        return self._docker_limit_memory_soft

    _docker_limit_request = ''
    @property
    def docker_limit_request(self):
        self._cp
        self._docker_limit_request = self.docker_defaults.get('docker_limit_request', 8192)
        return self._docker_limit_request

    _docker_limit_time_cpu = ''
    @property
    def docker_limit_time_cpu(self):
        self._cp
        self._docker_limit_time_cpu = self.docker_defaults.get('docker_limit_time_cpu', 60)
        return self._docker_limit_time_cpu

    _docker_limit_time_real = ''
    @property
    def docker_limit_time_real(self):
        self._cp
        self._docker_limit_time_real = self.docker_defaults.get('docker_limit_time_real', 120)
        return self._docker_limit_time_real

    _docker_limit_time_real_cron = ''
    @property
    def docker_limit_time_real_cron(self):
        self._cp
        self._docker_limit_time_real_cron = self.docker_defaults.get('docker_limit_time_real_cron', 120)
        return self._docker_limit_time_real_cron

    _docker_log_handler = ''
    @property
    def docker_log_handler(self):
        self._cp
        self._docker_log_handler = self.docker_defaults.get('docker_log_handler', ':INFO')
        return self._docker_log_handler

    _docker_log_level = ''
    @property
    def docker_log_level(self):
        self._cp
        self._docker_log_level = self.docker_defaults.get('docker_log_level', 'info')
        return self._docker_log_level

    _docker_logfile = ''
    @property
    def docker_logfile(self):
        self._cp
        self._docker_logfile = self.docker_defaults.get('docker_logfile', None)
        return self._docker_logfile

    _docker_syslog = ''
    @property
    def docker_syslog(self):
        self._cp
        self._docker_syslog = self.docker_defaults.get('docker_syslog', False)
        return self._docker_syslog

    _docker_logrotate = ''
    @property
    def docker_logrotate(self):
        self._cp
        self._docker_logrotate = self.docker_defaults.get('docker_logrotate', False)
        return self._docker_logrotate

    _docker_log_db = ''
    @property
    def docker_log_db(self):
        self._cp
        self._docker_log_db = self.docker_defaults.get('docker_log_db', False)
        return self._docker_log_db

    _docker_max_cron_threads = ''
    @property
    def docker_max_cron_threads(self):
        self._cp
        self._docker_max_cron_threads = self.docker_defaults.get('docker_max_cron_threads', 2)
        return self._docker_max_cron_threads

    _docker_workers = ''
    @property
    def docker_workers(self):
        self._cp
        self._docker_workers = self.docker_defaults.get('docker_workers', 4)
        return self._docker_workers

    _docker_running_env = ''
    @property
    def docker_running_env(self):
        self._cp
        self._docker_running_env = self.docker_defaults.get('docker_running_env', 'production')
        return self._docker_running_env

    _docker_without_demo = True
    @property
    def docker_without_demo(self):
        self._cp
        self._docker_without_demo = self.docker_defaults.get('docker_without_demo', True)
        return self._docker_without_demo

    _docker_server_wide_modules = ''
    @property
    def docker_server_wide_modules(self):
        self._cp
        self._docker_server_wide_modules = self.docker_defaults.get('docker_server_wide_modules', '')
        return self._docker_server_wide_modules

    _docker_db_sslmode = ''
    @property
    def docker_db_sslmode(self):        
        self._cp
        self._docker_db_sslmode = self.docker_defaults.get('docker_db_sslmode', False)
        return self._docker_db_sslmode

    _docker_list_db = False
    @property
    def docker_list_db(self):        
        self._cp
        self._docker_list_db = self.docker_defaults.get('docker_list_db', False)
        return self._docker_list_db

   # -----------------------------------------------------
    # property declarations
    # -----------------------------------------------------

    # -----------------------------------------------------
    # properties from remote block

    @property
    def http_server(self):
        # what http_server is in use on the remote server
        # either nginx or apache
        # from the list of remote servers
        return self.remote_servers.get(
            # find as what user we access that remote server
            self.remote_server_ip, {}).get('http_server', '')

    @property
    def http_server_fs_path(self):
        # from the list of remote servers
        return self.remote_servers.get(
            # find as what user we access that remote server
            self.remote_server_ip, {}).get('http_server_fs_path', '')
        
    _remote_http_url = ''

    @property
    def remote_http_url(self):
        return self._remote_http_url

    _remote_server_ip = ''

    @property
    def remote_server_ip(self):
        return self._remote_server_ip

    # _remote_user = ''

    @property
    def remote_user(self):
        # from the list of remote servers
        return self.remote_servers.get(
            # find as what user we access that remote server
            self.remote_server_ip, {}).get('remote_user', '')

    _remote_user_pw = ''

    @property
    def remote_user_pw(self):
        if not self._remote_user_pw:
            # from the list of remote servers
            _remote_user_pw =self.remote_servers.get(
                # and finally find what pw to use on the remote server
                # this pw is patched in at runtime
                self.remote_server_ip, {}).get('remote_pw', '')
        return self._remote_user_pw

    _remote_sites_home = ''

    # remote_sites_home
    # remote aequivalent to self.sites_home
    @property
    def remote_sites_home(self):
        if not self._remote_sites_home:
            # this info we used to get from the site description
            # but is better placed in the servers yaml
            # so what we do is get the servers ip address from the site description
            # and use it, to get the server-description from the servers.yaml
            self._remote_sites_home = self.remote_servers.get(self.remote_server_ip, {}).get(
                'remote_data_path', '-- remote sites home unknown --')
        return self._remote_sites_home
 
    # both of the following is used 
    # but it does not make sense to distinguish them on remote servers
    remote_data_path = remote_sites_home
    _redirect_email_to = ''

    # redirect_email_to
    # is used in testing environment, together with red_override_email_recipients
    @property
    def redirect_email_to(self):
        return self._redirect_email_to

    # -----------------------------------------------------
    # base data read from the yaml files

    @property
    def default_values(self):
        return self._default_values

    # projectname
    # is used to construct the foldernames of the project
    # it is set to the value of the site_name
    @property
    def projectname(self):
        return self.site.get('projectname', self.site.get('site_name', ''))

    # project_type
    # tells whether site is of type odoo or flectra
    @property
    def project_type(self):
        return self.project_defaults.get('erp_provider', 'odoo')
    erp_provider = project_type

    # sites_home is constructed of the fs path of the config/__init__.py file
    # it points to the erp-workbench installation folder
    @property
    def sites_home(self):
        return BASE_PATH

    # erp_server_data_path
    # points to the rp-workbench home directory
    # should be identical to sites_home
    @property
    def erp_server_data_path(self):
        return self.base_info['erp_server_data_path']
    data_path = erp_server_data_path

    # sitesinfo_path
    # path to the structure where the sites descriptions are kept
    @property
    def sitesinfo_path(self):
        return self.base_info['sitesinfo_path']

    _sites = {}
    # sites is a dict of all sites-descriptions known
    @property
    def sites(self):
        return self._sites

    _sites_local = {}
    # sites_local is a dict of all sites-descriptions with the local flag set
    @property
    def sites_local(self):
        return self._sites_local

    # is_local
    # flags a site description to be used only locally
    @property
    def is_local(self):
        return self.default_values.get('is_local')

    # siteinfos is the list of folders withing the sites_list structure
    # it is constructed from config/config/yaml: siteinfos
    # it defaults to localhost
    @property
    def siteinfos(self):
        return self.base_info.get('siteinfos')

    # site is the actively "running" site on which we opperate
    # it is constructed by looking up self.site_name from the self.sites dict
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

    # site_name is the name of the site we are acting on
    # its value has been passed as a command line option when executing a wp command
    @property
    def site_name(self):
        if self.sites:
            return self.site_names and self.site_names[0] or ''
        return ''

    @site_name.setter
    def site_name(self, v):
        self.site_names = [v]

    # site_data_dir
    # where the data files for this site are to be found
    @property
    def site_data_dir(self):
        self._cp
        return self.default_values['data_dir']
      
    @property  
    def site_addons_path(self):
        self._cp
        return self._site_addons_path
        
    @property
    def use_postgres_version(self):
        return self.docker_defaults.get('use_postgres_version')
    
    #@property
    #def version(self):
        #"""return the value of the version key of the site description
        
        #Returns:
            #string -- version of the erp system
        #"""

        #if self.site:
            #return self.erp_version

    @property
    def user(self):
        return ACT_USER

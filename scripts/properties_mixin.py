# BASE_PATH is the home directory of erp_workbench
# BASE_INFO is a dictoary with all the info read from the config yaml file found in config
# PROJECT_DEFAULTS, DOCKER_DEFAULTS info found in the respective yal files
#
import os
from config import (
    BASE_PATH,
    BASE_INFO,
    PROJECT_DEFAULTS,
    DOCKER_DEFAULTS,
    DOCKER_IMAGE,
    BITNAMI_DEFAULTS,
    BITNAMI_CHART,
    FOLDERNAMES,
    ACT_USER,
    REMOTE_SERVERS,
    MARKER,
)
import socket
from scripts.bcolors import bcolors
from scripts.construct_defaults import read_yaml_file


class PropertiesMixin(object):
    _login_info = {}

    # -------------------------------------------------------------
    # Bootstrap reading of the values from its divers sources
    # most of the variables are in an undefined setting until
    # they are bootstraped.
    # who does the bootstrapping depends on what part of erp-workbench
    # is involved.
    # many properties call _cp as first step to ensure bootstrapping
    # -------------------------------------------------------------
    # we must have parsed the site description at least once
    _all_done = False

    @property
    def _check_parsed(self):
        if not self._all_done:
            self._all_done = True
            self.prepare_properties(self.site)

    _cp = _check_parsed

    @_check_parsed.setter
    def set_check_parsed(self, value):
        self._check_parsed = value

    def reset_values(self):
        self._all_done = False
        self._default_values = {}

    # -------------------------------------------------------------
    # Some parts of erp-workbench are constructed using templates
    # these templates carry placeholders for values that are
    # provisioned by the default_values
    # -------------------------------------------------------------

    _default_values = {}

    @property
    def default_values(self):
        if not self._default_values:
            self._cp
            self.construct_defaults()
        return self._default_values

    # -------------------------------------------------------------
    # values read from the yaml files
    # -------------------------------------------------------------

    def _pep_up(self, value_dic):
        # some of the values might have yet placeholders
        for k, v in value_dic.items():
            try:
                value_dic[k] = v % self.default_values
            except:
                pass

    @property
    def base_info(self):
        return BASE_INFO

    _bitnamy_defaults = ""

    @property
    def bitnamy_defaults(self):
        if not self._bitnamy_defaults:
            self._pep_up(BITNAMI_DEFAULTS)
            self._bitnamy_defaults = BITNAMI_DEFAULTS
        return self._bitnamy_defaults

    @property
    def bitnami_chart(self):
        return BITNAMI_CHART

    @property
    def docker_defaults(self):
        return DOCKER_DEFAULTS

    @property
    def docker_image(self):
        return DOCKER_IMAGE

    @property
    def foldernames(self):
        return FOLDERNAMES

    @property
    def project_defaults(self):
        return PROJECT_DEFAULTS

    @property
    def remote_servers(self):
        return REMOTE_SERVERS

    # -------------------------------------------------------------
    # Projects
    # A projects describes an erp site
    # -------------------------------------------------------------

    # projectname
    # used as the name of the project, the site and the docker container
    # that will be generated
    @property
    def projectname(self):
        return self.site.get(
            "projectname",
            self.site.get(
                "site_name", self.site.get("server_name", self.site.get("db_name", ""))
            ),
        )

    # theoretically the erp workbench can handle other erp systems
    # than odoo
    # the value of erp_provider tells what the running site is based on
    _erp_provider = "odoo"

    @property
    def erp_provider(self):
        self._cp
        return self._erp_provider

    # -----------------------------------------------------
    # properties we need to construct the local project
    # -----------------------------------------------------

    # project_path is is where the local sites will be constructed
    @property
    def project_path(self):
        return self.base_info.get("project_path", "")

    # skeleton_path is where we find the project skeleton we copy
    # to the new project and fill with actual values
    @property
    def skeleton_path(self):
        import skeleton

        return skeleton.__path__[0]

    # the local project itself is structured in an outer folder
    # where we could place the projects documentation
    # and an inner folder, where the actual project is constructed
    @property
    def outer_path(self):
        return "%s/%s" % (self.project_path, self.site_name)

    @property
    def inner_path(self):
        return "%s/%s" % (self.outer_path, self.site_name)

    # sites_home is the installation folder of the erp-workbench
    # it is constructed using the fs path of the config/__init__.py file
    @property
    def sites_home(self):
        return BASE_PATH

    # -----------------------------------------------------
    # sites
    # -----------------------------------------------------

    # erp_server_data_path points to where the data is stored
    # for each site a folder with a data structure is consctructed
    # by default sites_home and erp_server_data_path are identical
    # its value can be set in config/config.yaml
    @property
    def erp_server_data_path(self):
        return self.base_info["erp_server_data_path"]

    data_path = erp_server_data_path

    # sites is a dict of all sites-descriptions known
    _sites = {}

    @property
    def sites(self):
        return self._sites

    # sites_local is a dict of all sites-descriptions with the local flag set
    _sites_local = None

    @property
    def sites_local(self):
        if self._sites_local is None:
            self._sites_local = {}
            for k, v in self.sites.items():
                if v.get("is_local"):
                    self._sites_local[k] = v
        return self._sites_local

    # is_local
    # flags a site description to be used only locally
    @property
    def is_local(self):
        return self.site.get("is_local")

    # sitesinfo_path
    # path to the structure where the sites descriptions are kept
    @property
    def sitesinfo_path(self):
        return self.base_info["sitesinfo_path"]

    # siteinfos is the list of repositories where we manage site descriptions
    # for each siteinfo a folder structure within sitesinfo_path is maintained
    # siteinfos is constructed from config/config/yaml: siteinfos
    # and defaults to localhost
    @property
    def siteinfos(self):
        return self.base_info.get("siteinfos")

    # -----------------------------------------------------
    # the running site
    # -----------------------------------------------------

    # site is the actively "running" site on which we opperate
    # it is constructed by looking up self.site_name (the project name) from the self.sites dict
    @property
    def site(self, site_name=""):
        """return a dictionary with a site description

        Keyword Arguments:
            site_name {str} -- name of the site to look up (default: {''})

        Returns:
            dict -- dictionary with the site description
        """
        """
        may 12th 2019: we want to slowly replace/enhance the content of
        the site description with a site specific yaml file
        This can be found in $SITESLIST-HOME/$SITESLIST-NAME/yaml/$SITE-NAME.yaml
        We do not want to read all of them at start up time, so keep a flag
        _yaml_dirty
        that tells us in the site-description , whether the yaml file is read.
        This flag is set to true when the sites are loaded at startup time

        We must be careful, that the _yaml_dirty is correctly handled when
        flattening sites.
        """

        if site_name:
            name = site_name
        else:
            name = self.site_name
        if name:
            site_dic = self.sites.get(name, {})
            self.get_site_yaml(name, site_dic)
            return site_dic
        else:
            return {}

    def get_site_yaml(self, site_name, site_dic):
        """read site specifig yaml file and clear _yml_dirty flag

        Arguments:
            site_name {string} -- name of the sit
            site_dic {dictionary} -- content of the site description
        """
        sites_list_path = BASE_INFO["sitesinfo_path"]
        yaml_path = "%s/%s/yaml/%s.yaml" % (
            self.sitesinfo_path,
            site_dic.get("site_list_name", "localhost"),
            site_name,
        )
        if os.path.exists(yaml_path):
            yaml_data = read_yaml_file(yaml_path)
            # site_dic.update(yaml_data)
            if self.opts.verbose:
                print(bcolors.WARNING, "not reading %s.yaml" % site_name, bcolors.ENDC)
        site_dic["_yaml_dirty"] = False

    # site_name is the name of the site we are acting on
    # its value has been passed as a command line option when executing a wb command
    # it is a list of site names as we could act on more than one when doing backup and such
    site_names = []

    @property
    def site_name(self):
        return self.site_names and self.site_names[0] or ""

    @site_name.setter
    def site_name(self, v):
        self.site_names = [v]

    # site_data_dir
    # where the data files for this site are to be found
    @property
    def site_data_dir(self):
        self._cp
        return "%s/%s" % (self.erp_server_data_path, self.site_name)

    @property
    def base_url(self):
        return self._base_url

    # -------------------------------------------------------------
    # database
    # -------------------------------------------------------------
    _db_host = "localhost"

    @property
    def db_host(self):
        if self.subparser_name == "docker":
            return self.docker_db_ip
        if self.subparser_name == "support":
            return ""
        return self._db_host

    @property
    def postgres_port(self):
        return self.base_info.get("postgres_port", 5342)

    @property
    def db_name(self):
        return self.site.get("db_name", self.site_name)

    @property
    def use_postgres_version(self):
        return self.docker_defaults.get("use_postgres_version")

    # -------------------------------------------------------------
    # credentials
    # -------------------------------------------------------------

    # odoo main password
    _erp_admin_pw = ""

    @property
    def erp_admin_pw(self):
        return self._erp_admin_pw  # constructed by set_passwords_and_site_values

    # the user running erp-workbench
    @property
    def user(self):
        return ACT_USER

    # ----------
    # local
    # ----------
    # as what user do we login to the database
    _db_user = ""

    @property
    def db_user(self):
        if self.subparser_name == "docker":
            return self.docker_db_user
        return self._db_user

    # the db users password. It is predefined in the docker.yaml file
    _db_user_pw = ""

    @property
    def db_user_pw(self):
        if self.subparser_name == "docker":
            return self.docker_db_user_pw
        return self._db_user_pw

    db_password = db_user_pw

    # as what user are we logging into odoo
    @property
    def rpc_user(self):
        if self.subparser_name == "docker":
            return self.docker_rpc_user
        return self._rpc_user

    # the password of the rpc user is provided dynamically,
    # and not red of the basic config files
    @property
    def rpc_user_pw(self):
        if self.subparser_name == "docker":
            return self.docker_rpc_user_pw
        return self._rpc_user_pw

    # ----------
    # docker
    # ----------
    @property
    def docker_db_user(self):
        return self._docker_db_user

    # by default the odoo docker db user's pw is 'odoo'
    _docker_db_user_pw = "odoo"

    @property
    def docker_db_user_pw(self):
        return self._docker_db_user_pw

    # --------------------------------------------------
    # the credential to log into the sites container
    # --------------------------------------------------
    @property
    def docker_rpc_user(self):
        self._cp
        return self._docker_rpc_user

    # by default the odoo rpc user's pw is 'admin'
    _docker_rpc_user_pw = "admin"

    @property
    def docker_rpc_user_pw(self):
        self._cp
        return self._docker_rpc_user_pw

    # ----------------------
    # the database container
    # ----------------------
    # docker_db_container_name is the name of the container read from docker.yaml
    _docker_db_container_name = ""

    @property
    def docker_db_container_name(self):
        self._cp
        return self._docker_db_container_name

    # docker_db_container is the database container itself
    _docker_db_container = ""

    @property
    def docker_db_container(self):
        self._cp
        return self._docker_db_container

    @property
    def docker_db_ip(self):
        self._cp
        # the ip address to access the db container
        if self.docker_db_container:
            return self.docker_db_container.attrs["NetworkSettings"]["Networks"][
                "bridge"
            ]["IPAddress"]
        return ""

    # docker_rpc_host
    # try to read the output of the command docker inspect containername
    # and collect the ip address of its first network interface
    _docker_rpc_host = "localhost"

    @property
    def docker_rpc_host(self):
        self._cp
        return self._docker_rpc_host

    # _docker_path_map is probably obsolete (robert jan 2019)
    _docker_path_map = ""

    @property
    def docker_path_map(self):
        self._cp
        return self._docker_path_map

    # docker_registry is a registry of docker containers and images
    # used by erp-workbench
    _docker_registry = {}

    @property
    def docker_registry(self):
        self._cp
        return self._docker_registry

    # docker_containers is a list of containers maintained by the docker python libraries
    @property
    def docker_containers(self):
        self._cp
        # update the docker registry so we get info about the db_container_name
        self.update_container_info()

        # get the list of containers
        return self.docker_client.containers

    # the docker_client is the interface erp-workbench uses to access docker
    _cli = {}

    @property
    def docker_client(self):
        self._cp
        if not self._cli:
            url = "unix://var/run/docker.sock"
            import docker

            client = docker.from_env()
            self._cli = client
        return self._cli

    # the name of the container we are dealing with
    _docker_container_name = ""

    @property
    def docker_container_name(self):
        self._cp
        return self._docker_container_name

    # the image we are using to build the container for the running site
    # set in the site description
    _docker_image_version = ""

    @property
    def docker_image_version(self):
        self._cp
        return self._docker_image_version

    erp_image_version = docker_image_version

    # docker_base_image is used to construct the docker_image_version
    # set in the site description
    _docker_base_image = ""

    @property
    def docker_base_image(self):
        self._cp
        return self._docker_base_image

    # the docker_default_port is used when a new site description is constructed
    # and no value has been provided by a command line option, read from docker.yaml
    @property
    def docker_default_port(self):
        self._cp
        # must be defined in the parent class
        return self.project_defaults.get("docker_default_port", 9000)

    # user/account name on dockerhub where the images for the running site are stored
    # set in the site description
    _docker_hub_name = ""

    @property
    def docker_hub_name(self):
        self._cp
        if not self._docker_hub_name:
            return self.docker_defaults.get("docker_hub_name")
        return self._docker_hub_name

    # password for the dockerhub account
    _docker_hub_name_pw = ""

    @property
    def docker_hub_name_pw(self):
        self._cp
        return self._docker_hub_name_pw

    # for the host of a docker container the container is seen like a networked PC
    # when a volume is mounted from the host file system into the docker, we must grant
    # the container users access permissionsto the files on the host fs.
    # how to do this best is not yet clear (jan.5th.2019, robert)
    _docker_external_user_group_id = ""

    @property
    def docker_external_user_group_id(self):
        self._cp
        return self._docker_external_user_group_id

    # what is the port trough which we can access odoo running in the a container
    _docker_rpc_port = ""

    @property
    def docker_rpc_port(self):
        self._cp
        return self._docker_rpc_port

    _docker_long_polling_port = ""

    @property
    def docker_long_polling_port(self):
        self._cp
        return self._docker_long_polling_port

    # the local odoo instances are installed from the odoo nigthly server
    # the nigthly variable helps to constructe the url to the correct version
    _erp_nightly = ""

    @property
    def erp_nightly(self):
        self._cp
        return self._erp_nightly

    # is_enterprise
    _is_enterprise = ""

    @property
    def is_enterprise(self):
        self._cp
        return self._is_enterprise

    # major version number of the odoo used like 11, 12
    _erp_version = ""

    @property
    def erp_version(self):
        self._cp
        return self._erp_version

    # minor version number of the odoo used like .0, .1
    _erp_minor = ""

    @property
    def erp_minor(self):
        self._cp
        return self._erp_minor

    # # odoos install folder
    # @property
    # def odoo_install_home(self):
    #     self._cp
    #     erp_src = 'https://nightly.odoo.com/%s/nightly/src/odoo_%s%s.latest.zip' % (
    #         self._erp_nightly, self.erp_version, self.erp_minor)
    #     return erp_src

    # -----------------------------------------------------
    # properties for handling the remote server on which
    # docker is running
    # -----------------------------------------------------

    # self.remote_servers is a list of servers defined in servers.yaml
    # each such server has properties used to access the containers running
    # on it

    @property
    def http_server(self):
        # what http_server is in use on the remote server
        # either nginx or apache
        # from the list of remote servers
        return self.remote_servers.get(self.remote_server_ip, {}).get("http_server", "")

    # http_server_fs_path is the file system path nginx/apache config file
    # for the running site
    @property
    def http_server_fs_path(self):
        # from the list of remote servers
        return self.remote_servers.get(self.remote_server_ip, {}).get(
            "http_server_fs_path", ""
        )

    # remote_http_url is the public url to access the running site
    _remote_http_url = ""

    @property
    def remote_http_url(self):
        return self._remote_http_url

    # remote_server_ip is the ip of the remote host on which the docker container
    # for the running site is running.
    _remote_server_ip = ""

    @property
    def remote_server_ip(self):
        try:
            remote_ip = socket.gethostbyname(self._remote_server_ip)
        except socket.gaierror as e:
            print(bcolors.FAIL)
            print("*" * 80)
            print(str(e))
            print(bcolors.ENDC)
            remote_ip = "0.0.0.0"
        return remote_ip

    # as what user are we accessing the remote server
    # _remote_user = ''
    @property
    def remote_user(self):
        # from the list of remote servers
        return self.remote_servers.get(
            # find as what user we access that remote server
            self.remote_server_ip,
            {},
        ).get("remote_user", "")

    # what is the the remote users password
    # this is pached in at runtime
    _remote_user_pw = ""

    @property
    def remote_user_pw(self):
        if not self._remote_user_pw:
            # from the list of remote servers
            _remote_user_pw = self.remote_servers.get(
                # and finally find what pw to use on the remote server
                # this pw is patched in at runtime
                self.remote_server_ip,
                {},
            ).get("remote_pw", "")
        return self._remote_user_pw

    # where are the datafolers of the remotely running sites/containers
    # remote_sites_home
    # remote aequivalent to self.site_data_dir
    _remote_sites_home = ""

    @property
    def remote_sites_home(self):
        if not self._remote_sites_home:
            # this info we used to get from the site description
            # but is better placed in the servers yaml
            # so what we do is get the servers ip address from the site description
            # and use it, to get the server-description from the servers.yaml
            self._remote_sites_home = self.remote_servers.get(
                self.remote_server_ip, {}
            ).get("remote_data_path", "")
            if not self._remote_sites_home:
                print(bcolors.FAIL)
                print("*" * 80)
                print(
                    "%s is not defined in the list of remote servers"
                    % self.remote_server_ip
                )
                print(
                    "you can add it by running bin/s --add-server %s"
                    % self.remote_server_ip
                )
                print("please check/adapt the new server description afterwards")
                print(bcolors.ENDC)
        return self._remote_sites_home

    # both of the following is used
    # but it does not make sense to distinguish them on remote servers
    remote_data_path = remote_sites_home

    # -----------------------------------------------------
    # addon modules
    # -----------------------------------------------------

    # docker_addon_path_prefix:
    # prefix added to each addon element in a docker installation

    # local_base_addons:
    # path to the odoo addons in a local installation
    # in the site's project folder
    @property
    def local_base_addons(self):
        base_addon = self.base_info.get("local_base_addons" "")
        return base_addon or ""  # make sure it is a string

    # docker_base_addons:
    # path to the odoo addons in a docker installation
    @property
    def docker_base_addons(self):
        base_addon = self.base_info.get("docker_base_addons" "")
        return base_addon or ""  # make sure it is a string

    # local_addon_path_prefix:
    # prefix added to each addon element in a local installation
    @property
    def local_addon_path_prefix(self):
        prefix = self.base_info.get("local_addon_path_prefix", ",")
        if not prefix.strip().startswith(","):
            prefix = ",%s" % prefix.strip()
        return prefix % {"site_data_dir": self.site_data_dir}

    # docker_addon_path_prefix:
    # prefix added to each addon element in a docker installation
    @property
    def docker_addon_path_prefix(self):
        prefix = self.base_info.get("docker_addon_path_prefix", "")
        if not prefix.startswith(","):
            prefix = "," + prefix.strip()
        return prefix or ""  # make sure it is a string

    @property
    def docker_site_addons_path(self):
        self._cp
        addons_path = (
            "%s/%s"
            % (
                self.docker_base_addons,
                self.docker_addon_path_prefix.join(self._site_addons_list),
            )
        ).replace("//", "/")
        return addons_path

    @property
    def local_site_addons_path(self):
        self._cp
        if self.local_base_addons:
            addons_path = "%s,%s" % (
                self.local_base_addons,
                self.local_addon_path_prefix.join(self._site_addons_list),
            )
        else:
            addons_path = self.local_addon_path_prefix.join(self._site_addons_list)
        # now we have to check, whether one of the modules to load have a inner_paths value
        inner_paths = []
        if self._site_addons_list:
            # we only do it, when there are addons collected
            for addon in self.site.get("addons"):
                inner_ps = addon.get("inner_paths", [])
                for ip in inner_ps:
                    inner_paths.append(
                        "%s/%s" % (addon.get("add_path", addon.get("group", "")), ip)
                    )
        ip_str = ""
        if inner_paths:
            ip_str = self.local_addon_path_prefix + self.local_addon_path_prefix.join(
                inner_paths
            )

        # the above procedure produce out of: self.local_addon_path_prefix.join(['a','b'])
        # something line 'a,/home/robert/workbench/afbschweiz/addons/b'
        # so we have to prepend it with self.local_addon_path_prefix
        # to make it '/home/robert/workbench/afbschweiz/addons/a,/home/robert/workbench/afbschweiz/addons/b'
        # and finaly we appen self.local_addon_path_prefix so that also modules that are added
        # directly into addons are found also
        return (
            self.local_addon_path_prefix
            + addons_path
            + ip_str
            + self.local_addon_path_prefix
        )

    # site_addons is the list of addons_entries in the odoo config
    _site_addons = {}

    @property
    def site_addons(self):
        return self._site_addons

    _site_addons_list = []

    @property
    def site_addons_list(self):
        return self._site_addons_list

    @property
    def erp_addons(self):
        return self.site.get("erp_addons", self.site.get("odoo_addons", []))

    # when constructing a docker image, we need to know
    # what non odoo standard python libraries we need to install
    _site_pip_modules = []

    @property
    def site_pip_modules(self):
        return self._site_pip_modules

    # when constructing a docker image, we need to know
    # what non standard os libraries we need to install
    _site_apt_modules = []

    @property
    def site_apt_modules(self):
        return self._site_apt_modules

    # what modules in the site-descriptions addon list to we
    # want to skip when installing
    _site_skip_list = []

    @property
    def site_skip_list(self):
        return self._site_skip_list

    # -----------------------------------------------------
    # thit n that
    # -----------------------------------------------------
    # the marker is used when constructing files to mark
    # start and end of some blocks
    @property
    def marker(self):
        return MARKER

    # when constructing a docker file we need to know what command to use
    # to install os libraries. For debian based systems this is apt
    @property
    def apt_command(self):
        return self.docker_image.get("apt_command", "apt")

    # when constructing a docker file we need to know what command to use
    # to install python libraries
    @property
    def pip_command(self):
        return self.docker_image.get("pip_command", "pip")

    # redirect_email_to
    # is used in testing environment, together with red_override_email_recipients
    @property
    def redirect_email_to(self):
        return self._redirect_email_to

    _redirect_email_to = ""

    # -----------------------------------------------------
    # values for the odoo config file
    # their defauls are all real from docker.yaml
    # --------------------start----------------------------
    _rpc_host = ""

    @property
    def rpc_host(self):
        return self._rpc_host

    _rpc_port = ""

    @property
    def rpc_port(self):
        if self.subparser_name == "docker":
            return self.docker_rpc_port
        return self._rpc_port

    _docker_local_user_id = ""

    @property
    def docker_local_user_id(self):
        self._cp
        self._docker_local_user_id = self.docker_defaults.get(
            "docker_local_user_id", 999
        )
        return self._docker_local_user_id

    _docker_db_maxcon = ""

    @property
    def docker_db_maxcon(self):
        self._cp
        self._docker_db_maxcon = self.docker_defaults.get("docker_db_maxcon", 64)
        return self._docker_db_maxcon

    _docker_limit_memory_hard = ""

    @property
    def docker_limit_memory_hard(self):
        self._cp
        self._docker_limit_memory_hard = self.docker_defaults.get(
            "docker_limit_memory_hard", 2684354560
        )
        return self._docker_limit_memory_hard

    _docker_limit_memory_soft = ""

    @property
    def docker_limit_memory_soft(self):
        self._cp
        self._docker_limit_memory_soft = self.docker_defaults.get(
            "docker_limit_memory_soft", 2147483648
        )
        return self._docker_limit_memory_soft

    _docker_limit_request = ""

    @property
    def docker_limit_request(self):
        self._cp
        self._docker_limit_request = self.docker_defaults.get(
            "docker_limit_request", 8192
        )
        return self._docker_limit_request

    _docker_limit_time_cpu = ""

    @property
    def docker_limit_time_cpu(self):
        self._cp
        self._docker_limit_time_cpu = self.docker_defaults.get(
            "docker_limit_time_cpu", 60
        )
        return self._docker_limit_time_cpu

    _docker_limit_time_real = ""

    @property
    def docker_limit_time_real(self):
        self._cp
        self._docker_limit_time_real = self.docker_defaults.get(
            "docker_limit_time_real", 120
        )
        return self._docker_limit_time_real

    _docker_limit_time_real_cron = ""

    @property
    def docker_limit_time_real_cron(self):
        self._cp
        self._docker_limit_time_real_cron = self.docker_defaults.get(
            "docker_limit_time_real_cron", 120
        )
        return self._docker_limit_time_real_cron

    _docker_log_handler = ""

    @property
    def docker_log_handler(self):
        self._cp
        self._docker_log_handler = self.docker_defaults.get(
            "docker_log_handler", ":INFO"
        )
        return self._docker_log_handler

    _docker_log_level = ""

    @property
    def docker_log_level(self):
        self._cp
        self._docker_log_level = self.docker_defaults.get("docker_log_level", "info")
        return self._docker_log_level

    _docker_logfile = ""

    @property
    def docker_logfile(self):
        self._cp
        self._docker_logfile = self.docker_defaults.get("docker_logfile", None)
        return self._docker_logfile

    _docker_syslog = ""

    @property
    def docker_syslog(self):
        self._cp
        self._docker_syslog = self.docker_defaults.get("docker_syslog", False)
        return self._docker_syslog

    _docker_logrotate = ""

    @property
    def docker_logrotate(self):
        self._cp
        self._docker_logrotate = self.docker_defaults.get("docker_logrotate", False)
        return self._docker_logrotate

    _docker_log_db = ""

    @property
    def docker_log_db(self):
        self._cp
        self._docker_log_db = self.docker_defaults.get("docker_log_db", False)
        return self._docker_log_db

    _docker_max_cron_threads = ""

    @property
    def docker_max_cron_threads(self):
        self._cp
        self._docker_max_cron_threads = self.docker_defaults.get(
            "docker_max_cron_threads", 2
        )
        return self._docker_max_cron_threads

    _docker_workers = ""

    @property
    def docker_workers(self):
        self._cp
        self._docker_workers = self.docker_defaults.get("docker_workers", 4)
        return self._docker_workers

    _docker_running_env = ""

    @property
    def docker_running_env(self):
        self._cp
        self._docker_running_env = self.docker_defaults.get(
            "docker_running_env", "production"
        )
        return self._docker_running_env

    _docker_without_demo = True

    @property
    def docker_without_demo(self):
        self._cp
        self._docker_without_demo = self.docker_defaults.get(
            "docker_without_demo", True
        )
        return self._docker_without_demo

    _docker_server_wide_modules = ""

    @property
    def docker_server_wide_modules(self):
        self._cp
        self._docker_server_wide_modules = self.docker_defaults.get(
            "docker_server_wide_modules", ""
        )
        return self._docker_server_wide_modules

    _docker_db_sslmode = ""

    @property
    def docker_db_sslmode(self):
        self._cp
        self._docker_db_sslmode = self.docker_defaults.get("docker_db_sslmode", False)
        return self._docker_db_sslmode

    _docker_list_db = False

    @property
    def docker_list_db(self):
        self._cp
        self._docker_list_db = self.docker_defaults.get("docker_list_db", False)
        return self._docker_list_db

    # ------------------end--------------------------------
    # values for the odoo config file
    # -----------------------------------------------------

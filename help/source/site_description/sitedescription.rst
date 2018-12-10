What is a site description
--------------------------

A site description is the heart and soul of the erp-workbeanch. It is a file, that describes the structure of a site.
The information in that file is used for a number of different tasks.

- naming the site
- providing info about its erp type and version
- Info about the docker environment to create 
- Info about erp-modules to load
- info about python modules needed to run the site
- info about os-modules needed to construct the docker container

It contains a number of sections:

- general
- remote server info
- docker info
- apache / nginx info
- erp-modules to install
- oca and other non official modules to install
- version info
- os- and python modules

A new site description file is constructed by executing::

    bin/s --add-site SITENAME {parameters}

A sample site description for a site named demo_global::

    demo_global = {
    # """
    # some nice description of the project
    # """
        "demo_global": {
            'site_name': 'demo_global',
            'servername': 'demo_global',
            'erp_admin_pw': '',
            'erp_version': '12',
            'erp_minor': '.0alpha1',
            'erp_nightly': 'master', # what folder on nightly if not version like 'master'
            # servertype is odoo or flectra
            'erp_provider': 'odoo',
            'db_name': 'demo_global',
            # inherits tells from what other site we want to inherit values
            'inherit': '',
            # should we use demodata
            'without_demo': 'all',
            # pg_version to use with dumper
            # 'pg_version' : '--cluster 10/main',
            'remote_server': {
                'remote_url': 'localhost',  # please adapt
                'remote_data_path': '/root/erp_workbench',
                'remote_user': 'root',
                # where is sites home on the remote server for non root users
                'remote_sites_home': '/home/robert/erp_workbench',
                'redirect_emil_to': '',  # redirect all outgoing mail to this account
                # needs red_override_email_recipients installed
            },
            'docker': {
                'base_image': 'robertrottermann/demo_global:12-latest',
                'erp_image_version': ':12',
                'container_name': 'demo_global',
                # 'db_container_name'    : 'db', # needs only to be set if it is not 'db'
                # trough what port can we access oddo (mapped to 8069)
                'erp_port': '8800',
                # trough what port can we access the sites long polling port (mapped to 8072)
                'erp_longpoll': '18800',
                # within the the container the erp user (odoo or flectra) has a user and group id that
                # is used to access the files in the log and filestore volumes
                'external_user_group_id': '104:107',
                # hub_name is the name to use to store our own images
                'hub_name': 'docker_hub',
                # ODOO_BASE_URL
                # If this variable is set, the `ir.config_parameter` `web.base.url`
                # will be automatically set to this domain when the container
                # starts. `web.base.url.freeze` will be set to `True`.
                'ODOO_BASE_URL': 'https://www.demo_global.ch'
            },
            # docker_hub is used to store images we build ourself
            # by default we use dockers own docker_hub, but could
            # provide our own
            'docker_hub': {
                # 'docker_hub' : {
                #   'user' : 'robertredcor',
                #   'docker_hub_pw' : '',
                # }
            },
            'apache': {
                'vservername': 'www.demo_global.ch',
                # 'vserveraliases': ['demo_global.ch',],
            },
            # erp_addons allow to install base tools
            'erp_addons': [
                # 'website builder',
                # 'crm',
            ],
            'addons': [
                {
                    """
                    # ***********************************
                    # please clean out lines not needed !
                    # ***********************************
                    ## what type is the repository
                    #'type' : 'git',
                    ## what is the url to the repository
                    #'url' : 'ssh://git@gitlab.redcor.ch:10022/agenda2go/docmarolf_calendar.git',
                    ## branch is the repositories branch to be used. default 'master'
                    #'branch' : 'branch.xx',
                    ## what is the target (subdirectory) within the addons folder
                    #'target' : 'docmarolf_calendar',
                    ## group what group should be created within the target directory.
                    #'group' : 'somegroup',
                    ## add_path is added to the addon path
                    ## it is needed in the case when group of modules are added under a group
                    #'add_path : 'somesubdir',
                    ## name is used as name of the addon to install
                    #'name' : 'some name',
                    ## names is a list of names, when more than one addon should be installed
                    ## from a common addon directory
                    #'names' : ['list', 'of', 'addons'],
                    """
                    'type': 'git',
                    'url': '',
                    'name': '',
                    'name': [],
                    'target': '',
                    'group': '',
                    'add_path': '',
                    'branch': '',
                    'tag': '',
                    'pip_list' : [], # what extra python libraries to load
                    'apt_list' : [], # what extra apt modules to install into a docker

                    # 'addon_name' : '' # this value needs only be set, 
                                        # when the name of the modul is not part of the git url
                },
                {
                    # ***********************************
                    # type local allows loading
                    # a module while developing.
                    # the module will not be touched so it
                    # should be in anly of the addon folders
                    # pointed to by othe site.
                    # a good place would be the
                    # SITENAME_addons folder created  in
                    # every buildout folder created by
                    # erp_workbench
                    # ***********************************
                    'type': 'local',
                    'url': '',
                    'name': 'my_library',
                },
            ],
            'tags': {
                # ***********************************
                # a dictonary pointing to tags to be
                # used for addons.
                # tags found here have lower precendence
                # the the ones found in the addon section
                # ***********************************
                # 'module_x' : 'vXXX',
            },
            'skip': {
                # the addons to skip when installing
                # the name is looked up in the addon stanza in the following sequence:
                # - name
                # - add_path
                # - group
                'addons': [],
                # skip when it is installed
                'updates': [],
            },
            # extra libraries needed to be installed by pip or apt
            # this is used in two places
            # 1. pip installs are executed when creating a site on the local computer
            #    and executing bin/dosetup [-f] in the sites buildout directory
            # 2. both pip and apt installs are executed when a docker image is created
            'extra_libs': {
                # 'pip' : [
                #   'xmlsec',
                #   'scrapy',
                #   'html2text',
                # ],
                # 'apt' : [
                #   'python-dev',
                #   'pkg-config',
                #   'libxml2-dev',
                #   'libxslt1-dev',
                #   'libxmlsec1-dev',
                #   'libffi-dev',
                # ]
            },
            'develop': {
                'addons': [],
            },
            # slave info: is this site slave of a master site from which it will be updated
            'slave_info': {
                # # master_site ist the name of the mastersite
                # # this must be a site in sites.py
                # "master_site" : '',
                # # master_domain is the domain from which the master is copied
                # "master_domain" : 'localhost',
            }
        },

    }

    # all options that are added to the parent parser
# the parent parser gets incloded in some other also
# and provides common options

from config import BASE_PATH, BASE_INFO, DOCKER_DEFAULTS
from scripts.parser_handler import ParserHandler

def add_options_docker(parser, result_dic):
    """add options to the create parser
    
    Arguments:
        parser {argparse instance} -- instance to which arguments should be added
    """
    parser_docker = ParserHandler(parser, result_dic)

    
    # -----------------------------------------------
    # manage docker
    # -----------------------------------------------
    #parser_support_s = parser_support.add_subparsers(title='docker commands', dest="docker_commands")
    parser_docker.add_argument(
        "-dBI", "--use_bitnami",
        action="store_true", dest="docker_use_bitnami", default=False,
        help='Use bitnami settings when handling docker or kubernetes',
    )
    parser_docker.add_argument(
        "-dbi", "--build_image",
        action="store_true", dest="docker_build_image", default=False,
        help='create a docker image. Name must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_docker.add_argument(
        "-dbis", "--build_image_use_sites",
        action="store", dest="use_sites",
        help='use sites to collect libraries to build image',
        need_name=True
    )
    parser_docker.add_argument(
        "-dbiC", "--build_image_collect_sites",
        action="store_true", dest="use_collect_sites",
        help='collect all libraries from sites with the same erp version, to create an image that can handle all situations',
        need_name=True,
        name_valid=True,
    )
    parser_docker.add_argument(
        "-dp", "--docker-pull-image",
        action="store_true", dest="docker_pull_image", default=False,
        help='pull actual image used by a docker container. Name must be provided,'
    )
    parser_docker.add_argument(
        "-dpi", "--push_image",
        action="store_true", dest="docker_push_image", default=False,
        help='push a docker image. Name of site must be provided'
    )
    parser_docker.add_argument(
        "-dc", "--create_container",
        action="store_true", dest="docker_create_container", default=False,
        help='create a docker container. Name must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_docker.add_argument(
        "-dr", "--recreate-container",
        action="store_true", dest="docker_recreate_container", default=False,
        help='recreate docker container. Name must be provided,'
    )
    parser_docker.add_argument(
        "-dR", "--rename-container",
        action="store_true", dest="docker_rename_container", default=False,
        help='rename container to have actual date in its name and recreate docker container. Name must be provided,'
    )
    parser_docker.add_argument(
        "-dcdb", "--create_db_container",
        action="store_true", dest="docker_create_db_container", default=False,
        help='create a docker database container. It will be named db. It uses the postgres version in config/docker.yaml',
    )
    parser_docker.add_argument(
        "-dbdumper", "--build_dumper_image",
        action="store_true", dest="build_dumper_image", default=False,
        help='buid a dbdumper image. It uses the postgres version in config/docker.yaml',
    )
    parser_docker.add_argument(
        "-dddb", "--drop_db",
        action="store_true", dest="docker_drop_db", default=False,
        help='drop database in db docker container. name of the site db belongs to must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_docker.add_argument(
        "-dlsdb", "--list_db",
        action="store_true", dest="docker_list_db", default=False,
        help='list databases in db docker container.',
    )
    parser_docker.add_argument(
        "-dcu", "--create_update_container",
        action="store_true", dest="docker_create_update_container", default=False,
        help='create a docker container that runs the etc/runodoo.sh script at startup. Name must be provided',
        need_name=True,
        name_valid=True,
    )
    # -----------------------------------------------
    # manage bitnami
    # -----------------------------------------------
    # parser_docker.add_argument(
    #     "-dbib", "--build-image-bitnami",
    #     action="store_true", dest="build_image_bitnami", default=False,
    #     help='Build an image after the holi gospel of bitnami')
    parser_docker.add_argument(
        "-drhc", "--refetch-helm-chart",
        action="store_true", dest="refetch_helm_chart", default=False,
        help='Refetch helm chart even if it already exists')
    parser_docker.add_argument(
        "-dE", "--execute-script",
        action="store", dest="executescript",
        help="Run a script against a running erp site. Name must be given",
        need_name=True,
        name_valid=True)
    parser_docker.add_argument(
        "-dEP", "--execute-script-parameter",
        action="store", dest="executescriptparameter",
        help="parameters to be passed to the executed script. It must be a comma separated string of key=value pairs. No spaces!")
    parser_docker.add_argument(
        "-dSL", "--set-local-data-docker",
        action="store_true", dest="set_local_data_docker", default=False,
        help="force setting local data from the site description, when we are running in a docker")
    parser_docker.add_argument(
        "-dSOS", "--set-erp-settings-docker",
        action="store_true", dest="set_erp_settings_docker", default=False,
        help="set erp settings like the mail handlers. The script tries to define for what ip",
        need_name=True,
        name_valid=True)
    #parser_docker.add_argument(
        #"-dsapw", "--docker-set-admin-pw",
        #action="store_true", dest="docker_set_admin_pw", default = False,
        #help='Set admin password from site description in a docker conatiner. option -n must be set and valid.',
    #)
    parser_docker.add_argument(
        "-dd", "--delete_container",
        action="store_true", dest="docker_delete_container", default=False,
        help='delete a docker container. Name must be provided',
        need_name=True
    )
    parser_docker.add_argument(
        "-ds", "--start_container",
        action="store_true", dest="docker_start_container", default=False,
        help='start a docker container. Name must be provided',
        need_name=True
    )
    parser_docker.add_argument(
        "-dshow",
        action="store_true", dest="docker_show", default=False,
        help='show some info about a container. Name must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_docker.add_argument(
        "-dshowa",
        action="store_true", dest="docker_show_all", default=False,
        help='show all info about a container. Name must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_docker.add_argument(
        "-dS", "--stop_container",
        action="store_true", dest="docker_stop_container", default=False,
        help='stop a docker container. Name must be provided',
        need_name=True
    )
    parser_docker.add_argument(
        "-drs", "--restart_container",
        action="store_true", dest="docker_restart_container", default=False,
        help='restart a docker container. Name must be provided'
    )
    parser_docker.add_argument(
        "-ddbname", "--dockerdbname",
        action="store", dest="dockerdbname", # no default, otherwise we can not get it from the site description
        help="user to access db in a docker, if not set, it is taken form the sites erp stanza, default %s" % DOCKER_DEFAULTS['docker_db_container_name'])

    parser_docker.add_argument(
        "-ddbuser", "--dockerdbuser",
        action="store", dest="docker_db_user", # no default, otherwise we can not get it from the site description
        help="user to access db in a docker, if not set, it is taken form the sites erp stanza, default %s" % DOCKER_DEFAULTS['docker_db_user'])

    parser_docker.add_argument(
        "-ddbpw",
        action="store", dest="docker_db_user_pw", # no default, otherwise we can not get it from the site description
        help="password to access db in a docker, if not set, it is taken form the sites erp stanza, default %s" % DOCKER_DEFAULTS['docker_db_user_pw'])

    parser_docker.add_argument(
        "-drpcuser",
        action="store", dest="drpcuser", # no default, otherwise we can not get it from the site description
        help="password to access db in a docker, if not set, it is taken form the sites erp stanza, default %s" % DOCKER_DEFAULTS['docker_rpc_user'])

    parser_docker.add_argument(
        "-drpcuserpw",
        action="store", dest="drpcuserpw", # no default, otherwise we can not get it from the site description
        help="password to access db in a docker, if not set, it is taken form the sites erp stanza, default %s" % DOCKER_DEFAULTS['docker_rpc_user_pw'])

    parser_docker.add_argument(
        "-dud", "--dataupdate_docker",
        action="store_true", dest="dataupdate_docker", default=False,
        help='update local data from remote server into local docker. Name must be provided.\nRespects -N and -nupdb options',
        need_name=True
    )
    parser_docker.add_argument(
        "-ddump", "--dump-local-docker",
        action="store_true", dest="dump_local_docker", default=False,
        help='dump database data into the servers dump folder. does use docker',
        need_name=True
    )
    parser_docker.add_argument(
        "-dio", "--dinstallown",
        action="store_true", dest="dinstallown", default=False,
        help='install all modules listed as addons. Name must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_docker.add_argument(
        "-duo", "--dupdateown",
        action="store", dest="dupdateown", default='',
        help='update modules listed as addons, pass a comma separated list (no spaces) or all. Name must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_docker.add_argument(
        "-dro", "--dremoveown",
        action="store", dest="dremoveown", default='',
        help='remove modules listed as addons, pass a comma separated list (no spaces) or all. Name must be provided',
        need_name=True,
        name_valid=True,
    )
    parser_docker.add_argument(
        "-dI", "--dinstall_erp_modules",
        action="store_true", dest="dinstall_erp_modules", default=False,
        help='install modules listed as addons into docker. Name must be provided',
        need_name=True,
        name_valid=True,
    )
    #parser_docker.add_argument(
        #"-dassh", "--docker-add_ssh",
        #action="store_true", dest="docker_add_ssh", default=False,
        #help='add ssh to a docker container'
    #)    
    

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# make sure we are in a virtualenv
# !!!!!!!!!!!!!!!!!!!!!!!!!!!
# Do NOT !!!!! sort imports
# !!!!!!!!!!!!!!!!!!!!!!!!!!!
import os, sys, time
# robert: i usualy thest in wingide
if not os.environ.get('VIRTUAL_ENV') and not os.environ.get('WINGDB_ACTIVE') and not os.environ.get('UNIT_TESTING'):
    print('not running in a virtualenv')
    print('activate the worbench environment executing:')
    print('workon workbench')
    sys.exit()
from argparse import RawTextHelpFormatter, ArgumentParser
import readline, glob
import subprocess
#import xml.dom.minidom
import re
import argparse
import argcomplete

try:
    from scripts.bcolors import bcolors
except ImportError:
    sys.path.insert(0, os.path.split(os.path.split(os.path.realpath(__file__))[0])[0])

from scripts.bcolors import bcolors
from scripts.banner import BANNER_HEAD, BANNER_TEXT

from scripts.messages import *

from scripts.utilities import create_server_config, checkout_sa, list_sites

try:
    from config import SITES, SITES_LOCAL
except ImportError:
    from config import sites_handler
    sites_handler.check_and_create_sites_repo()
    from config import SITES, SITES_LOCAL
    
from config import ACT_USER, BASE_PATH, FOLDERNAMES, \
    BASE_INFO, MARKER, LOGIN_INFO_FILE_TEMPLATE, \
    REQUIREMENTS_FILE_TEMPLATE, DOCKER_DEFAULTS
from config.config_data.base_info import BASE_DEFAULTS
from config.config_data.project_info import PROJECT_DEFAULTS

from config.handlers import SiteCreator
from config.handlers import DockerHandler
from config.handlers import SupportHandler
from config.handlers import RemoteHandler
from config.handlers import MailHandler

# get config options
from scripts.options_create import add_options_create
from scripts.options_docker import add_options_docker
from scripts.options_parent import add_options_parent
from scripts.options_rpc import add_options_rpc
from scripts.options_support import add_options_support
from scripts.options_remote import add_options_remote
from scripts.options_mail import add_options_mail

banner = bcolors.red + BANNER_HEAD  + bcolors.normal + BANNER_TEXT

#ascii art by: Cara Pearson
colors = bcolors

#https://stackoverflow.com/questions/6365601/default-sub-command-or-handling-no-sub-command-with-argparse
def set_default_subparser(self, name, args=None):
    """default subparser selection. Call after setup, just before parse_args()
    name: is the name of the subparser to call by default
    args: if set is the argument list handed to parse_args()

    , tested with 2.7, 3.2, 3.3, 3.4
    it works with 2.6 assuming argparse is installed
    """
    subparser_found = False
    name_to_return = ''
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:  # global help if no subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
                    name_to_return = sp_name
        if not subparser_found:
            # insert default in first position, this implies no
            # global options without a sub_parsers specified
            if args is None:
                sys.argv.insert(1, name)
            else:
                args.insert(0, name)
            name_to_return = name
    return name_to_return

def main(opts, parsername, need_names_dic):
    """
    """
    # default_handler = SiteCreator
    try:
        import wingdbstub
    except:
        pass
    # if the name ends with /, cut it off
    if opts.name.endswith('/'):
        opts.name = opts.name[:-1]
    opts.subparser_name = parsername
    if parsername == 'create':
        handler = SiteCreator(opts, SITES)
    elif parsername == 'support':
        handler = SupportHandler(opts, SITES)
    elif parsername == 'remote':
        handler = RemoteHandler(opts, SITES)
    elif parsername == 'docker':
        handler = DockerHandler(opts, SITES)
    elif parsername == 'mail':
        handler = MailHandler(opts, SITES)
    else:
        handler = SiteCreator(opts, SITES)
       # _subparser_name = 'docker'

    # ckeck whether the used option needs a name to work
    handler.check_name(need_names_dic=need_names_dic)

    # ckeck wheter the path to the sites-list has to be adapted
    # if yes, flag it to the user. To do the actual update
    # the user has to use the support optin --fix-sites-list
    from config import sites_handler
    sites_handler.fix_sites_list()
    # ckeck wheter the the sites-list has to be autoloaded
    sites_handler.check_pull()
    did_run_a_command = False
    # ----------------------
    # create commands
    # ----------------------
    if parsername == 'create':

        # create
        # ------
        # builds or updates a server structure
        # to do so, it does a number of steps
        #   - creates the needed folders in $ERP_SERVER_DATA
        #   - creates a build structure in $PROJECT_HOME/$SITENAME/$SITENAME
        #     where $PROJECT_HOME is read from the config file.
        #   - copies and sets up all files from skeleton directory to the build structure
        #     this is done executing create_new_project and do_copy
        #   - builds a virtualenv environment in the build structure
        #   - prepares to builds an erp server within the build structure by
        #     execution  bin/build_erp within the build structure.
        #     Within this bild environment the erp's module path will be set
        #     that it points to the usual erp-workbench directories within the build substructure
        #     and also to the directories within erp_workbench as dictated by the
        #     various modules installed from interpreting the site declaration
        #     in sites.py
        #   - add a "private" addons folder within the build structure called
        #     $SITENAME_addons. This folder is also added to the erp-site's addon path.
        #   - set the data_dir to point to $ERP_SERVER_DATA/$SITENAME/filestore
        #
        # modules_update
        # -------------
        if opts.create or opts.modules_update or opts.module_update:
            info_dic = {
                'project_path' : handler.default_values['inner'],
                'erp_version': BASE_INFO.get('erp_version', BASE_INFO.get('odoo_version')),
                'site_name' : handler.site_name,
                'erp_provider' : PROJECT_DEFAULTS.get('erp_provider'),
            }
            if opts.create:
                existed = handler.create_or_update_site()
                if existed:
                    if not opts.quiet:
                        print()
                        print('%s site allredy existed' % handler.site_name)
                        print(SITE_EXISTED % info_dic)
                else:
                    if handler.site_name:
                        if not opts.quiet:
                            print()
                            print('%s site created' % handler.site_name)
                            print(SITE_NEW % info_dic)
            # create the folder structure within the datafoler defined in the config
            # this also creates the config file used by a docker server within the
            # newly created folders
            handler.create_folders(quiet=True)
            create_server_config(handler)
            did_run_a_command = True
    
            # make sure project was added to bash_aliases
            handler.add_aliases()
            # checkout repositories
            checkout_sa(opts)
            
        # list_sites
        # ----------
        # list_sites lists all existing sites both from global and local sites
        if opts.list_sites:
            list_sites(SITES, opts.quiet)
            did_run_a_command = True
            return

        # listownmodules
        # --------------
        # list the modules that are declared within the selected site
        # installown install all erp modules declared in the selected site
        # todo: why are the two following options combined here??? !!!!!!!!!!!!
        if opts.listownmodules or opts.install_erp_modules:
            handler.install_own_modules()
            did_run_a_command = True
            return
        
        # delete_site_local
        # --------
        # delete_site_local removes a site and all project files
        if opts.delete_site_local:
            handler.delete_site_local()
            did_run_a_command = True
            return

        # installown or updateown or removeown
        # ------------------------------------
        # installown install all modules declared in the selected site
        # updateown updates one or all modules declared in the selected site
        # removeown removes one or all modules declared in the selected site
        #
        # to be able to execute do this, the target server has to be running.
        # this server is accessed uding odoo's rpc_api.
        # to do so, info on user, that should access the running server needs
        # to be collected. the following values
        # read from either the config data or can be set using command line options.
        # --- database ---
        # - db_user : the user to access the servers database
        #   to check what modules are allready installed the servers database
        #   has to be accessed.
        #   option: "-dbu", "--dbuser".
        #   default: logged in user
        # - db_password
        #   option: "-p", "--dbpw".
        #   default: admin
        # - dbhost: the host on which the database is running
        #   option: "-dbh", "--dbhost"
        #   default: localhost.
        # --- user accessing the running odoo server ---
        # - rpcuser: the login user to access the odoo server
        #   option: "-rpcu", "--rpcuser"
        #   default: admin.
        # - rpcpw: the login password to access the odoo server
        #   option: "-P", "--rpcpw"
        #   default: admin.
        # - rpcport: the the odoo server is running at
        #   option: "-PO", "--port"
        #   default: 8069.
    
        if opts.installown or opts.updateown or opts.removeown:
            handler.install_own_modules()
            did_run_a_command = True

        # dataupdate 
        # ----------
        # these options are used to copy a running remote server to a lokal
        # odoo instance
        #
        # dataupdate:
        # -----------
        # this copies both an odoo db and the related file data structure from
        # a remote server to a locally existing (buildout created) server.
        # the needed info is gathered from diverse sources:
        # local_data.py
        # -------------
        # - DB_USER: the user name with which to access the local database
        #   default: the logged in user.
        # - DB_PASSWORD: the password to access the local database server
        #   default: odoo
        #   If the option -p --password is used, the password in local_data is
        #   overruled.
        # remote data:
        # ------------
        # to collect data on the remote server the key remote_server is used
        #   to get info from sites.py for $SITENAME
        # - remote_url : the servers url
        # - remote_data_path : COLLECT it from ODOO_SERVER_DATA ??
        # local_data.REMOTE_SERVERS:
        # ---------------------------
        # from this dictonary information on the remote server is collected
        # this is done looking up 'remote_url' in local_data.REMOTE_SERVERS.
        # - remote_user: user to acces the remote server with
        # - remote_pw : password to access the remote user with. should normaly the empty
        #   as it is best only to use a public key.
        # - remote_data_path: how the odoo erverdata can be access on the remote server
        #   ??? should be created automatically
        # sites_pw.py:
        # ------------
        # the several password used for the services to be acces on the odoo instance,
        # the remote server or on the mail server can be mixed in from
        # sites_pw.py.
        # !!!! sites_pw.py should be kept separate, and should not be version controlled with the rest !!!
        #
        # it executes these steps:
        # - it executes a a command in a remote remote server in a remote shell
        #   this command starts a temporary docker container and dumps the
        #   database of the source server to its dump folder which is:
        #       $REMOTE_URL:$ODOO_SERVER_DATA/$SITENAME/dump/$SITENAME.dmp
        # - rsync this file to:
        #       localhost:$ODOO_SERVER_DATA/$SITENAME/dump/$SITENAME.dmp
        # - drop the local database $SITENAME
        # - create the local database $SITENAME
        # - restore the local datbase $SITENAME from localhost:$ODOO_SERVER_DATA/$SITENAME/dump/$SITENAME.dmp
        # - rsync the remote filestore to the local filestore:
        #   which is done with a command similar to:
        #   rsync -av $REMOTEUSER@$REMOTE_URL:$ODOO_SERVER_DATA/$SITENAME/filestore/ localhost:$ODOO_SERVER_DATA/$SITENAME/filestore/
        #
        # run_local_docker
        # ----------------
        # when the option -L --local_docker is used, data is copied from a docker container
        # running on localhost
        if opts.dataupdate  or opts.dataupdate_close_connections:
            # def __init__(self, opts, default_values, site_name, foldernames=FOLDERNAMES)
            set_local = True
            handler.doUpdate(db_update = not opts.noupdatedb, norefresh=opts.norefresh, set_local = set_local)
            did_run_a_command = True
        if opts.dump_local:
            # def __init__(self, opts, default_values, site_name, foldernames=FOLDERNAMES)
            handler.dump_instance()
            did_run_a_command = True

    # ----------------------
    # docker commands
    # ----------------------
    if parsername == 'docker':
        # docker_create_container
        # -----------------------
        # it creates and starts a docker container
        # the created container collects info from sites.py for $SITENAME
        # it uses the data found with the key "docker"
        # it collects these data:
        # - container_name: name of the container to create.
        #   must be unique for each remote server
        # - odoo_image_version: name of the docker image used to build
        #   the container
        # - odoo_port: port on which to the running odoo server within the
        #   container can be reached. must be unique for each remote server
        if opts.docker_create_container:
            # "docker -dc", "--create_container",
            handler.check_and_create_container()
            did_run_a_command = True
        if opts.docker_create_update_container:
            # "docker -dcu", "--create_update_container",
            handler.check_and_create_container(update_container=True)
            did_run_a_command = True
        if opts.docker_delete_container:
            handler.check_and_create_container(delete_container=True)
            did_run_a_command = True
        if opts.docker_create_db_container:
            # "docker -dcdb", "--create_db_container",
            handler.check_and_create_container(container_name='db')
            did_run_a_command = True

        # recreate container
        # ------------------
        # recreate a conainer
        if opts.docker_recreate_container:
            handler.check_and_create_container(recreate_container = True)
            did_run_a_command = True
            return
        
        # rename container
        # ----------------
        # recreate a conainer
        if opts.docker_rename_container:
            handler.check_and_create_container(rename_container = True)
            did_run_a_command = True
            return
        
        # build image
        # ----------
        # build docker image used by a site
        if opts.docker_build_image:
            handler.build_image()
            did_run_a_command = True
            return
        if opts.build_dumper_image:
            handler.build_dumper_image()
            did_run_a_command = True
            return

        # pull image
        # ----------
        # pull an actual docker image used by a site
        if opts.docker_pull_image:
            handler.check_and_create_container(pull_image = True)
            did_run_a_command = True
            return
    
        # push image
        # ----------
        # push docker image used by a site
        if opts.docker_push_image:
            handler.push_image()
            did_run_a_command = True
            return
        
        # installown or updateown or removeown
        # ------------------------------------
        # installown install all modules declared in the selected site
        # updateown updates one or all modules declared in the selected site
        # removeown removes one or all modules declared in the selected site
        
        # ----------> see create commands
        
        if opts.dinstallown or opts.dupdateown or opts.dremoveown or opts.dinstall_erp_modules:
            #handler = dockerHandler(opts, default_values, site_name)
            handler.docker_install_own_modules()
            did_run_a_command = True

        # dataupdate_docker
        # -------------------------------
        # these options are used to copy a running remote server to a lokal
        # odoo instance
        #
        # see explanation create->dataupdate
        # run_local_docker
        # ----------------
        # when the option -L --local_docker is used, data is copied from a docker container
        # running on localhost
        if opts.dataupdate_docker:
            # def __init__(self, opts, default_values, site_name, foldernames=FOLDERNAMES)
            set_local = True
            handler.doUpdate(db_update = not opts.noupdatedb, norefresh=opts.norefresh, set_local = set_local)
            did_run_a_command = True
        if opts.dump_local_docker:
            # def __init__(self, opts, default_values, site_name, foldernames=FOLDERNAMES)
            handler.dump_instance()
            did_run_a_command = True

        # start or restart docker
        if opts.docker_restart_container or opts.docker_start_container or opts.docker_stop_container:
            if opts.docker_start_container:
                handler.start_container()
            elif opts.docker_restart_container:
                handler.restart_container()
            else:
                handler.stop_container()
            did_run_a_command = True

        # docker_show
        # --------------
        # show some info about a containe
        if opts.docker_show or opts.docker_show_all:
            if opts.docker_show_all:
                handler.docker_show('all')
            else:
                handler.docker_show()
            did_run_a_command = True
        
        if not did_run_a_command:
            print(bcolors.WARNING)
            print('*' * 80)
            print('The selected docker option is either invalid or not yet implemented')
            print(bcolors.ENDC)
        return
    
    # ----------------------
    # support commands
    # ----------------------
    if parsername == 'support':
        # add_site
        # --------
        # add_site adds a site description to the sites.py file
        # add_site_local adds a site description to the sites_local.py file
        if opts.add_site or opts.add_site_local:
            handler.add_site_to_sitelist()
            did_run_a_command = True
            return

        # drop_site
        # --------
        # drop_site removes a site description from the sites.py file
        if opts.drop_site:
            handler.drop_site()
            did_run_a_command = True
            return

        # edit_site, edit_server
        # ----------------------
        # Lets the user edit the content of config/localdat.py to edit a server
        # description, or change the server description in LOCALDATA['sitesinfo_path']
        if opts.edit_site or opts.edit_server:
            if opts.edit_site:
                handler.check_name()
            handler.edit_site_or_server()
            did_run_a_command = True
            return

        # add_server
        # ----------
        # add_server_to_server_list
        # add new server info to localdat
        # ----------------------------------
        if opts.add_server:
            handler.add_server_to_server_list()
            did_run_a_command = True
            return
    
def parse_args():
    print_banner = True
    print_banner = BASE_DEFAULTS.get('print_banner', True)
    if print_banner:
        print(banner)
    
    argparse.ArgumentParser.set_default_subparser = set_default_subparser
    usage = ""
    need_names_dic = {
        'need_name' : [], # we need a name
        'name_valid': [], # given name must be valid  
    }
    # -----------------------------------------------
    # parent parser holds arguments, that are used for all subparsers 
    parent_parser = ArgumentParser(usage=usage, add_help=False)
    # set options for parent_parser
    add_options_parent(parent_parser, need_names_dic)
    # parser_rpc is also used in several parsers to provide default values
    parser_rpc = ArgumentParser(add_help=False)
    # set options for parser_rpc
    add_options_rpc(parser_rpc, need_names_dic)


    # parser is the main parser
    parser = ArgumentParser()
    subparser_help = """
    erp workbench provides commands to manage erp sites.
    These commands ares grouped into several groups of subcommands.
    use {SUBCOMMAND} --help to see the subcommans options.
    """
    subparsers = parser.add_subparsers(help=subparser_help)

    # -----------------------------------------------
    # create commands
    parser_manage = subparsers.add_parser(
        'create',
        help="""
        create is used to manage local and remote sites by reading 
        site descrition created using the sites command set
        """,
        parents=[parser_rpc, parent_parser],
        #prog='PROG',
        usage='%(prog)s [options]')
    # -----------------------------------------------
    # support commands
    parser_support = subparsers.add_parser(
        'support', 
        help="""
        support provides commands to handle site descriptions from which sites are constructed
        and other support commands.
        """, 
        parents=[parent_parser])
    add_options_support(parser_support, need_names_dic)
    # -----------------------------------------------
    # manage docker
    parser_docker = subparsers.add_parser(
        'docker',
        help='docker provides commands to handle docker containers',
        parents=[parent_parser])
    add_options_docker(parser_docker, need_names_dic)
    # -----------------------------------------------
    # manage remote server (can be localhost)
    parser_remote = subparsers.add_parser(
        'remote',
        help='remote provides commands to manage elements of the remote server.',
        parents=[parent_parser])
    # -----------------------------------------------
    # manage mails
    parser_mail = subparsers.add_parser(
        'mail',
        help='mail provides commands to manage mail accounts.',
        parents=[parent_parser])
    add_options_mail(parser_mail, need_names_dic)

    # -----------------------------------------------
    # manage sites create and update sites
    # -----------------------------------------------
    #http://stackoverflow.com/questions/10448200/how-to-parse-multiple-sub-commands-using-python-argparse
    #parser_site_s = parser_site.add_subparsers(title='manage sites', dest="site_creation_commands")
    add_options_create(parser_manage, need_names_dic)
    # -----------------------------------------------
    # manage remote server (can be localhost)
    # -----------------------------------------------
    add_options_remote(parser_remote, need_names_dic)
    
    sub_parser = parser.set_default_subparser('create')
    args, unknownargs = parser.parse_known_args()
    command_line = ' '.join(sys.argv)
    args.command_line = command_line
    unknownargs = [a for a in unknownargs if a and a[0] != '-']
    if not args.name:
        cmds = ['create', 'support', 'docker', 'remote', 'mail']
        if unknownargs and unknownargs[0] not in cmds:
            args.name = unknownargs[0]
        else:
            args.name = ''
    return args, sub_parser, need_names_dic


if __name__ == '__main__':
    
    args, sub_parser_name, need_names_dic = parse_args()


    #(opts, args) = parser.parse_args()

    # --------------------------------------------------------
    # set a marker, so we can check if any command was executed
    # --------------------------------------------------------
    did_run_a_command = False
    main(args, sub_parser_name, need_names_dic) #opts.noinit, opts.initonly)

    if 0: #not did_run_a_command:
        print(bcolors.FAIL)
        print('*' * 80)
        print('it looks as if no valid comand was executed')
        print('*' * 80)
        print(bcolors.ENDC)
        

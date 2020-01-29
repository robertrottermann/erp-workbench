#!bin/python
# -*- encoding: utf-8 -*-

#https://www.digitalocean.com/community/tutorials/how-to-set-up-a-private-docker-registry-on-ubuntu-14-04
import os
import re
import sys
from scripts.bcolors import bcolors
import docker
try:
    from docker import Client
    print(bcolors.FAIL)
    print('*' * 80)
    print('the Docker-library you are using is outdated')
    print('please run:')
    print('    pip uninstall docker-py && pip install -U docker')
    print()
    print('in an active workbench environment')
    print(bcolors.ENDC)
    sys.exit()
except ImportError:
    pass
from config import ODOO_VERSIONS
#from config.handlers import InitHandler, DBUpdater
from scripts.create_handler import InitHandler
from scripts.update_local_db import DBUpdater
import shutil
from site_desc_handler.handle_remote_data import get_remote_server_info
from scripts.bcolors import bcolors
import datetime
from datetime import date
from requests.exceptions import HTTPError
import shlex

from scripts.messages import DOCKER_DB_MISSING, DOCKER_DB_MISSING, DOCKER_INVALID_PORT, \
    DOCKER_INVALID_PORT, DOCKER_IMAGE_PULLED, DOCKER_IMAGE_PULL_FAILED, DOCKER_IMAGE_NOT_FOUND, \
    DOCKER_IMAGE_PUSH_MISING_HUB_INFO, SITE_NOT_EXISTING, DOCKER_IMAGE_CREATE_ERROR, \
    DOCKER_IMAGE_CREATE_MISING_HUB_INFO, DOCKER_IMAGE_CREATE_MISING_HUB_USER, ERP_VERSION_BAD, \
    DOCKER_IMAGE_CREATE_MISING_HUB_USER, DOCKER_IMAGE_CREATE_PLEASE_WAIT, DOCKER_IMAGE_CREATE_FAILED, \
    DOCKER_IMAGE_CREATE_DONE

# DOCKER_APT_PIP_HEAD is used when constructing docker and either pip or
# apt libraries needs to be merged in
DOCKER_APT_PIP_HEAD = """WORKDIR /odoo
RUN apt update;
"""

class DockerHandler(InitHandler, DBUpdater):
    master = '' # possible master site from which to copy

    """
    this class needs a general fixing !!!!!!!!
    we should use docker.from_env() to create the client
    and have everything done by this client and not by "import Client"
    actually we seem not to use Client at all!!
    """
    def __init__(self, opts, sites = {}, url='unix://var/run/docker.sock', use_tunnel=False):
        """
        """
        super().__init__(opts, sites)
        self.url = url

        if not self.site:
            return # when we are creating the db container

        ####################
        # self.client new 17th june 2019
        self.client = docker.from_env()

        # collect data from the site description
        self.setup_docker_env(self.site)
        # make sure the registry exists
        self.update_docker_info()
        # ----------------------
        # get the db container
        # ----------------------
        # the name of the database container is by default db

        # update the docker registry so we get info about the db_container_name
        self.update_container_info()

    _subparser_name = 'docker'
    @property
    def subparser_name(self):
        return self._subparser_name

    def get_container(self, name):
        cli = self.docker_client
        containers = cli.containers.list(filters={'name': name}, all=True)
        if containers:
            return containers[0]


    def update_docker_info(self, name='', required=False, start=True):
        """
        update_docker_info checks if a docker exists and is started.
        If it does not exist and required is false, the container is created and started.
        If it does not exist and required is True, an error is thrown.
        If it does exist and is stoped and start is True, it is started.
        If it does exist and is stoped and start is False, nothing happens.

        In all cases, status info read from the docker engine is saved into the registry
        """
        registry = self.docker_registry
        cli = self.docker_client
        info = []
        if name:
            # check whether a container with the requested name exists.
            # similar to docker ps -a, we need to also consider the stoped containers
            #existing_container  = cli.containers.get(name)
            existing_container = self.get_container(name)
            if existing_container:
                # collect info on the container
                # this is equivalent to docker inspect name
                try:
                    info = existing_container.attrs
                except docker.errors.NotFound:
                    info = []
                if info:
                    if info['State']['Status'] != 'running':
                        if start:
                            existing_container.restart()
                            existing_container = self.get_container(name)
                            info = existing_container and existing_container.attrs
                            if not info:
                                raise ValueError('could not restart container %s', name)
                        elif required:
                            raise ValueError('container %s is stoped, no restart is requested', name)
                    registry[name] = info
                else:
                    if required:
                        if name == 'db':
                            print(DOCKER_DB_MISSING)
                            return
                        raise ValueError('required container:%s does not exist' % name)
            else:
                if required:
                    if name == 'db':
                        print(DOCKER_DB_MISSING)
                        return
                    raise ValueError('required container:%s does not exist' % name)
        return info # only needed when testing

    def update_container_info(self):
        """
        update_container_info tries to start all docker containers a site is associated with:
        The server where these dockers reside, depends on the options selected.
        It could be either localhost, or the remote host.
        Either two or three containers are handeled on each site:
        - db: this is the container containing the database.
              it is only checkd for existence and started when stopped.
        - $DOCKERNAME: This is the docker that containes the actual site
              The value of $DOCKERNAME is read from the site info using the key 'docker'
        If the site is a slave, and a transfer from the master to the slave is requested:
        - $MASTER_DOCKERNAME: this is the container name of the master site as found in sites.py.
        """
        name = self.site_name
        if name and self.sites.get(name):
            #erp_provider  = self.erp_provider
            if not self.docker_container_name:
                #print('the site description for %s has no docker description or no container_name' % self.site_name)
                return
            if self.subparser_name == 'docker':
                if not self.opts.docker_build_image:
                    # collect info on database container which normally is named 'db'
                    self.update_docker_info(self.docker_db_container_name, required=True)
                    self.update_docker_info(self.docker_container_name)

    # -------------------------------
    # check_and_create_container
    # checks if a docker container for the actual site exists
    # if not it is created and started
    # if it exists but not started it is started
    # --------------------------------
    def _create_container(self, docker_template, info_dic):
        """this is a helper method that does the actual creation of the container

        Arguments:
            template {string} -- template used to run docker create
            info_dic {dict} -- dictionary with info about values to use with the container

        Achtung:
            can not handle flectra update container
        """
        docker_info = {
            'erp_port' : info_dic['erp_port'],
            'erp_longpoll' : info_dic['erp_longpoll'],
            'site_name' : info_dic['site_name'],
            'container_name' : info_dic['container_name'],
            'remote_data_path' : info_dic['remote_data_path'],
            'erp_image_version' : info_dic['erp_image_version'],
            'erp_server_data_path' : info_dic['erp_server_data_path'],
            'docker_common' : info_dic['docker_common'], # values for the docker config
            'docker_command' : shutil.which('docker'),
        }
        docker_template = docker_template % docker_info
        mp = self.docker_path_map
        if mp and self.user != 'root':
            try:
                t, s = mp
                docker_template = docker_template.replace(s, t)
            except:
                pass
        docker_template = re.sub(' *= *', '=', docker_template)
        self.run_commands([docker_template], self.user, pw='')

    def check_and_create_container(self,
                                   container_name='',
            recreate_container=False,
            rename_container=False,
            pull_image=False,
            update_container=False,
            delete_container=False):
        """create a new docker container or manage an existing one

        Keyword Arguments:
            container_name {str} -- name of the container, mandatory (default: {''})
            rename_container {bool} -- rename the container by adding a time-stamp to its name (default: {False})
            pull_image {bool} -- pull an actual image from dockerhup (default: {False})
            update_container {bool} -- create a container, that runs etc/runodoo.sh as entrypoint. --stop-after-init (default: {False})

        Raises:
            ValueError -- [description]
        """

        name = self.site_name or container_name
        site = self.site
        base_info = self.base_info
        base_info['docker_command'] = shutil.which('docker')
        # constructs a dictionary with values to patch the docker files with
        info_dic = self.create_docker_composer_dict()
        if name == 'db':
            #self.update_docker_info('db')
            container_name = 'db'
            site = {
                'docker' : {
                    'container_name' : 'db',
                    'erp_port' : 'db',
                    'erp_longpoll' : 'db',
                    'erp_image_version' : 'db',
                }
            }
            erp_port = ''
            long_polling_port = ''
        else:
            site = self.site

            if not site:
                print(bcolors.FAIL)
                print('*' * 80)
                print('%s is not a known site' % name)
                print(bcolors.ENDC)
                return

            if not container_name:
                # get info on the docker container to use
                #'docker' : {
                    #'erp_image_version': 'odoo:9.0',
                    #'container_name'    : 'afbs',
                    #'erp_port'         : '8070',
                #},
                container_name = self.docker_container_name
            erp_port = self.docker_rpc_port
            if erp_port == '??':
                print(DOCKER_INVALID_PORT % (name, name))
                return()
            long_polling_port = self.docker_long_polling_port
            if long_polling_port == '??':
                print(DOCKER_INVALID_PORT % (name, name))
                return()

            allow_empty = ['list_db', 'log_db', 'logfile', 'server_wide_modules', 'without_demo', 'logrotate', 'syslog']
            if not delete_container and container_name != 'db':
                # make sure we have valid elements
                for k,v in info_dic.items():
                    if k == 'erp_image_version':
                        v = v.split(':')[0] # avoid empty image version with only tag
                    if not v and k not in allow_empty:
                        print(bcolors.FAIL)
                        print('*' * 80)
                        print('the value for %s is not set but is needed to create a docker container.' % k)
                        print('*' * 80)
                        print(bcolors.ENDC)
                        sys.exit()
            info_dic['docker_site_addons_path'] = self.docker_site_addons_path
            info_dic['docker_db_container_name'] = self.docker_db_container_name
            # some of the docker templates have many elements in common, get them
            from templates.docker_templates import docker_common as DC
            docker_common = DC % info_dic
            info_dic['docker_common'] = docker_common  # values for the docker config

            # if we are running as user root, we make sure that the
            # folders that are accessed from within odoo belong to the respective
            # we do that before we start the container, so it has immediat access
            if os.geteuid() == 0:
                # cd to the site folder, preserve old folder
                act_pwd = os.getcwd()
                t_folder = os.path.normpath('%s/%s' % (base_info['erp_server_data_path'], name))
                try:
                    os.chdir(t_folder)
                    user_and_group = self.docker_external_user_group_id
                    cmdlines = [
                        ['/bin/chown', user_and_group, 'log'],
                        ['/bin/chown', user_and_group, 'filestore', '-R'],
                    ]
                    for c in cmdlines:
                        os.system(' '.join(c))
                    #self.run_commands(cmdlines, self.user, pw='')
                    os.chdir(act_pwd)
                except OSError:
                    pass # no such folder

        if not info_dic.get('container_name'):
            info_dic['container_name'] = container_name

        if pull_image:
            image = self.erp_image_version
            if image:
                self.pull_image(image)

        elif rename_container:
            self.stop_container(container_name)
            n = str(datetime.datetime.now()).replace(':', '_').replace('.', '_').replace(' ', '_').replace('-', '_')
            self.rename_container(container_name, '%s.%s' % (container_name, n))

        elif recreate_container:
            # make sure the container is stopped
            from templates.docker_templates import docker_delete_template
            self.stop_container(container_name)
            self._create_container(docker_delete_template, info_dic)

        elif update_container:
            # create a container that runs etc/odoorunner.sh as entrypoint
            from templates.docker_templates import docker_template_update
            self._create_container(docker_template_update, info_dic)

        elif delete_container:
            from templates.docker_templates import docker_delete_template
            # make sure the container is stopped
            self.stop_container(container_name)
            info_dic['docker_common'] = ''
            self._create_container(docker_delete_template, info_dic)
            print('container %s deleted' % name)

        elif recreate_container or rename_container or self.docker_registry \
             and container_name or (container_name == 'db'):
            if container_name != 'db':
                from templates.docker_templates import docker_template, flectra_docker_template
                if self.erp_provider == 'flectra':
                    docker_template = flectra_docker_template
                # robert june 19, do not recreate if container allready exists
                if not self.docker_registry.get(container_name):
                    self._create_container(docker_template, info_dic)
                    print('created container %s' % name)
            else:
                # we need a postgres version
                pg_version = self.use_postgres_version
                if not pg_version:
                    print(bcolors.FAIL)
                    print('*' * 80)
                    print('you must define a postgres version like 10.0 in config/docker.yaml')
                    print('*' * 80)
                    print(bcolors.ENDC)
                    sys.exit()

                # here we need to decide , whether we run flectra or odoo
                if self.erp_provider == 'flectra':
                    from templates.docker_templates import flectra_docker_template
                else:
                    from templates.docker_templates import docker_db_template
                base_info['postgres_version'] = pg_version
                docker_template = docker_db_template % base_info
                from templates.docker_templates import logout_template
                logout_template = logout_template % base_info
                # just to be sure, we log out of docker, as the db base image is not created by us
                try:
                    self.run_commands([logout_template], user=self.user, pw='')
                except:
                    pass
                # now create the db container
                try:
                    self.run_commands([docker_template], user=self.user, pw='')
                    print('created database container')
                except:
                    pass # did exist allready ??
            if self.opts.verbose:
                print(docker_template)
        #else:
            #if self.opts.verbose:
                #print('container %s allready running' % name)

    def create_docker_composer_file(self):
        from templates.docker_compose import composer_template
        template = composer_template % self.create_docker_composer_dict()
        docker_target_path = '%s/%s/docker' % (self.erp_server_data_path, self.site_name)
        with open('%s/docker-compose.yml' % docker_target_path, 'w') as f:
            status = f.write(template)
        return status

    def create_docker_composer_dict(self):
        """constructs a dictionary with values to patch the docker files with

        Returns:
            dict -- dictionary with needed values
        """

        composer_dict = {
            # 'addons_path' : '%s%s' % (self.docker_defaults.get('docker_addons_base_path'), self.docker_site_addons_path),
            'erp_server_data_path' : self.erp_server_data_path,
            'site_name' : self.site_name,
            'container_name': self.docker_container_name,
            'erp_image_version' : self.erp_image_version,
            'docker_db_container_name' : self.docker_db_container_name,
            'erp_port': self.docker_rpc_port,
            'erp_longpoll': self.docker_long_polling_port,
            'docker_local_user_id' : self.docker_local_user_id,
            'db_host' : self.db_host,
            'db_name' : self.db_name,
            'db_user' : self.db_user,
            'db_password' : self.db_password,
            'db_sslmode' : self.docker_db_sslmode,
            'list_db' : self.docker_list_db,
            # in the following line, the $ needs to be escaped with a second $
            'dbfilter': '^%s$$' % self.site_name,
            'admin_passwd' : shlex.quote(self.docker_rpc_user_pw),
            'db_maxconn' : self.docker_db_maxcon,
            'limit_memory_soft' : self.docker_limit_memory_soft,
            'limit_memory_hard' : self.docker_limit_memory_hard,
            'limit_request' : self.docker_limit_request,
            'limit_time_cpu' : self.docker_limit_time_cpu,
            'limit_time_real' : self.docker_limit_time_real,
            'limit_time_real_cron' : self.docker_limit_time_real_cron,
            'log_handler' : self.docker_log_handler,
            'log_level' : self.docker_log_level,
            'max_cron_threads' : self.docker_max_cron_threads,
            'workers' : self.docker_workers,
            'logfile' : self.docker_logfile,
            'log_db' : self.docker_log_db,
            'running_env' : self.docker_running_env,
            'without_demo' : self.docker_without_demo,
            'server_wide_modules' : self.docker_server_wide_modules,
            # elements to contruct volum paths
            'remote_data_path' : self.remote_data_path,
            'logrotate' : self.docker_logrotate,
            'syslog' : self.docker_syslog,
        }
        return composer_dict


    def pull_image(self, imagename):
        """
        docker login
        docker tag e6861e4e5151 robertredcor/afbs:9.0
        docker push robertredcor/afbs
        """
        try:
            self.docker_client.pull(imagename)
            print(DOCKER_IMAGE_PULLED % (imagename, self.site_name))
        except docker.errors.NotFound:
            print(DOCKER_IMAGE_PULL_FAILED % (imagename, self.site_name))

    def push_image(self):
        """
        docker login
        docker tag e6861e4e5151 robertredcor/afbs:9.0
        docker push robertredcor/afbs
        """
        client = self.docker_client
        name = self.site_name
        site = self.site
        if not site:
            raise ValueError('%s is not a known site' % name)
        #docker_info = self.docker_info
        image = self.erp_image_version
        if image:
            images = [i['RepoTags'] for i in client.images()]
            found = False
            if images:
                for tags in images:
                    if not tags:
                        break
                    for tag in tags:
                        if tag == image:
                            found = True
                            break
                    if found:
                        break
        if not found:
            print(DOCKER_IMAGE_NOT_FOUND % image)
        self.dockerhub_login()
        result = client.push(image, stream=True)
        for line in result:
            print(line)

    def retag_image(self):
        """
        docker login
        docker tag e6861e4e5151 robertredcor/afbs:9.0
        docker push robertredcor/afbs
        """
        client = self.docker_client
        dirt_info = self.opts.docker_images_retag.split(':')
        if len(dirt_info) != 2:
            print(bcolors.FAIL)
            print('*' * 80)
            print('bad -dirt data: need ACTUAL-TAG:TARGET-TAG')
            print(bcolors.ENDC)
        images = [i['RepoTags'] for i in client.images()]
        # keep a list of images that start with the source name
        image, target = dirt_info
        found = []
        if images:
            for fullnames in images:
                if not fullnames:
                    break
                for fullname in fullnames:
                    i_name, tag = (fullname.split(':') + [''])[:2]
                    print(i_name, tag)
                    if i_name == image:
                        found.append((i_name, tag))
        if not found:
            print(DOCKER_IMAGE_NOT_FOUND % image)
        else:
            # we have to construct a new name for the images.
            # image:tag -> target:tag
            for image, tag in found:
                old_name = '%s:%s' % (image, tag)
                new_name = '%s:%s' % (target, tag)
                self.docker_client.tag(old_name, new_name)
                self.docker_client.remove_image(old_name)


    def dockerhub_login(self):
        client = self.docker_client
        site = self.site
        print(bcolors.WARNING)
        print('*' * 80)
        print('dockerhub_login needs to be reimplemented')
        print(bcolors.ENDC)
        return
        raise Exception('need to adapt dockerhub_login')
        docker_info = site['docker']
        hname =  docker_info.get('hub_name', 'docker_hub')
        if hname != 'docker_hub':
            raise ValueError('only docker_hub is suported when login in')
        hub_info = site['docker_hub'].get(hname)
        if not hub_info:
            print(DOCKER_IMAGE_PUSH_MISING_HUB_INFO % self.site_name)
        user = self.docker_hub_name
        pw = hub_info.get('docker_hub_pw')
        try:
            client.login(username=user, password=pw)
        except:
            raise ValueError('could  not log in to docker hub, user or pw wrong')

    def _clean_run_block(self, block):
        # make sure run_block is well formed
        block = block.strip()
        parts = block.split('\\')
        block = '\\'.join([p for p in parts if p])
        return block

    def build_dumper_image(self):
        """
        build dbdumper image
        """
        from templates.docker_templates import dumper_docker_template
        template = dumper_docker_template % {'postgres_version' : int(float(self.use_postgres_version))}
        docker_target_path = '%s/dumper/' % self.sites_home
        dumper_image = self.docker_defaults.get('docker_dumper_image')
        with open('%sDockerfile' % docker_target_path, 'w') as f:
            f.write(template)
        try:
            docker_file = '%sDockerfile' % docker_target_path
            from docker import APIClient
            cli = APIClient(base_url='unix://var/run/docker.sock')
            client = docker.DockerClient(base_url='unix://var/run/docker.sock')
            #result = self.docker_client.images.build(
            #print('----> starting')
            result = cli.build(
            #result = client.images.build(
            # result = self.docker_client.build(
                docker_target_path,
                tag=dumper_image,
                dockerfile=docker_file,
                rm=True,
            )
            build_info = []
            is_ok = self._print_docker_result(result, docker_file, docker_target_path, build_info)
            if is_ok:
                print(bcolors.OKGREEN)
                print('*' * 80)
                print('The dbdumper image has been created')
                print('please check executing: docker images')
                print('*' * 80)
                print(bcolors.ENDC)
            else:
                print(bcolors.FAIL)
                print('*' * 80)
                print('something is fishy in the state of danemark ..')
                print('the dbdumper image could not be created')
                print('*' * 80)
                print(bcolors.ENDC)

        except Exception as e:
            print(bcolors.FAIL)
            print('*' * 80)
            print('something is fishy in the state of danemark ..')
            print(str(e))
            print('*' * 80)
            print(bcolors.ENDC)

    def _print_docker_result(self, result, docker_file, docker_target_path, return_info=[]):
        """creating docker images provides no error code, we have to scruntinize the result

        Arguments:
            result {stream} -- what the docker build returned
            docker_file {string} -- in fact the Dockerfile to be build
            docker_target_path {string} -- the path to the Dockerfile

        Keyword Arguments:
            return_info {list} -- just a hack so we can give a nicer feedback with the last line read (default: {[]})

        Returns:
            list -- see above
        """

        is_ok = True
        return_info.append('')
        for line in result:
            line = eval(line.decode('utf-8'))
            if isinstance(line, dict):
                if line.get('errorDetail'):
                    print(DOCKER_IMAGE_CREATE_ERROR % (
                        self.site_name,
                        self.site_name,
                        line.get('errorDetail'),
                        docker_file,
                        docker_target_path))
                    is_ok = False
                status = line.get('status')
                if status:
                    print(line['status'].strip())
                    continue
                sl = line.get('stream')
                if sl:
                    print(line['stream'].strip())
                    return_info[0] = line['stream'].strip()

        return is_ok

    def build_image_bitnami(self):
        """[summary]
        """
        pass


    def build_image(self):
        """
        build image that has all python modules installed mentioned in the site description
        the base odo image is also read from the site description

        a docker image will only be built when the site description has a docker_hub block.
        """
        from templates.docker_templates import docker_base_file_template, docker_run_apt_template, docker_run_no_apt_template, \
             docker_erp_setup_requirements, docker_erp_setup_version, docker_erp_setup_script
        def apt_lines(block):
            if not block:
                return []
            result = ['apt-get install -y --no-install-recommends']
            pref = ' ' * 4
            for line in block:
                result.append(pref + line.strip())
            return result
        # do we have a dockerhub user?
        hub_name  = self.docker_hub_name
        if not hub_name:
            print(DOCKER_IMAGE_CREATE_MISING_HUB_INFO % self.site_name)
            return
        dockerhub_user = self.site.get('docker_hub', {}).get(hub_name, {}).get('user')
        dockerhub_user_pw = self.site.get('docker_hub', {}).get(hub_name, {}).get('docker_hub_pw')
        if not dockerhub_user or not dockerhub_user_pw:
            print(bcolors.WARNING)
            print('*' * 80)
            print(DOCKER_IMAGE_CREATE_MISING_HUB_USER % self.site_name)
            print("please edit the site description to be able to upload the image")
            print(bcolors.ENDC)

        # copy files from the official erp-sites docker file to the sites data directory
        # while doing so adapt the dockerfile to pull all needed elements
        erp_version = self.erp_version
        if not erp_version in list(ODOO_VERSIONS.keys()):
            print(ERP_VERSION_BAD % (self.site_name, self.site.get('erp_version', self.site.get('odoo_version'))))
            return

        #docker_source_path = '%s/docker/docker/%s/' % (self.default_values['erp_server_data_path'], erp_version)
        # get path to where we want to write the docker file
        docker_target_path = '%s/docker/' % self.site_data_dir
        if not os.path.exists(docker_target_path):
            os.makedirs(docker_target_path, exist_ok=True)

        # get the pip and apt libraries to include in the image
        apt_list = self.site_apt_modules
        pip_list = self.site_pip_modules

        # collect environment variables from the config/docker.yaml file
        image_envars = self.docker_image.get('environment', {})
        en_vars = ''
        if image_envars:
            envar_line = 'ENV  %s=%s\n'
            for k,v in image_envars.items():
                en_vars += (envar_line % (k.strip(), v.strip()))
        # collect extra build commands
        run_extra_run_block = ''
        extra_commands = self.site.get('docker_build_cmds', [])
        if extra_commands:
            for extra_command in extra_commands:
                run_extra_run_block += 'RUN %s\n' % extra_command.strip()

        with open('%sDockerfile' % docker_target_path, 'w' ) as result:
            data_dic = {
                'erp_image_version'  : self.docker_base_image
            }
            data_str = DOCKER_APT_PIP_HEAD
            if apt_list or pip_list:
                data_str += "RUN set -x; "
                pref = ' ' * 8
                if apt_list:
                    data_str += 'apt install -y '
                    data_str += self._clean_run_block('\n'.join(['%s%s \\' % (pref, a) for a in apt_list]))
                if pip_list:
                    #if apt_list:
                        #data_str += ';\\\n'
                    data_str += "\nRUN "
                    data_str += '    pip install --cache-dir=.pip '
                    data_str +=  (' '.join(['%s' % p for p in pip_list]))
            data_dic['run_block'] = data_str
            data_dic['env_vars'] = en_vars
            data_dic['run_extra_run_block'] = run_extra_run_block
            docker_file = (docker_base_file_template % data_dic).replace('\\ \\', '\\')
            result.write(docker_file)
        # construct folder layout as expected by the base image
        # see https://github.com/camptocamp/docker-odoo-project/tree/master/example
        print(bcolors.WARNING)
        print('*' * 80)
        print("Building folder structure exepected by the build process in %s" %
              docker_target_path)
        print(bcolors.ENDC)
        for f in ['external-src', 'local-src', 'data', 'features', 'songs']:
            try:
                td = '%s%s' % (docker_target_path, f)
                if not os.path.exists(td):
                    os.mkdir(td )
            except OSError:
                pass
        for f in [
            ('VERSION', docker_erp_setup_version % str(date.today())),
            ('migration.yml', ''),
            ('requirements.txt', docker_erp_setup_requirements),
            ('setup.py', docker_erp_setup_script),]:
            # do not overwrite anything ..
            fp = '%s%s' % (docker_target_path, f[0])
            if not os.path.exists(fp):
                open(fp, 'w').write(f[1])
            else:
                print('%s\n%s\n%s -> not overwitten %s' % (bcolors.WARNING, '-'*80, fp, bcolors.ENDC))
        # check out odoo source
        os.chdir(docker_target_path)
        # construct a valid version
        version = self.erp_version
        minor = self.erp_minor
        try:
            version = str(int(float(version)))
        except:
            print(bcolors.FAIL)
            print('*' * 80)
            print(DOCKER_IMAGE_CREATE_MISING_HUB_USER % self.site_name)
            print("%s is not a valid version. Please fix it in the sitedescription for site %s" % (version, self.site))
            print(bcolors.ENDC)
        if minor:
            version = ('%s.%s' % (version, minor)).replace('..', '.')

        if os.path.exists('src') and os.path.isdir('src'):
            o_dir = os.getcwd()
            os.chdir('src')
            print(bcolors.WARNING)
            print('*' * 80)
            print("Git upgrading existing %s" % os.getcwd())
            print(bcolors.ENDC)
            cmd_lines = [
                'git pull',
            ]
            self.run_commands(cmd_lines=cmd_lines)
            os.chdir(o_dir)
        else:
            print(bcolors.WARNING)
            print('*' * 80)
            print("Git clonig odoo source V%s to be included in the image to %s/src" %
                  (version, os.getcwd()))
            print(bcolors.ENDC)
            cmd_lines = [
                'git init .',
                'git submodule init',
                'git submodule add -b %s https://github.com/odoo/odoo.git src' % version

            ]
            self.run_commands(cmd_lines=cmd_lines)

        print(DOCKER_IMAGE_CREATE_PLEASE_WAIT)
        tag = self.erp_image_version
        return_info = []
        try:
            docker_file = '%sDockerfile' % docker_target_path
            from docker import APIClient
            cli = APIClient(base_url='unix://var/run/docker.sock')
            client = docker.DockerClient(base_url='unix://var/run/docker.sock')
            #result = self.docker_client.images.build(
            #print('----> starting')
            result = cli.build(
            #result = client.images.build(
                path = docker_target_path,
                tag = tag,
                dockerfile=docker_file,
                rm=True,
                quiet=False
            )
            if result:
                # https://techoverflow.net/2019/04/01/fixing-gcloud-warning-docker-credential-gcloud-not-in-system-path/
                is_ok = self._print_docker_result(result, docker_file, docker_target_path, return_info)
                if not is_ok:
                    return
        except docker.errors.NotFound:
            print(DOCKER_IMAGE_CREATE_FAILED % (self.site_name, self.site_name))
        else:
            result = return_info[0].split(' ')[-1]
            # the last line is something like:
            # {"stream":"Successfully built 97cea8884220\n"}
            print(DOCKER_IMAGE_CREATE_DONE % (
                self.site_name,result, dockerhub_user or 'YOUR_DOCKERHUB_ACCOUNT',
                result, self.site_name))

    def rename_container(self, name, new_name):
        """
        """
        try:
            self.docker_client.stop(name)
            self.docker_client.rename(name, new_name)
            print('renamed %s to %s' % (name, new_name))
        except:
            print('container %s nicht gefunden' % name)

    def stop_container(self, name=''):
        """
        """
        if not name:
            name = self.docker_container_name
        container = self.get_container(name)
        try:
            print('stoping container %s' % name)
            container.stop()
            print('stopped %s' % name)
        except docker.errors.NotFound:
            print('container %s nicht gefunden' % name)



    def start_container(self, name=''):
        """
        """
        if not name:
            name = self.site_name
        container = self.get_container(name)
        try:
            print('starting container %s' % name)
            container.start()
            print('started %s' % name)
        except docker.errors.NotFound:
            print('container %s nicht gefunden' % name)

    def restart_container(self, name=''):
        """
        """
        if not name:
            name = self.site_name
        container = self.get_container(name)
        try:
            print('restarting container %s' % name)
            container.restart()
            print('restarted %s' % name)
        except docker.errors.NotFound:
            print('container %s nicht gefunden' % name)

    def doTransfer(self):
        """
        """
        super().doTransfer()

    def checkImage(self, image_name):
        """
        """
        # todo should also check remotely
        image_list = self.docker_client.images.list(image_name)
        if image_list:
            return image_list[0]
        #return self.docker_client.images(image_name)

    #def _find_image(self, image_name):
        #"""
        #find an image by its tag
        #"""
        #name, tag = (image_name.split(':') + [''])[:2]
        #images = self.client.images()
        #for image in images:
            ## I assume that a repotag is always name:tag
            #for repo_tag in image.get('RepoTags', []):
                #n,t = repo_tag.split(':')
                #if n.lower() == name.lower():
                    #if tag:
                        #if tag.lower() == t.lower():
                            #return image
                    ## no tag, so accept any tag
                    #return image


    def doUpdate(self, db_update=True, norefresh=None, names=[], set_local=True):
        """
        set_local is not used yet
        """
        # self.update_container_info()
        # we need to learn what ip address the local docker db is using

        # we have to decide, whether this is a local or remote
        dumper_image = self.docker_defaults.get('docker_dumper_image')
        dumper_info = self.checkImage(dumper_image)
        if not dumper_info:
            print(bcolors.FAIL + \
                  'the %s image is not available. please create it first. ' \
                  'insturctions on how to do it , you find in %s/dumper' % (
                      dumper_image,
                      self.default_values['sites_home']),
                  '\nan easy way to do it is: bin/d -dbdumper' + bcolors.ENDC
                  )
            return
        # if the container does not yet exists, we create them (master and slave)
        self.check_and_create_container()
        get_remote_server_info(self.opts, self.sites)

        #mp = self.default_values.get('docker_path_map')
        #if mp and ACT_USER != 'root':
            #t, s = mp
            #remote_data_path = remote_data_path.replace(s, t)
        self.stop_container(self.site_name)
        self._doUpdate(db_update, norefresh, self.site_name, self.opts.verbose and ' -v' or '')

        # if we know admins password, we set it
        # for non docker pw is usualy admin, so we do not use it
        #adminpw = self.sites[self.site_name].get('erp_admin_pw')
        #if adminpw:
            #cmd_lines_docker += [['%s/psql' % where, '-U', user, '-d', site_name,  '-c', "update res_users set password='%s' where login='admin';" % adminpw]]

        self.start_container(self.site_name)


    def docker_install_own_modules(self, quiet=False):
        """
        """
        # get_module_obj
        db_info = self.docker_registry.get(self.site_name)
        if not db_info:
            print(bcolors.FAIL + 'no docker container %s running' % self.site_name + bcolors.ENDC)
            if self.opts.docker_start_container:
                print(bcolors.WARNING + 'it will be created' + bcolors.ENDC)
                self.check_and_create_container()
                self.update_container_info()
            else:
                return
        return self.install_own_modules( quiet=quiet)


    # shell
    # -----
    # shell runs and eneters a shell
    # in a docker container
    def run_shell(self):
        container_name = self.opts.shell
        print('docker exec -it %s bash' % container_name)
        os.system('docker exec -it %s bash' % container_name)
        return

    def execute_in_shell(self, cmd_lines):
        """
        execute_in_shell enters a container by its shell
        and executes a command
        Args:
            cmd_lines (list): This is a list of [commands] to be executed
                         within the shell

        Returns:
            tuple: (return_code, "error message")
        """
        import json
        class StreamLineBuildGenerator(object):
            def __init__(self, json_data):
                self.__dict__ = json.loads(json_data)

        # make sure container is up and running
        self.check_and_create_container()
        # this places info about the running container into the default_values
        docker_info = self.docker_registry.get(self.site_name)
        if not docker_info:
            print(bcolors.FAIL + 'no docker container %s running' % self.site_name + bcolors.ENDC)
            return
        # the docker id is used to access the running container
        container_id = docker_info['Id']
        # we need an interface to the docker engine
        cli = self.docker_client

        for cmds in cmd_lines:
            exe = cli.exec_create(container=container_id, cmd=cmds, tty=True, privileged=True)
            exe_start= cli.exec_start(exec_id=exe, stream=True, tty=True,)

            #for val in exe_start:
                #print (val)

            for line in exe_start:
                try:
                    stream_line = StreamLineBuildGenerator(line)
                    # Do something with your stream line
                    # ...
                except ValueError:
                    # If we are not able to deserialize the received line as JSON object, just print it out
                    print(line)
                    continue


        #http://stackoverflow.com/questions/35207295/docker-py-exec-start-howto-stream-the-output-to-stdout    # execute_in_shell


    def docker_add_ssh(self):
        """
        runs self.execute_in_shell and installs openssh server
        using apt get.
        It then creates a /root/.ssh folder in the container and
        copies the id_rsa.pub found in the local .ssh folder to
        the containers /root/.ssh/autorized_keys file

        Args:

        Returns:

        """
        try:
            key_pub = open(os.path.expanduser('~/.ssh/id_rsa.pub'), 'r').read()
        except:
            print(bcolors.FAIL, 'could not read %s' % os.path.expanduser('~/.ssh/id_rsa.pub'), bcolors.ENDC)
            return
        cmds = [
            ['/usr/bin/apt', 'update'],
            ['/usr/bin/apt', 'install', '-y', 'openssh-server'],
            ['mkdir', '-p', '/root/.ssh'],
            ['echo',  key_pub, '>', '/root/.ssh/authorized_keys'],
        ]
        self.execute_in_shell(cmds)

    def docker_start_ssh(self):
        """
        runs self.execute_in_shell and start openssh server
        Args:

        Returns:

        """
        cmds = [['service', 'ssh', 'start']]
        self.execute_in_shell(cmds)

    def docker_show(self, what='base'):
        """
        docker_show displays a list information about a containe
        Args:

        Returns:

        """
        # make sure container is up and running
        self.check_and_create_container()
        # this places info about the running container into the default_values
        docker_info = self.docker_registry.get(self.site_name)
        if not docker_info:
            print(bcolors.FAIL + 'no docker container %s running' % self.site_name + bcolors.ENDC)
            return
        # the docker id is used to access the running container
        indent = '    '
        if what == 'base':
            name = docker_info['Name']
            print('-' * len(name))
            print(name)
            print('-' * len(name))

            running = docker_info['State']['Running']

            print('running:', running and bcolors.OKGREEN, running, bcolors.ENDC)
            if running:
                print(indent, 'Pid:', docker_info['State']['Pid'])
                print(indent, 'StartedAt:', docker_info['State']['StartedAt'])
            print('Network settings')
            print('----------------')
            for n in ['IPAddress','Gateway']:
                print(indent, n, ':', docker_info['NetworkSettings'][n])
            print('Ports')
            print('-----')
            for k,v in list(docker_info['NetworkSettings']['Ports'].items()):
                print(indent, k, ':', v)
            print('Volumes')
            print('-------')
            for v in docker_info['Mounts']:
                print(indent, v['Destination'])
                print(indent * 2, v['Source'])
        else:
            if what != 'all':
                what = what.split[',']
            for k,v in list(docker_info.items()):
                if what != 'all' or not k in what:
                    print(k, ':')
                    if isinstance(v, (str, int)):
                        print(indent, v)
                    elif isinstance(v, (tuple, list)):
                        for elem in v:
                            if isinstance(elem, str):
                                print(indent * 2, elem)
                            elif isinstance(elem, dict):
                                for kk,vv in list(elem.items()):
                                    print(indent * 2, kk, ':', vv)
                                print(indent * 2, '-' * 10)
                    elif isinstance(v, dict):
                        for kk,vv in list(v.items()):
                            print(indent * 2, kk, ':', vv)
                        print(indent * 2, '-' * 10)


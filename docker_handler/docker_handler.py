#!bin/python
# -*- encoding: utf-8 -*-

#https://www.digitalocean.com/community/tutorials/how-to-set-up-a-private-docker-registry-on-ubuntu-14-04
from docker import Client
from config import BASE_PATH, SITES, BASE_INFO, DOCKER_DEFAULTS, ODOO_VERSIONS, PROJECT_DEFAULTS, APT_COMMAND, PIP_COMMAND #,DOCKER_FILES
#from config.handlers import InitHandler, DBUpdater
from scripts.create_handler import InitHandler
from scripts.update_local_db import DBUpdater
import os
import re
import sys
import shutil
from scripts.utilities import get_remote_server_info, bcolors
from scripts.messages import *
import docker
import datetime
from datetime import date

# DOCKER_APT_PIP_HEAD is used when constructing docker and either pip or 
# apt libraries needs to be merged in
DOCKER_APT_PIP_HEAD = """WORKDIR /odoo
RUN apt update;
"""

class DockerHandler(InitHandler, DBUpdater):
    master = '' # possible master site from which to copy
    def __init__(self, opts, sites=SITES, url='unix://var/run/docker.sock', use_tunnel=False):
        """
        """
        super().__init__(opts, sites)
        try:
            from docker import Client
        except ImportError:
            print('*' * 80)
            print('could not import docker')
            print('please run bin/pip install -r install/requirements.txt')
            return
        self.url = url
        cli = self.docker_client # self.default_values.get('docker_client')

        if not self.site:
            return # when we are creating the db container
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
        if name:
            # check whether a container with the requested name exists.
            # similar to docker ps -a, we need to also consider the stoped containers
            exists  = cli.containers(filters={'name' : name}, all=1)
            if exists:
                # collect info on the container
                # this is equivalent to docker inspect name
                try:
                    info = cli.inspect_container(name)
                except docker.errors.NotFound:
                    info = []
                if info:
                    if info['State']['Status'] != 'running':
                        if start:
                            cli.restart(name)
                            info = cli.containers(filters={'name' : name})
                            if not info:
                                raise ValueError('could not restart container %s', name)
                            info = info[0]
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
            docker = site_info.get('docker')
            if self.docker_container_name:
                print('the site description for %s has no docker description or no container_name' % opts.name)
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
        self.run_commands([docker_template], self.user, pw='')

    def check_and_create_container(self, container_name='', rename_container = False, pull_image = False, update_container=False, delete_container=False):
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
        BASE_INFO['docker_command'] = shutil.which('docker')
        if name == 'db':
            self.update_docker_info('db')
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
            raise ValueError('%s is not a known site' % name)
        docker_info = self.docker_info
        if not container_name:
            # get info on the docker container to use
            #'docker' : {
                #'erp_image_version': 'odoo:9.0',
                #'container_name'    : 'afbs',
                #'erp_port'         : '8070',
            #},        
            container_name = self.container_name
            erp_port = self.docker_rpc_port
            if erp_port == '??':
                print(DOCKER_INVALID_PORT % (name, name))
                return()
            long_polling_port = self.docker_long_polling_port
            if long_polling_port == '??':
                print(DOCKER_INVALID_PORT % (name, name))
                return()
            #if not long_polling_port:
            #    long_polling_port = int(erp_port) + 10000
            
        if pull_image:
            image = self.erp_image_version
            if image:
                self.pull_image(image)
            return
        if rename_container:
            self.stop_container(container_name)
            n = str(datetime.datetime.now()).replace(':', '_').replace('.', '_').replace(' ', '_').replace('-', '_')
            self.rename_container(container_name, '%s.%s' % (container_name, n))
        # if we are running as user root, we make sure that the 
        # folders that are accessed from within odoo belong to the respective 
        # we do that before we start the container, so it has immediat access
        if os.geteuid() == 0:
            # cd to the site folder, preserve old folder
            act_pwd = os.getcwd()
            t_folder = os.path.normpath('%s/%s' % (BASE_INFO['erp_server_data_path'], name))
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
        # the docker registry was created by update_docker_info
        # if this registry does not contain a description for container_name
        # we have to create it
        info_dic = {
            'erp_port' : erp_port,
            'erp_longpoll' : long_polling_port,
            'site_name' : name,
            'container_name' : container_name,
            'remote_data_path' : self.remote_data_path,
            'erp_image_version' : self.erp_image_version,
            'erp_server_data_path' : self.erp_server_data_path,           
        }
        # make sure we have valid elements
        for k,v in info_dic.items():
            if k == 'erp_image_version':
                v = v.split(':')[0] # avoid empty image version with only tag
            if not v:
                print(bcolors.FAIL)
                print('*' * 80)
                print('the value for %s is not set but is needed to create a docker container.' % k)
                print('*' * 80)
                print(bcolors.ENDC)
                sys.exit()                
        if update_container:
            # create a container that runs etc/odoorunner.sh as entrypoint
            from templates.docker_templates import docker_template_update
            self._create_container(docker_template_update, info_dic)
        elif delete_container:
            from templates.docker_templates import docker_delete_template
            # make sure the container is stopped
            self.stop_container(self.container_name)
            self._create_container(docker_delete_template, info_dic)
        elif rename_container or self.docker_registry \
            and self.container_name or (container_name == 'db'):
            if container_name != 'db':
                from templates.docker_templates import docker_template, flectra_docker_template
                if self.erp_provider == 'flectra':
                    docker_template = flectra_docker_template
                self._create_container(docker_template, info_dic)
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
                BASE_INFO['postgres_version'] = pg_version
                docker_template = docker_db_template % BASE_INFO
                try:
                    self.run_commands([docker_template], user=self.user, pw='')
                except:
                    pass # did exist allready ??
            if self.opts.verbose:
                print(docker_template)
        else:
            if self.opts.verbose:
                print('container %s allready running' % name)

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
        docker_info = self.docker_info
        image = self.erp_image_version
        if image:
            images = [i['RepoTags'] for i in client.images()]
            found = False
            for tags in images:
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
        

    def dockerhub_login(self):
        client = self.docker_client
        site = self.site
        docker_info = site['docker']
        hname =  docker_info.get('hub_name', 'docker_hub')
        if hname != 'docker_hub':
            raise ValueError('only docker_hub is suported when login in')
        hub_info = site['docker_hub'].get(hname)
        if not hub_info:
            print(DOCKER_IMAGE_PUSH_MISING_HUB_INFO % self.site_name)
        user = self.docker_hub_user
        pw = hub_info.get('docker_hub_user_pw')
        try:
            client.login(username=user, password=pw)
        except:
            raise ValueError('could  not log in to docker hub, user or pw wrong')
                
    def collect_extra_libs(self):
        """
        collect apt modules and pip libraries needed to construct image with expected capabilities
        we collect them from the actual site, and all sites named with the option -sites
        """
        extra_libs = self.site.get('extra_libs', {})        
        if self.opts.use_collect_sites:
            version = self.version
            more_sites = []
            for k, v in list(self.sites.items()):
                if v.get('erp_version') == version:
                    more_sites.append(k)
        else:
            more_sites = (self.opts.use_sites or '').split(',')
        # libraries we need to install using apt
        apt_list = extra_libs.get(APT_COMMAND, [])       
        # libraries we need to install using pip
        pip_list = extra_libs.get(PIP_COMMAND, [])  
        for addon in self.site.get('addons', []):
            pip_list += addon.get('pip_list', [])
            apt_list += addon.get('apt_list', [])
        for s in more_sites:
            if not s:
                continue
            site = self.sites.get(s)
            if not site:
                print((SITE_NOT_EXISTING % s))
                continue
            apt_list += site.get('extra_libs', {}).get(APT_COMMAND, [])
            pip_list += site.get('extra_libs', {}).get(PIP_COMMAND, [])
            for addon in self.site.get('addons', []):
                pip_list += addon.get('pip_list', [])
                apt_list += addon.get('apt_list', [])
            
        if apt_list:
            apt_list = list(set(apt_list))
        if pip_list:
            pip_list = list(set(pip_list))
        if self.opts.verbose:
            print(bcolors.WARNING)
            print('*' * 80)
            print('apt_list:%s' % apt_list)
            print('pip_list:%s' % pip_list)
            print(bcolors.ENDC)
        return apt_list, pip_list
    
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
        docker_target_path = '%s/dumper/' % BASE_PATH
        with open('%sDockerfile' % docker_target_path, 'w') as f:
            f.write(template)
        try:
            docker_file = '%sDockerfile' % docker_target_path
            result = self.docker_client.build(
                docker_target_path, 
                tag='dbdumper',
                dockerfile=docker_file)
            is_ok = self._print_docker_result(result, docker_file, docker_target_path)
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
            docker_file {strin} -- in fact the Dockerfile to be build
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

    def build_image(self):
        """
        build image that has all python modules installed mentioned in the site description
        the base odo image is also read from the site description
        
        a docker image will only be buildt when the site description has a docker_hub block.
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
        docker_info = self.site.get('docker', {})
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
        erp_version = self.site.get('erp_version', self.site.get('odoo_version'))
        if not erp_version in list(ODOO_VERSIONS.keys()):
            print(ERP_VERSION_BAD % (self.site_name, self.site.get('erp_version', self.site.get('odoo_version'))))
            return
        docker_source_path = '%s/docker/docker/%s/' % (self.default_values['erp_server_data_path'], erp_version)
        # get path to where we want to write the docker file
        docker_target_path = '%s/docker/' % self.default_values['data_dir']
        if not os.path.exists(docker_target_path):
            os.makedirs(docker_target_path, exist_ok=True)
        # there are some files we can copy unaltered
        #for fname in DOCKER_FILES[erp_version]:
            #shutil.copy('%s%s' % (docker_source_path, fname), docker_target_path)
        # construct dockerfile from template
        apt_list, pip_list = self.collect_extra_libs()
        #line_matcher = re.compile(r'\s+&& pip install.+')
        with open('%sDockerfile' % docker_target_path, 'w' ) as result:
            data_dic = {
               'erp_image_version'  : self.docker_base_image
            }
            data_str = DOCKER_APT_PIP_HEAD
            if apt_list or pip_list:
                data_str += "RUN set -x; \\"
                pref = ' ' * 8
                if apt_list:
                    data_str += 'apt install -y '
                    data_str += self._clean_run_block('\n'.join(['%s%s \\' % (pref, a) for a in apt_list]))
                if pip_list:
                    if apt_list:
                        data_str += ';\\\n'
                    data_str += '    pip install --cache-dir=.pip '
                    data_str +=  (' '.join(['%s' % p for p in pip_list]))
            data_dic['run_block'] = data_str     
            docker_file = (docker_base_file_template % data_dic).replace('\\ \\', '\\') 
            result.write(docker_file)
        # construct folder layout as expected by the base image
        # see https://github.com/camptocamp/docker-odoo-project/tree/master/example
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
        act = os.getcwd()
        os.chdir(docker_target_path)
        # construct a valid version
        version = self.version
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
                
        cmd_lines = [
            'git init .',
            'git submodule init',
            'git submodule add -b %s https://github.com/odoo/odoo.git src' % version
        ]
        self.run_commands(cmd_lines=cmd_lines)
        #for line in open( '%sDockerfile' % docker_source_path, 'r' ):
            #if line_matcher.match(line):
                #pip_line = line
                #pref = ' ' * 8
                ## write out all librarieds needed for the new python libraries to be
                ## installed by pip
                #for line in apt_lines(apt_list):
                    #result.write( pref + line + " \\\n")
                ## finally add the pip line embellished with our own list
                #result.write( pref + pip_line.strip() + ' '  + ' '.join([p.strip() for p in pip_list]) + '\n')
            #else:
                #result.write( line ) 
        print(DOCKER_IMAGE_CREATE_PLEASE_WAIT)
        tag = self.erp_image_version
        return_info = []
        try:
            docker_file = '%sDockerfile' % docker_target_path
            result = self.docker_client.build(
                docker_target_path, 
                tag = tag, 
                dockerfile=docker_file)
            is_ok = self._print_docker_result(result, docker_file, docker_target_path, return_info)
            if not is_ok:
                return
        except docker.errors.NotFound:
            print(DOCKER_IMAGE_CREATE_FAILED % (self.site_name, self.site_name))
        else:
            # the last line is something like:
            # {"stream":"Successfully built 97cea8884220\n"}
            print(DOCKER_IMAGE_CREATE_DONE % (dockerhub_user, return_info[0].split(' ')[-1], tag, tag))                

    def rename_container(self, name, new_name):
        """
        """
        try:
            self.docker_client.stop(name)
            self.docker_client.rename(name, new_name)
            print('rename %s to %s' % (name, new_name))
        except:
            print('container %s nicht gefunden' % name)

    def stop_container(self, name=''):
        """
        """
        if not name:
            name = self.container_name
        try:
            print('stoping container %s' % name)
            self.docker_client.stop(name)
            print('stopped %s' % name)
        except docker.errors.NotFound:
            print('container %s nicht gefunden' % name)
            
        

    def start_container(self, name=''):
        """
        """
        if not name:
            name = self.site_name
        print('starting container %s' % name)
        self.docker_client.start(name)
        print('started %s' % name)

    def restart_container(self, name=''):
        """
        """
        if not name:
            name = self.site_name
        print('restarting container %s' % name)
        self.docker_client.restart(name)
        print('restarted %s' % name)

    def doTransfer(self):
        """
        """
        super(dockerHandler, self).doTransfer()

    def checkImage(self, image_name):
        """
        """
        # todo should also check remotely
        return self.docker_client.images(image_name)

    def createDumperImage(self):
        """
        """
        act = os.getcwd()
        p = '%s/dumper' % self.sites_home
        os.chdir(p)
        self.run_commands([['docker build  -t dbdumper .']], self.user, pw='')
        os.chdir(act)

    def doUpdate(self, db_update=True, norefresh=None, names=[], set_local=True):
        """
        set_local is not used yet
        """
        # self.update_container_info()
        # we need to learn what ip address the local docker db is using
        # if the container does not yet exists, we create them (master and slave)
        self.check_and_create_container()
        server_dic = get_remote_server_info(self.opts)
        # we have to decide, whether this is a local or remote
        remote_data_path = server_dic['remote_data_path']
        dumper_image = BASE_INFO.get('docker_dumper_image')
        if not dumper_image:
            print(bcolors.FAIL + \
                  'the %s image is not available. please create it first. ' \
                  'insturctions on how to do it , you find in %s/dumper' % (
                      dumper_image,
                      self.default_values['sites_home'] + bcolors.ENDC))
        if not self.checkImage(dumper_image):
            self.createDumperImage()
            if not self.checkImage(dumper_image):
                print(bcolors.FAIL + \
                      'the %s image is not available. please create it first. ' \
                      'insturctions on how to do it , you find in %s/dumper' % (
                          dumper_image,
                          self.default_values['sites_home'] + bcolors.ENDC))
                return

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


    def docker_install_own_modules(self, list_only=False, quiet=False):
        """
        """
        if list_only:
            return install_own_modules(self.opts, self.default_values, list_only, quiet)
        # get_module_obj
        docker_info = self.docker_registry.get(self.site_name)
        db_info = self.docker_registry.get(self.site_name)
        if not db_info:
            print(bcolors.FAIL + 'no docker container %s running' % self.site_name + bcolors.ENDC)
            if self.opts.docker_start_container:
                print(bcolors.WARNING + 'it will be created' + bcolors.ENDC)
                self.check_and_create_container()
                self.update_container_info()
            else:
                return
        return self.install_own_modules( list_only, quiet)


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
        

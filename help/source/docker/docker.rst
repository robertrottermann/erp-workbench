----------------------------------------------------
Handling the docker containers used by erp-workbench
----------------------------------------------------

erp-workbench tries to blur the distinction of a site running locally or in a remote docker context.

Create an image to be used by a docker container
================================================

Settings within the site description
************************************
There are two parts in the description concerning docker behaviour:

* Creation of the container
::

    'docker': {
        'base_image': 'robertredcor/coobytech:11-latest',
        'erp_image_version': 'odoo:11',
        'container_name': 'coobytech',
        # 'db_container_name'    : 'db', # needs only to be set if it is not 'db'
        # trough what port can we access oddo (mapped to 8069)
        'erp_port': '9000',
        # trough what port can we access the sites long polling port (mapped to 8072)
        'erp_longpoll': '19000',
        # within the the container the erp user (odoo or flectra) has a user and group id that
        # is used to access the files in the log and filestore volumes
        'external_user_group_id': '104:107',
        # hub_name is the name to use to store our own images
        'hub_name': 'docker_hub',
        # ODOO_BASE_URL
        # If this variable is set, the `ir.config_parameter` `web.base.url`
        # will be automatically set to this domain when the container
        # starts. `web.base.url.freeze` will be set to `True`.
        'ODOO_BASE_URL': 'https://www.coobytech.ch'
    },

* Creation of image used by the container
Please make sure, that you provide credentials to acces the docker hub repository selected (robertrottermann in the following example)

::

    # docker_hub is used to store images we build ourself
    # by default we use dockers own docker_hub, but could
    # provide our own
    'docker_hub': {
        'docker_hub' : {
            'user' : 'robertredcor',
            # the password can either be provided verbatim
            # or merged in at creation time using the sites_pw.py facility
            'docker_hub_pw' : 'THEPASSWORD',
        }
    },

Creating a new image
********************

command:
::

    bin/d -dbi SITENAME

The following stepss are executed while creating a docker image:

- check credentials to docker hub

    Issue a warning if not found

- create a folder::

    $WB-DATA/$SITE/docker

    Within this folder checkout the odoo source code.
    What version is read from the site description.
    the source target folder is something like::

docker_source_path
'/home/robert/workbench/docker/docker/11/'
docker_target_path


docker_target_path
'/home/robert/workbench/coobytech/docker/'
        

Withing this folder the following subfolders are created

Then all extralibs are collected

apt
pip

Then a Dockerfile is constructed using the following code snippet::

        with open('%sDockerfile' % docker_target_path, 'w' ) as result:
            pref = ' ' * 8
            data_dic = {
               'erp_image_version'  : docker_info.get('base_image', 'camptocamp/odoo-project:%s-latest' % erp_version),
               'apt_list' : '\n'.join(['%s%s \\' % (pref, a) for a in apt_list]),
            }
            if pip_list:
                data_dic['pip_install'] = '&& pip install'
                data_dic['pip_list'] = (' '.join(['%s' % p for p in pip_list])) + ' \\'
            else:
                data_dic['pip_install'] = ''
                data_dic['pip_list'] = '\\'
                
            # depending whether there are python-libraries and or apt modules to install
            # we have to constuct a docker run block
            if apt_list:
                data_dic['run_block'] = docker_run_apt_template % data_dic
            elif pip_list:
                data_dic['run_block'] = docker_run_no_apt_template % data_dic
            else:
                data_dic['run_block'] = ''
            docker_file = (docker_base_file_template % data_dic).replace('\\ \\', '\\') 
            result.write(docker_file)

the Dockerfile constructed is simmilar to::            

    FROM robertredcor/coobytech:11-latest
    MAINTAINER robert@redo2oo.ch

    # Project's specifics packages
    RUN set -x; \
            && pip install twilio email_validator phonenumbers xlrd sqlalchemy mysqlclient \


    COPY ./requirements.txt /opt/odoo/
    RUN cd /opt/odoo && pip install -r requirements.txt

    ENV ADDONS_PATH=/opt/odoo/local-src,/opt/odoo/src/addons
    #ENV DB_NAME=afbsdemo
    ENV MIGRATE=False
    # Set the default config file
    ENV OPENERP_SERVER /etc/odoo/openerp-server.conf


Next a set of subfolders the camptocamp docker process expect are created::

        # construct folder layout as expected by the base image
        # see https://github.com/camptocamp/docker-odoo-project/tree/master/example
        for f in ['external-src', 'local-src', 'data', 'features', 'songs']:
            try:
                td = '%s%s' % (docker_target_path, f)
                if not os.path.exists(td):
                    os.mkdir(td )
            except OSError: 
                pass

construct some auxiliary files needed::

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
                print('%s\n%s\n%snot overwitten %s' % (bcolors.WARNING, '-'*80, fp, bcolors.ENDC))

Now get the odoo source code::

        os.chdir(docker_target_path)
        cmd_lines = [
            'git init .',
            'git submodule init',
            'git submodule add -b %s https://github.com/odoo/odoo.git src' % PROJECT_DEFAULTS.get('erp_nightly')
        ]
        self.run_commands(cmd_lines=cmd_lines)

and finally create the image wich can last a couple of minutes::

            result = self.default_values['docker_client'].build(
                docker_target_path, 
                tag = tag, 
                dockerfile = '%sDockerfile' % docker_target_path)


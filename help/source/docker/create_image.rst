----------------------
Creating docker images
----------------------

erp-workbench tries to blur the distinction of a site running locally or in a remote docker context.

Create an image to be used by a docker container
================================================

Steps to create a docker image
******************************

Adapt the site-description as needed for the project and execute::

    bin/d -dbi SITENAME

Assuming that we use the following example, this will create a new docker image
based on 'camptocamp/odoo-project:11.0-latest' which will be fetched from docker hub.
The new image will then be tagged 'coobyhq/odoo-project:11.0-latest', redy to be uploaded 
to the docker hub.

the result should be something like::

    --------------------------------------------
    Finished to create docker image.
    Now it is the appropriate time to tag and upload it to
    your docker hub account.
    Todo so, make sure that you computer is logged into
    your docker hub account and then 
    please execute the following commands:

    docker login -u coobyhq
    docker tag coobyhq/odoo-project:11.0-latest coobyhq/odoo-project:11.0-latest
    docker push coobyhq/odoo-project:11.0-latest
    ---------------------------------------------


Settings within the site description
************************************
There are two parts in the description concerning image creation:

* Creation of the image and the container::

    'docker': {
        # when BUILDING an new image: on what image are we basing this new image
        'base_image'        : 'camptocamp/odoo-project:11.0-latest',
        # when CREATING a container: what image do we use for it
        'erp_image_version': 'coobyhq/odoo-project:11.0-latest',
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

* Taging the image::

    Please make sure, that you provide credentials to acces the docker hub repository 
    otherwise you get a warning::

    # docker_hub is used to store images we build ourself
    # by default we use dockers own docker_hub, but could
    # provide our own
    'docker_hub': {
        'docker_hub' : {
            'user' : 'coobyhq',
            'docker_hub_pw' : '',
        }
    },

Making sure os- and python-libraries are added to the image
***********************************************************

In the part extra_libs of the site description you can add entries
to the pip- resp. apt- list::

    # extra libraries needed to be installed by pip or apt
    # this is used in two places
    # 1. pip installs are executed when creating a site on the local computer
    #    and executing bin/dosetup [-f] in the sites buildout directory
    # 2. both pip and apt installs are executed when a docker image is created
    'extra_libs': {
        'pip' : [
            'xlrd',
            'email_validator',
            'twilio',
            'mysqlclient',
            'sqlalchemy',
            'phonenumbers',
        ],
        'apt' : [
            'python-dev',
            'libmysqlclient-dev',
        ]
    },

These elements will be installed into the generated image.


command within the erp workbench:
::

    bin/d -dbi SITENAME

Steps executed while creating a docker image:
*********************************************

- check credentials to docker hub

    Issue a warning if not found

- create a folder::

    $WB-DATA/$SITE/docker

- Within this folder checkout the odoo source code.
    What odoo-version to use is read from the site description.
    the source target folder is something like::

        # path to copy odoo source to
        docker_source_path: '~/workbench/docker/docker/11/'
        # path to construct needed folder structure
        docker_target_path: '~/workbench/coobytech/docker/'
        

* Within docker_target_path folder the following files and folders are created. Their function is explained on the cmaptocamp docker-hub page::

    data/
    Dockerfile
    external-src/
    features/
    .git/
    .gitmodules
    local-src/
    migration.yml
    requirements.txt
    setup.py
    songs/
    src/
    VERSION


* Next all extralibs are collected.

* Next a Dockerfile is constructed using the following code snippet. The Dockerfile constructed using the obove examples is simmilar to::            

    FROM camptocamp/odoo-project:11.0-latest
    MAINTAINER robert@redo2oo.ch

    # For installing odoo you have two possibility
    # 1. either adding the whole root directory
    #COPY . /odoo

    # 2. or adding each directory, this solution will reduce the build and download
    # time of the image on the server (layers are reused)
    COPY ./src /odoo/src
    COPY ./external-src /odoo/external-src
    COPY ./local-src /odoo/local-src
    COPY ./data /odoo/data
    COPY ./songs /odoo/songs
    COPY ./setup.py /odoo/
    COPY ./VERSION /odoo/
    COPY ./migration.yml /odoo/
    RUN pip install --cache-dir=.pip -e /odoo
    RUN pip install --cache-dir=.pip -e /odoo/src


                WORKDIR /odoo
                RUN apt update;
                RUN set -x; \
                apt install -y default-libmysqlclient-dev \
            libffi-dev \
            python3-dev \
            libxml2-dev \
            libxslt1-dev \
            build-essential \
            python-dev \
            zlib1g-dev \
            libssl-dev ;\
        pip install --cache-dir=.pip twilio xlrd mysql-connector phonenumbers email_validator sqlalchemy validate_email

    COPY ./requirements.txt /opt/odoo/
    RUN cd /opt/odoo && pip install --cache-dir=.pip -r requirements.txt

    ENV ADDONS_PATH=/opt/odoo/local-src,/opt/odoo/src/addons
    #ENV DB_NAME=afbsdemo
    ENV MIGRATE=False
    # Set the default config file
    ENV OPENERP_SERVER /etc/odoo/openerp-server.conf

* Next a set of subfolders the camptocamp docker process expect are created::

        # construct folder layout as expected by the base image
        # see https://github.com/camptocamp/docker-odoo-project/tree/master/example
        for f in ['external-src', 'local-src', 'data', 'features', 'songs']:
            try:
                td = '%s%s' % (docker_target_path, f)
                if not os.path.exists(td):
                    os.mkdir(td )
            except OSError: 
                pass

* Next construct some auxiliary files needed::

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

* Now get the odoo source code::

        os.chdir(docker_target_path)
        cmd_lines = [
            'git init .',
            'git submodule init',
            'git submodule add -b %s https://github.com/odoo/odoo.git src' % PROJECT_DEFAULTS.get('erp_nightly')
        ]
        self.run_commands(cmd_lines=cmd_lines)

* and finally create the image wich can last a couple of minutes.

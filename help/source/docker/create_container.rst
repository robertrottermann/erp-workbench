---------------------------
Creating a docker container
---------------------------

The following assumes we handle a site called coobytech!

Preparation
-----------

- make sure there is a database container running
    if not create it::
    
        bin/d -dcdb

- in the site-description define what image to use, set the ports at which the site should be accessible and the site url

    ::

        'docker': {
                ...
                # when CREATING a container: what image do we use for it
                'erp_image_version': 'coobyhq/odoo-project:11.0-latest',
                ...
                # trough what port can we access oddo (mapped to 8069)
                'erp_port': '9000',
                # trough what port can we access the sites long polling port (mapped to 8072)
                'erp_longpoll': '19000',
                ...
                'ODOO_BASE_URL': 'https://www.coobytech.ch'
        },

    to edit the coobytech site-description execute::

        bin/e coobytech

- make sure the image to build the container on ('coobyhq/odoo-project:11.0-latest' in the above example) exists and is accessible.
- make sure the files in the coobytech folder are accessible from "outside" (since a docker container is like some other pc)

::

    chmod 777 coobytech -R


Create the container
--------------------

::

    bin/d -dc coobytech

check if it is running
----------------------

::

    docker ps

The output should be something like::

    CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                                                 NAMES
    564893d5cabf        e522607d61fb        "docker-entrypoint..."   14 hours ago        Up 13 hours         127.0.0.1:9000->8069/tcp, 127.0.0.1:19000->8072/tcp   coobytech
    f1ddc44cf38b        postgres:10.0       "docker-entrypoint..."   10 days ago         Up 14 hours         0.0.0.0:55432->5432/tcp                               db


Caveats
-------

When for some reason a container was created but not started up properly, chances are that the containers database was only created partially.
Such a partial database **MUST** be deleted for the container to start up properly.

Troubleshooting
---------------

A docker container runs als long as its main process (the one with pid 1) is running. Then it terminates.
erp-workbench creates its containers with the -d flag which instructs the docker engine to restart the container
automatically until it is explicitly stopped.

Therefore when the containers main process crashes because its environment is bad docker is constantly restarting the container.
This can easily be spotted when the uptime listed in the output of the ps command is only a few seconds and the status is "restarting"

There are some tools you can use to investigate the reason for this::

    docker logs -f coobytech

this "tails" the logs written by the docker daemon, and could give hints what is the cause of the failure. The root cause
is probably a bad image in the ancestry of the container.

When the container comes up but the site is not accessible in the browser you can check the odoo logs::

    tail -f coobytech/log/odoo_log

When the container comes up you can also start a bash shell to "enter" it::

    docker exec -it coobytech bash

Or when you have installed roberts superduper aliases (https://gitlab.redcor.ch/open-source/aliases.git)::

    de coobytech


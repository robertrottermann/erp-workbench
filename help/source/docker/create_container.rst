---------------------------
Creating a docker container
---------------------------

The foolwing assumes we handle a site called coobytech!

Preparation
-----------

- make sure there is a database container running
- in the site-description set the ports at which the site should be accessible and the site url::

        'docker': {
        ...
        # trough what port can we access oddo (mapped to 8069)
        'erp_port': '9000',
        # trough what port can we access the sites long polling port (mapped to 8072)
        'erp_longpoll': '19000',
        ...
        'ODOO_BASE_URL': 'https://www.coobytech.ch'
    },

to edit the coobytech site-descrition execute::

    bin/e coobytech

Create the container
--------------------

::

    bin/d -dc coobytech

Caveats
-------

When for some reason a container was created but not started up properly, that the continers database was only created partially.
Such a partial database **MUST** be deleted for the container to start up properly.
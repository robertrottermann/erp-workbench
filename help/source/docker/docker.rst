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


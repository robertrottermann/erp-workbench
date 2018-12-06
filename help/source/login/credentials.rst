Provide credentials at runtime
==============================

To provide credentials dynamically erp-workbench loads a file *sites_pw.py*
at startup.
From this file **SITES_PW** is imported.
SITES_PW is a dictonary of dictonaries with the following minimal set of fields:

:: 

    SITENAME {
        'odoo_admin_pw' : 'A SUPERSECRET SECRET',
        ...
    }


Example::

    #!/usr/bin/python
    # -*- encoding: utf-8 -*-

    SITES_PW = {
        # docker hub is special, as it has no odoo_admin_pw
        'docker_hub' : {
            'docker_hub' : {
                'robertredcor' : {'docker_hub_pw' : 'RottiTheGreyt'}
            }
        },
        "aerohrone" : {
            'odoo_admin_pw' : 'PasswordForAeroRhone',
            'email_pw_incomming' : 'PasswordForAeroRhone',
            'email_pw_outgoing' : '',
        },
        "afbsdemo" : {
            'odoo_admin_pw' : 'afbsdemo$77',
            'email_pw_incomming' : 'afbsdemo$77',
            'email_pw_outgoing' : 'afbsdemo$77',
        },
    }

All the fields of the credentials dict are merged into the site description with 
the name of the key used in  SITES_PW.
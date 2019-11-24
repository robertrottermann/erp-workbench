import os
"""
in the server section of a migration stanza
the following values are read in preparation to create the upgrade config
    - host -> db_host
    - port -> db_port
    - user -> db_user
    - password -> db_password
"""
migrations = {
    '12.0': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '12.0',
            'addons_dir': os.path.join('odoo', 'addons'),
            'root_dir': os.path.join(''),
            'cmd': 'odoo-bin --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc',
            },
    },
    '11.0': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '11.0',
            'addons_dir': os.path.join('odoo', 'addons'),
            'root_dir': os.path.join(''),
            'cmd': 'odoo-bin --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc',
            },
    },
    '10.0': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '10.0',
            'addons_dir': os.path.join('odoo', 'addons'),
            'root_dir': os.path.join(''),
            'cmd': 'odoo-bin --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc',
            },
    },
    '9.0': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '9.0',
            'addons_dir': os.path.join('openerp', 'addons'),
            'root_dir': os.path.join(''),
            'cmd': 'openerp-server --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc',
            },
    },
    '8.0': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '8.0',
            'addons_dir': os.path.join('openerp', 'addons'),
            'root_dir': os.path.join(''),
            'cmd': 'openerp-server --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc',
            },
    },
    '7.0': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '7.0',
            'addons_dir': os.path.join('openerp', 'addons'),
            'root_dir': os.path.join(''),
            'cmd': 'openerp-server --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc '
                   '--no-netrpc',
        },
    },
    '6.1': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '6.1',
            'addons_dir': os.path.join('openerp', 'addons'),
            'root_dir': os.path.join(''),
            'cmd': 'openerp-server --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc '
                   '--no-netrpc',
        },
    },
    '6.0': {
        'addons': {
            'addons': {
                'type': 'link',
                'url': os.path.join('server', 'addons'),
            },
        },
        'server': {
            'type': 'git',
            'url': 'git://github.com/OpenUpgrade/OpenUpgrade.git',
            'branch': '6.0',
            'addons_dir': os.path.join('bin', 'addons'),
            'root_dir': os.path.join('bin'),
            'cmd': 'bin/openerp-server.py --update=all --database=%(db)s '
                   '--config=%(config)s --stop-after-init --no-xmlrpc '
                   '--no-netrpc',
        },
    },
}

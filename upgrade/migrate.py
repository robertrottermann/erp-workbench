#!/usr/bin/env python3

try:
    import wingdbstub
except ImportError:
    pass
import os
import sys
import psycopg2
import psycopg2.extensions
from optparse import OptionParser
from configparser import ConfigParser
from functools import reduce
import getpass
sys.path.insert(0, '..')
from scripts import bcolors
from migrations import migrations

# check whether openupgradelb ist installed
try:
    import openupgradelib
except ImportError:
    print(bcolors.FAIL)
    print('*' * 80)
    print('is not installed')
    print('please run:')
    print('git clone --single-branch --depth=1 %(url)s %(target)s' % {
        'url': 'https://github.com/OCA/openupgradelib',
        'target': 'openupgradelib',
        })
    print('    and then cd openupgradelib;python setup.py install')
    print()
    print('in your active workbench environment')
    print(bcolors.ENDC)
    sys.exit()


class migration_handler(object):
    conn_parms = {}
    config = ConfigParser()
    verbose = False

    def __init__(self, options, parser):
        self.options = options
        self.parser = parser
        self.verbose = options.verbose
        # we need at least on migration
        if not options.config or not options.migrations\
                or not reduce(lambda a, b: a and (b in migrations),
                              options.migrations.split(','),
                              True):
            parser.print_help()
            sys.exit(5)

        # are the migrations valid
        for version in options.migrations.split(','):
            if version not in migrations:
                print(('%s is not a valid version! (valid verions are %s)' % (
                    version,
                    ','.join(sorted([a for a in migrations])))
                ))

        # read the config file of the source site
        # it will be used to construct a temporary config file used while migrating
        self.config.read(options.config)

        conn_parms = self.conn_parms
        for parm in ('host', 'port', 'user', 'password'):
            db_parm = 'db_' + parm
            if config.has_option('options', db_parm):
                value = config.get('options', db_parm)
                if value == 'False':
                    continue
                conn_parms[parm] = value

        if 'user' not in conn_parms:
            conn_parms['user'] = getpass.getuser()

        # get the source db name
        db_name = options.database or config.get('options', 'db_name')

        if not db_name or db_name == '' or db_name.isspace()\
                or db_name.lower() == 'false':
            parser.print_help()
            sys.exit(2)

        conn_parms['database'] = db_name
        conn_parms['new_database'] = options.new_database

        # the following folder will be used to copy version depending files
        if not os.path.exists(options.branch_dir):
            os.mkdir(options.branch_dir)


    def copy_database(self):
        conn_parms = self.conn_parms
        db_old = conn_parms['database']
        db_new = conn_parms.get('new_database')
        if not db_new:
            db_new = '%s_migrated' % conn_parms['database']
        del conn_parms['new_database'] # not used anymore
        print(('copying database %(db_old)s to %(db_new)s...' % {'db_old': db_old,
                                                                'db_new': db_new}))
        if conn_parms.get('host') == 'False':
            del conn_parms['host']
            del conn_parms['port']
        conn = psycopg2.connect(**conn_parms)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute('drop database if exists "%(db)s"' % {'db': db_new})
        try:
            print("Copying the database using 'with template'")
            sql = 'create database "%(db_new)s" with template "%(db_old)s"' % {'db_new': db_new, 'db_old': db_old}
            print(sql)
            cur.execute(sql)
            cur.close()
        except psycopg2.OperationalError:
            print("Failed, fallback on creating empty database + loading a dump")
            cur.execute('create database "%(db)s"' % {'db': db_new})
            cur.close()

            os.environ['PGUSER'] = conn_parms['user']
            if conn_parms.get('host') and not os.environ.get('PGHOST'):
                os.environ['PGHOST'] = conn_parms['host']

            if conn_parms.get('port') and not os.environ.get('PGPORT'):
                os.environ['PGPORT'] = conn_parms['port']

            password_set = False
            if conn_parms.get('password') and not os.environ.get('PGPASSWORD'):
                os.environ['PGPASSWORD'] = conn_parms['password']
                password_set = True

            os.system(
                ('pg_dump --format=custom --no-password %(db_old)s ' +
                 '| pg_restore --no-password --dbname=%(db_new)s') %
                {'db_old': db_old, 'db_new': db_new}
            )

            if password_set:
                del os.environ['PGPASSWORD']
        return db_new

    def run_upgrade(self):
        options = self.options
        config = self.config
        for version in options.migrations.split(','):
            if not os.path.exists(os.path.join(options.branch_dir, version)):
                os.mkdir(os.path.join(options.branch_dir, version))
            for (name, addon_config) in dict(migrations[version]['addons'], server=migrations[version]['server']).items():
                if isinstance(addon_config, dict):
                    addon_config = addon_config
                else:
                    addon_config = {'url': addon_config}
                addon_config_type = addon_config.get('type', 'git')
                # we want to make sure, that a valid structure for the addons exist
                if os.path.exists(os.path.join(options.branch_dir, version, name)):
                    if addon_config_type == 'link':
                        continue
                    elif addon_config_type == 'git':
                        cmd_line = 'cd %(location)s; git pull origin %(branch)s' % {
                            'branch': addon_config.get('branch', 'master'),
                            'location': os.path.join(options.branch_dir,
                                                     version,
                                                     name),
                        }
                        if self.verbose:
                            print(cmd_line)
                        os.system(cmd_line)
                    else:
                        raise Exception('Unknown type %s' % addon_config_type)
                else:
                    if addon_config_type == 'link':
                        print(('linking %s to %s' % (addon_config['url'],
                                                    os.path.join(options.branch_dir,
                                                                 version,
                                                                 name))))
                        os.symlink(addon_config['url'],
                                   os.path.join(options.branch_dir, version, name))
                    elif addon_config_type == 'git':
                        print(('getting ' + addon_config['url']))
                        result = os.system('git clone --branch %(branch)s --single-branch --depth=1 %(url)s %(target)s' %
                                           {
                                                  'branch': addon_config.get('branch', 'master'),
                                                  'url': addon_config['url'],
                                                  'target': os.path.join(options.branch_dir,
                                                                         version,
                                                                         name),
                                           })
                        if result != 0:
                            print("Could not clone version")
                            sys.exit(6)
                    else:
                        raise Exception('Unknown type %s' % addon_config_type)
            # copy database ??
            db_name = self.conn_parms['database']
            if not options.inplace:
                db_name = self.copy_database()

            print(('running migration for '+version))
            config.set('options', 'without_demo', 'True')
            config.set('options', 'logfile', logfile)
            config.set('options', 'port', 'False')
            config.set('options', 'netport', 'False')
            config.set('options', 'xmlrpc_port', 'False')
            config.set('options', 'netrpc_port', 'False')
            config.set(
                'options',
                'addons_path',
                ','.join(
                    [os.path.join(options.branch_dir,
                                  version,
                                  'server',
                                  migrations[version]['server']['addons_dir'])] +
                    [os.path.join(options.branch_dir,
                                  version,
                                  name,
                                  addon_conf.get('addons_dir', '')
                                  if isinstance(addon_conf, dict) else '')
                     for (name, addon_conf)
                     in migrations[version]['addons'].items()]))
            config.set(
                'options',
                'root_path',
                os.path.join(
                    options.branch_dir,
                    version,
                    'server',
                    migrations[version]['server']['root_dir']))
            if options.force_deps:
                if not config.has_section('openupgrade'):
                    config.add_section('openupgrade')
                config.set('openupgrade', 'force_deps', options.force_deps)
            config.write(
                open(
                    os.path.join(options.branch_dir, version, 'server.cfg'), 'w+'))

            print(("copied %s to %s_migration" % (db_name, db_name)))
            print((os.path.join(
                options.branch_dir,
                version,
                'server',
                migrations[version]['server']['cmd'] % {
                    'db': db_name,
                    'config': os.path.join(options.branch_dir, version,
                                           'server.cfg')
                })))
            print('please run the above command manually')


def main(options, parser):
    handler = migration_handler(options, parser)
    if options.force_deps:
        try:
            eval(options.force_deps)
        except:
            parser.print_help()
            sys.exit(3)

    if options.add:
        merge_migrations = {}
        if os.path.isfile(options.add):
            import imp
            merge_migrations_mod = imp.load_source('merge_migrations_mod',
                                                   options.add)
            merge_migrations = merge_migrations_mod.migrations
        else:
            try:
                merge_migrations = eval(options.add)
            except:
                parser.print_help()
                sys.exit(4)

        def deep_update(dict1, dict2):
            result = {}
            for (name, value) in dict1.items():
                if name in dict2:
                    if isinstance(dict1[name], dict) and isinstance(dict2[name],
                                                                    dict):
                        result[name] = deep_update(dict1[name], dict2[name])
                    else:
                        result[name] = dict2[name]
                else:
                    result[name] = dict1[name]
            for (name, value) in dict2.items():
                if name not in dict1:
                    result[name] = value
            return result

        migrations = deep_update(migrations, merge_migrations)
    handler.run_upgrade()

config = ConfigParser()
parser = OptionParser(
    description='Migrate script for the impatient or lazy. '
    'Makes a copy of your database, downloads the files necessary to migrate '
    'it as requested and runs the migration on the copy (so your original '
    'database will not be touched). While the migration is running only '
    'errors are shown, for a detailed log see ${branch-dir}/migration.log')
parser.add_option(
    "-C", "--config", action="store", type="string",
    dest="config",
    help="current openerp config (required)")
parser.add_option(
    "-D", "--database", action="store", type="string",
    dest="database",
    help="current openerp database (required if not given in config)")
parser.add_option(
    "-N", "--new_database", action="store", type="string",
    dest="new_database",
    help="name of the new  database")
parser.add_option(
    "-B", "--branch-dir", action="store", type="string",
    dest="branch_dir",
    help="the directory to download openupgrade-server code to [%default]",
    default='/var/tmp/openupgrade')
parser.add_option(
    "-R", "--run-migrations", action="store", type="string",
    dest="migrations",
    help="comma separated list of migrations to run, ie. \"" +
    ','.join(sorted([a for a in migrations])) +
    "\" (required)")
parser.add_option(
    "-U", "--user", action="store", type="string",
    dest="user",
    help="username, default=" + getpass.getuser())
parser.add_option(
    "-v", "--verbose", action="store_true",
    dest="verbose",
    help="be verbose")
parser.add_option(
    "-A", "--add", action="store", type="string", dest="add",
    help="load a python module that declares a dict "
    "'migrations' which is merged with the one of this script "
    "(see the source for details). You also can pass a string "
    "that evaluates to a dict. For the banking addons, pass "
    "\"{'6.1': {'addons': {'banking': 'lp:banking-addons/6.1'}}}\"")
parser.add_option("-I", "--inplace", action="store_true", dest="inplace",
                  help="don't copy database before attempting upgrade "
                  "(dangerous)")
parser.add_option(
    "-F", "--force-deps", action="store", dest="force_deps",
    help="force dependencies from a dict of the form \"{'module_name': "
    "['new_dependency1', 'new_dependency2']}\"")
(options, args) = parser.parse_args()
# where is logfile used?
logfile = os.path.join(options.branch_dir, 'migration.log')

main(options, parser)



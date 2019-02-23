#!bin/python
# -*- encoding: utf-8 -*-

#https://www.digitalocean.com/community/tutorials/how-to-set-up-a-private-docker-registry-on-ubuntu-14-04
#from config.handlers import InitHandler, DBUpdater
import os
import sys
import shutil
import tempfile
import zipfile
import configparser
import json
import subprocess

from scripts.create_handler import InitHandler
from scripts.update_local_db import DBUpdater
from scripts.bcolors import bcolors
from contextlib import contextmanager
from scripts.messages import DOCKER_DB_MISSING  # , DOCKER_DB_MISSING, DOCKER_INVALID_PORT, \
#       DOCKER_INVALID_PORT, DOCKER_IMAGE_PULLED, DOCKER_IMAGE_PULL_FAILED, DOCKER_IMAGE_NOT_FOUND, \
#       DOCKER_IMAGE_PUSH_MISING_HUB_INFO, SITE_NOT_EXISTING, DOCKER_IMAGE_CREATE_ERROR, \
#       DOCKER_IMAGE_CREATE_MISING_HUB_INFO, DOCKER_IMAGE_CREATE_MISING_HUB_USER, ERP_VERSION_BAD, \
#       DOCKER_IMAGE_CREATE_MISING_HUB_USER, DOCKER_IMAGE_CREATE_PLEASE_WAIT, DOCKER_IMAGE_CREATE_FAILED, \
#       DOCKER_IMAGE_CREATE_DONE


#----------------------------------------------------------
# Handle ini-file
#----------------------------------------------------------
def parse_odoo_config(path):
    """scan odoo config file into dictionary
    
    Arguments:
        path {string} -- path to the config file
    """

    result = {}
    config = configparser.ConfigParser()
    config.read(path)
    if 'options' in config:
        for key, value in config['options'].items():
            result[key] = value
    return result

#----------------------------------------------------------
# Postgres subprocesses
#----------------------------------------------------------

def find_pg_tool(name):
    return shutil.which(name)

#def exec_pg_environ():
    #"""
    #Force the database PostgreSQL environment variables to the database
    #configuration of Odoo.

    #Note: On systems where pg_restore/pg_dump require an explicit password
    #(i.e.  on Windows where TCP sockets are used), it is necessary to pass the
    #postgres user password in the PGPASSWORD environment variable or in a
    #special .pgpass file.

    #See also http://www.postgresql.org/docs/8.4/static/libpq-envars.html
    #"""
    #env = os.environ.copy()
    #if odoo.tools.config['db_host']:
        #env['PGHOST'] = odoo.tools.config['db_host']
    #if odoo.tools.config['db_port']:
        #env['PGPORT'] = str(odoo.tools.config['db_port'])
    #if odoo.tools.config['db_user']:
        #env['PGUSER'] = odoo.tools.config['db_user']
    #if odoo.tools.config['db_password']:
        #env['PGPASSWORD'] = odoo.tools.config['db_password']
    #return env

def exec_pg_command(name, *args, **pg_env):
    prog = find_pg_tool(name)
    with open(os.devnull) as dn:
        args2 = (prog,) + args
        rc = subprocess.call(args2, env=pg_env, stdout=dn, stderr=subprocess.STDOUT)
        if rc:
            raise Exception('Postgres subprocess %s error %s' % (args2, rc))

@contextmanager
def tempdir():
    tmpdir = tempfile.mkdtemp()
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)

def zip_dir(path, stream, include_dir=True, fnct_sort=None):      # TODO add ignore list
    """
    : param fnct_sort : Function to be passed to "key" parameter of built-in
                        python sorted() to provide flexibility of sorting files
                        inside ZIP archive according to specific requirements.
    """
    path = os.path.normpath(path)
    len_prefix = len(os.path.dirname(path)) if include_dir else len(path)
    if len_prefix:
        len_prefix += 1

    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
        for dirpath, dirnames, filenames in os.walk(path):
            filenames = sorted(filenames, key=fnct_sort)
            for fname in filenames:
                bname, ext = os.path.splitext(fname)
                ext = ext or bname
                if ext not in ['.pyc', '.pyo', '.swp', '.DS_Store']:
                    path = os.path.normpath(os.path.join(dirpath, fname))
                    if os.path.isfile(path):
                        zipf.write(path, path[len_prefix:])



def dump_db_manifest(cr, manifest={}):
    # get te version
    cr.execute('select version();')
    row = cr.fetchone()
    pg_version = row.get('version').split(' ')[1]
    # pg_version = "%d.%d" % divmod(cr._obj.connection.server_version / 100, 100)
    cr.execute("SELECT name, latest_version FROM ir_module_module WHERE state = 'installed'")
    modules = dict(cr.fetchall())
    manifest['modules'] = modules
    manifest['pg_version'] = pg_version
    return manifest

class MigrationHandler(InitHandler, DBUpdater):
    master = '' # possible master site from which to copy
    def __init__(self, opts, sites = {}):
        """
        """
        super().__init__(opts, sites)

        
    _subparser_name = 'migrate'
    @property
    def subparser_name(self):
        return self._subparser_name 

    _migration_tokens = ''
    @property
    def migration_tokens(self):
        """migration token is a list of names we want to collect values for
        
        Returns:
            list -- list of strings
        """

        return self._migration_tokens
    
    def collect_installed(self, cursor):
        """collect installed apps and modules
        
        Arguments:
            cursor {sql cursor} -- cursor returned by get_cursor
        """
        sql = 'select * from ir_module_module'
        cursor.execute(sql)
        rows = cursor.fetchall()
        result = {}
        for row in rows:
            name = row.get('name')
            state = row.get('state')
            app_id = row.get('id')
            if state == 'installed':
                result[name] = app_id
        return result

    def collect_migration_info(self):
        """read the migration values for the running site
        to do so, we collect the values for the tokens we read from
        config/migration.yaml
        """
        pass

    def migrate_remove_apps(self):
        """read a list of apps and modules to delete
        and remove them
        """
        file_with_apps = self.opts.migrate_remove_apps
        cursor = self.get_cursor()
        module_obj = self.get_module_obj()
        
        if not os.path.exists(file_with_apps):
            print(bcolors.FAIL)
            print('*' * 80)
            print('%s does not exist' % file_with_apps)
            print(bcolors.ENDC)
            return
        with open(file_with_apps, 'r') as f:
            lines = f.readlines()
        lines = [l.strip() for l in lines]
        for line in lines:
            if line:
                installed = self.collect_installed(cursor)
                app_id = installed.get(line)
                if app_id:
                    print(bcolors.FAIL)
                    print('*' * 80)
                    print('about to uninstall %s' % line)
                    print(bcolors.ENDC)
                    module_obj.browse(app_id).button_immediate_uninstall()


    def migrate_dump_site(self):
        backup_format = 'zip'
        opts = self.opts
        
        dump_stream = self.dump_db(self.site_name, backup_format)

    def dump_db(self, db_name, backup_format='zip'):
        """Dump database `db` into file-like object `stream` if stream is None
        return a file object with the dump """
        # ['pg_dump', '--no-owner', '--file=/tmp/tmp87h3qpev/dump.sql', 'redo2oo11']
        cmd = ['pg_dump', '--no-owner']
        cmd.append(db_name)
        odoo_options = {}
        opts = self.opts
        if opts.migrate_config_path:
            odoo_options = parse_odoo_config(opts.migrate_config_path)
            if not odoo_options:
                print(bcolors.FAIL)
                print('*' * 80)
                print('%s is not readable' % opts.migrate_config_path)
                print(bcolors.ENDC)
                sys.exit()
        if self.site_name in self.site_names:
            # this is a site handled by erpworkbench
            filestore = self.site_data_dir
            # filestore = '%s/filestore/%s' % (self.site_data_dir, db_name)
        elif self.opts.migrate_data_path:
            filestore = self.opts.migrate_data_path
        if not filestore:
            filestore = odoo_options.get('data_dir')
        if not filestore:
            print(bcolors.FAIL)
            print('*' * 80)
            print('no datafile detected')
            print(bcolors.ENDC)
            sys.exit()
        filestore = '%s/filestore/%s' % (filestore, db_name)
        
        # get odoo version info
        if self.site_name in self.site_names:
            version = '%s%s' % (self.erp_version, self.erp_minor)
            v_int = int(self.erp_version)
        else:
            version = opts.migrate_version
            if version:
                newstr = ''.join((ch if ch in '0123456789.' else ' ') for ch in '11.0-final')
                try:
                    version = str(float(newstr))
                    v_int = int(version)
                except:
                    raise ValueError('can not detect version from %s' % opts.migrate_version)
            else:
                print(bcolors.FAIL)
                print('*' * 80)
                print('please provide a version like -mver 11.0-final')
                print(bcolors.ENDC)
                sys.exit()
                
        backup_format = 'zip'
        cr = self.get_cursor()
        # version_info format: (MAJOR, MINOR, MICRO, RELEASE_LEVEL, SERIAL)
        # inspired by Python's own sys.version_info, in order to be
        # properly comparable using normal operarors, for example:
        #  (6,1,0,'beta',0) < (6,1,0,'candidate',1) < (6,1,0,'candidate',2)
        #  (6,1,0,'candidate',2) < (6,1,0,'final',0) < (6,1,2,'final',0)
        version_info = (v_int, 0, 0, 'final', 0, '')        
        manifest = {
            'odoo_dump': '1',
            'db_name': db_name,
            'version': version,
            'version_info': version_info,
            'major_version': version,
            'pg_version': '',
            'modules': [],
        }
        
        pg_env = os.environ.copy()
        pg_env['PGHOST'] = self.db_host
        pg_env['PGPORT'] = str(self.postgres_port)
        pg_env['PGUSER'] = self.db_user
        pg_env['PGPASSWORD'] = self.db_user_pw
        
        with tempdir() as dump_dir:
            if os.path.exists(filestore):
                shutil.copytree(filestore, os.path.join(dump_dir, 'filestore'))
            #manifest = dump_db_manifest(cr, manifest)
            with open(os.path.join(dump_dir, 'manifest.json'), 'w') as fh:
                json.dump(dump_db_manifest(cr, manifest), fh, indent=4)
            cmd.insert(-1, '--file=' + os.path.join(dump_dir, 'dump.sql'))
            exec_pg_command(*cmd, **pg_env)
            t=tempfile.TemporaryFile()
            zip_dir(dump_dir, t, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
            t.seek(0)
            # now write everything to a file
            with open('%s.zip' % self.site_name, 'wb') as zip_file:
                zip_file.write(t.read())
        a = 1




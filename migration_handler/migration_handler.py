#!bin/python
# -*- encoding: utf-8 -*-

#https://www.digitalocean.com/community/tutorials/how-to-set-up-a-private-docker-registry-on-ubuntu-14-04
from config import ODOO_VERSIONS
#from config.handlers import InitHandler, DBUpdater
from scripts.create_handler import InitHandler
from scripts.update_local_db import DBUpdater
import os
import re
import sys
import shutil
from site_desc_handler.handle_remote_data import get_remote_server_info
from scripts.bcolors import bcolors
from contextlib import contextmanager
import shutil
import tempfile
import zipfile

from scripts.messages import DOCKER_DB_MISSING #, DOCKER_DB_MISSING, DOCKER_INVALID_PORT, \
#       DOCKER_INVALID_PORT, DOCKER_IMAGE_PULLED, DOCKER_IMAGE_PULL_FAILED, DOCKER_IMAGE_NOT_FOUND, \
#       DOCKER_IMAGE_PUSH_MISING_HUB_INFO, SITE_NOT_EXISTING, DOCKER_IMAGE_CREATE_ERROR, \
#       DOCKER_IMAGE_CREATE_MISING_HUB_INFO, DOCKER_IMAGE_CREATE_MISING_HUB_USER, ERP_VERSION_BAD, \
#       DOCKER_IMAGE_CREATE_MISING_HUB_USER, DOCKER_IMAGE_CREATE_PLEASE_WAIT, DOCKER_IMAGE_CREATE_FAILED, \
#       DOCKER_IMAGE_CREATE_DONE

#----------------------------------------------------------
# Postgres subprocesses
#----------------------------------------------------------

def find_pg_tool(name):
    path = None
    if config['pg_path'] and config['pg_path'] != 'None':
        path = config['pg_path']
    try:
        return which(name, path=path)
    except IOError:
        raise Exception('Command `%s` not found.' % name)

def exec_pg_environ():
    """
    Force the database PostgreSQL environment variables to the database
    configuration of Odoo.

    Note: On systems where pg_restore/pg_dump require an explicit password
    (i.e.  on Windows where TCP sockets are used), it is necessary to pass the
    postgres user password in the PGPASSWORD environment variable or in a
    special .pgpass file.

    See also http://www.postgresql.org/docs/8.4/static/libpq-envars.html
    """
    env = os.environ.copy()
    if odoo.tools.config['db_host']:
        env['PGHOST'] = odoo.tools.config['db_host']
    if odoo.tools.config['db_port']:
        env['PGPORT'] = str(odoo.tools.config['db_port'])
    if odoo.tools.config['db_user']:
        env['PGUSER'] = odoo.tools.config['db_user']
    if odoo.tools.config['db_password']:
        env['PGPASSWORD'] = odoo.tools.config['db_password']
    return env

def exec_pg_command(name, *args):
    prog = find_pg_tool(name)
    env = exec_pg_environ()
    with open(os.devnull) as dn:
        args2 = (prog,) + args
        rc = subprocess.call(args2, env=env, stdout=dn, stderr=subprocess.STDOUT)
        if rc:
            raise Exception('Postgres subprocess %s error %s' % (args2, rc))

@contextmanager
def tempdir():
    tmpdir = tempfile.mkdtemp()
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)

def dump_db_manifest(cr):
    pg_version = "%d.%d" % divmod(cr._obj.connection.server_version / 100, 100)
    cr.execute("SELECT name, latest_version FROM ir_module_module WHERE state = 'installed'")
    modules = dict(cr.fetchall())
    manifest = {
        'odoo_dump': '1',
        'db_name': cr.dbname,
        'version': odoo.release.version,
        'version_info': odoo.release.version_info,
        'major_version': odoo.release.major_version,
        'pg_version': pg_version,
        'modules': modules,
    }
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

        dump_stream = openerp.service.db.dump_db(name, None, backup_format)

    def dump_db(db_name, stream, backup_format='zip'):
        """Dump database `db` into file-like object `stream` if stream is None
        return a file object with the dump """

        cmd = ['pg_dump', '--no-owner']
        cmd.append(db_name)
        filestore = self.opts.migrate_data_path
        backup_format = 'zip'
        cr = self.get_cursor()
        with tempdir() as dump_dir:
            if os.path.exists(filestore):
                shutil.copytree(filestore, os.path.join(dump_dir, 'filestore'))
            with open(os.path.join(dump_dir, 'manifest.json'), 'w') as fh:
                db = odoo.sql_db.db_connect(db_name)
                with db.cursor() as cr:
                    json.dump(dump_db_manifest(cr), fh, indent=4)
            cmd.insert(-1, '--file=' + os.path.join(dump_dir, 'dump.sql'))
            exec_pg_command(*cmd)
            if stream:
                odoo.tools.osutil.zip_dir(dump_dir, stream, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
            else:
                t=tempfile.TemporaryFile()
                odoo.tools.osutil.zip_dir(dump_dir, t, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
                t.seek(0)
                return t




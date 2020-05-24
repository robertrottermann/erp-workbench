from __future__ import print_function
import os, sys
import subprocess
from argparse import ArgumentParser
import subprocess
from subprocess import PIPE
# #process = subprocess.Popen(['/bin/bash'], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
# subprocess.call('bash', shell=True, executable='/bin/bash')
# print "hello dumper"
# print '--------->', os.environ.get('POSTGRES_PASSWORD')
# print 'Number of arguments:', len(sys.argv), 'arguments.'
# print 'Argument List:', str(sys.argv)

POSTGRES_PASSWORD = 'odoo'
POSTGRES_USER = 'odoo'
POSTGRES_HOST = 'db'

HOME = '/mnt/sites/'
SITES_HOME = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
# ------------------------------------
# get_value_from_config
# gets a value from etc/open_erp.conf
# ------------------------------------
def get_value_from_config(path, key=''):
    res = {}
    for l in open(path):
        if l and l.find('=') > -1:
            parts = l.split('=', 1)
            res[parts[0].strip()] = parts[1].strip()
    if key:
        return res.get(key)
    else:
        return res

# ------------------------------------
# get_instance_list
# checks all subdirectories whether
# they provide an etc/open_erp.conf
# if yes, it is considered to be an
# openerp site
# a dict of {'sitename' : dbname, ..}
#   is returned
# ------------------------------------
def get_instance_list(opts, quiet = False):
    if opts.test:
        HOME = SITES_HOME
    dirs = [d for d in os.listdir(HOME) if os.path.isdir('%s/%s' % (HOME, d))]
    result = {}
    for d in dirs:
        plist  = ('%s/%s/etc/openerp-server.conf' % (HOME, d), '%s/%s/etc/flectra.conf' % (HOME, d))
        # if opts.veryverbose:
        #     print p
        for p in plist:
            if os.path.exists(p):
                db = get_value_from_config(p, 'db_name')
                result[d] = db
                if not quiet:
                    print(d, 'db:', get_value_from_config(p, 'db_name'))
    return result

DB_LIST_SELECT = 'SELECT datname FROM pg_database;'


def list_databases(opts):
    from socket import gethostbyname
    try:
        import psycopg2
    except:
        print('could not import psycopg2')

    c_string = "user='%s' host='%s' password='%s'" % ('odoo', gethostbyname('db'), 'odoo')
    #
    try:
        conn = psycopg2.connect(c_string)
    except:
        print("I am unable to connect to the database using")
        print(c_string)
    cur = conn.cursor()
    cur.execute(DB_LIST_SELECT)
    print("These databases exist:")
    for row in cur.fetchall():
        if row[0] not in ['odoo', 'postgres', 'template0', 'template1']:
            print( "   ", row[0])
    return

def reload_instance(opts):
    dbname = opts.reload
    verbose = opts.verbose
    if verbose:
        print('*' * 80)
        print('make sure container is stopped !!!')
    # collect list of dictionaries with all sites
    # known in this environment
    data = get_instance_list(opts, quiet = True)
    instances = []
    names = list(data.keys())
    # all allows us do restore all backups
    if dbname == 'all':
        instances = names
    else:
        instances = [n for n in dbname.split(',') if n in names]

    for instance in instances:
        # drop database
        dbname = data[instance]
        cmds = ["PGPASSWORD=%s " % POSTGRES_PASSWORD, '/usr/bin/psql',
            "-h", POSTGRES_HOST, '-U', POSTGRES_USER, '-d', 'postgres',
            '-c', '"drop database IF EXISTS %s;"' % dbname ]
        cmdline = ' '.join(cmds)
        if verbose:
            print('*' * 80)
            print(cmdline)
        # recreate database
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, shell=True)
        if verbose:
            print(p.communicate())
        else:
            p.communicate()
        cmds = ["PGPASSWORD=%s " % POSTGRES_PASSWORD, '/usr/bin/psql',
            "-h", POSTGRES_HOST, '-U', POSTGRES_USER, '-d', 'postgres',
            '-c', '"create database %s;"' % dbname ]
        cmdline = ' '.join(cmds)
        if verbose:
            print(cmdline)
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, shell=True)
        if verbose:
            print(p.communicate())
        else:
            p.communicate()
        # do the actual reading of the database
        # the database will have the same name as on the remote server
        dpath = '%s/%s/dump' % (HOME, instance)
        cmds = ["PGPASSWORD=%s " % POSTGRES_PASSWORD,
            '/usr/bin/psql', "-h", POSTGRES_HOST,
            '-U', POSTGRES_USER, '-d', dbname,
            '-f'
            "%s/%s.dmp" % (dpath, dbname)]
        cmdline = ' '.join(cmds)
        if verbose:
            print(cmdline)
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, shell=True)
        if verbose:
            print(p.communicate())
        else:
            p.communicate()


def drop_instance(opts):
    dbname = opts.drop
    data = get_instance_list(opts, quiet = True)
    instances = []
    names = list(data.keys())
    instances = [n for n in dbname.split(',') if n in names]
    verbose = opts.verbose
    for instance in instances:
        dbname = data[instance]
        # drop database
        dbname = data[instance]
        cmds = ["PGPASSWORD=%s " % POSTGRES_PASSWORD, '/usr/bin/psql',
            "-h", POSTGRES_HOST, '-U', POSTGRES_USER, '-d', 'postgres',
            '-c', '"drop database IF EXISTS %s;"' % dbname ]
        cmdline = ' '.join(cmds)
        if verbose:
            print('*' * 80)
            print(cmdline)
        # recreate database
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, shell=True)
        if verbose:
            print(p.communicate())
        else:
            p.communicate()

def dump_instance(opts):
    dbname = opts.dump
    verbose = opts.verbose
    data = get_instance_list(opts, quiet = True)
    instances = []
    names = list(data.keys())
    use_ascii = opts.useascii
    if dbname == 'all':
        instances = names
    else:
        instances = [n for n in dbname.split(',') if n in names]
    for instance in instances:
        dbname = data[instance]
        dpath = ''
        # there are multiple scenario where we should dump to
        # 1. scenario: how it should be:
        #   /mnt/sites/SITE_NAME/dump exists
        dpath = '%s/%s/dump' % (HOME, instance)
        if os.path.exists(dpath):
            if use_ascii:
                #['pg_dump', '--no-owner', '--file=/tmp/tmpmuhvw4h3/dump.sql', 'afbs13_2']
                cmds = [
                    "PGPASSWORD=%s " % POSTGRES_PASSWORD,
                    "/usr/bin/pg_dump",
                    "-h", POSTGRES_HOST,
                    "-U", POSTGRES_USER,
                    "--no-owner",
                    "--file=%s/%s.dmp" % (dpath, dbname),
                    dbname]
                    #'-Fp', dbname, "> %s/%s.dmp" % (dpath, dbname)]
            else:
                cmds = [
                    "PGPASSWORD=%s " % POSTGRES_PASSWORD,
                    "/usr/bin/pg_dump",
                    "-h", POSTGRES_HOST,
                    "-U", POSTGRES_USER,
                    '-Fc', dbname, "> %s/%s.dmp" % (dpath, dbname)]
            cmdline = ' '.join(cmds)
            if verbose:
                print('*' * 80)
                print(cmdline)
            p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, shell=True)
            p.communicate()
            if verbose:
                print('dumped:', dpath)
        else:
            print('not existing:', dpath)

def main():
    usage = "dumper.py -h for help on usage"
    parser = ArgumentParser(usage=usage)

    parser.add_argument("-d", "--dump",
                    action="store", dest="dump", default='',
                    help="dump database, use all to dump all or comma separated list of sites")

    parser.add_argument("-dd", "--drop",
                    action="store", dest="drop", default='',
                    help="drop database, name nust be provided")

    parser.add_argument("-l", "--list",
                    action="store_true", dest="list_sites", default=False,
                    help="list existing sites")

    parser.add_argument("-ldb", "--listdb",
                    action="store_true", dest="list_databases", default=False,
                    help="list existing databases within the db container")

    parser.add_argument("-r", "--reload",
                    action="store", dest="reload", default=False,
                    help="reload data into database, use all to reload all or comma separated list of sites\nthis is done by droping the database and recostructing it")

    parser.add_argument("-s", "--shell",
                    action="store_true", dest="shell", default=False,
                    help="drop into an interactive shell")

    parser.add_argument("-t", "--test",
                    action="store_true", dest="test", default=True,
                    help="test (probably using wing)")

    parser.add_argument("-v", "--verbose",
                    action="store_true", dest="verbose", default=True,
                    help="be verbose")

    parser.add_argument("-a", "--use-ascii",
                    action="store_true", dest="useascii", default=True,
                    help="dump to uncompressed ascii sql file")

    opts = parser.parse_args()

    if opts.shell:
        subprocess.call('bash', shell=True, executable='/bin/bash')
    elif opts.list_sites:
        get_instance_list(opts)
    elif opts.list_databases:
        list_databases(opts)
    elif opts.drop:
        drop_instance(opts)
    elif opts.dump:
        dump_instance(opts)
    elif opts.reload:
        reload_instance(opts)

if __name__ == '__main__':
    main()
#

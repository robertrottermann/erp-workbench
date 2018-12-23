#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import sys
import subprocess
from subprocess import PIPE
import re
from pprint import pprint, pformat
from io import StringIO
from copy import deepcopy
import psutil
from scripts.messages import *
from scripts.bcolors import bcolors
from scripts.vcs.git import GitRepo, BUILDOUT_ORIGIN, logging
from scripts.vcs.base import UpdateError
try:
    from git import Repo
except ImportError as e:
    print(MODULE_MISSING % 'git')
    sys.exit()
from config import SITES, SITES_LOCAL
import git
import socket
from socket import gaierror

"""
create_new_project.py
---------------------
create a new odoo project so we can easily maintain a local and a remote
set of configuration files and keep them in sync.

It knows enough about odoo to be able to treat some special values correctly

"""

# after strt tag we start to lok for values
START_TAG = '[login_info]'
# delimiter defines start of new value
DELIMITER = '##----'
# base path is the path from where this script is loaded
# it is wehere all config info is stored
SITE_TEMPLATE = """
    "%(site_name)s" : {
%(data)s
    },
"""

from config.config_data.servers_info import REMOTE_SERVERS


def get_process_id(name, path):
    """Return process ids found by (partial) name or regex.

    >>> get_process_id('kthreadd')
    [2]
    >>> get_process_id('watchdog')
    [10, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56, 61]  # ymmv
    >>> get_process_id('non-existent process')
    []
    """
    # child = subprocess.Popen(['pgrep', '-f', name], stdout=subprocess.PIPE, shell=False)
    # response = child.communicate()[0]
    # pids = [int(pid) for pid in response.split()]
    result = []
    for p in psutil.process_iter():
        cmdline = p.cmdline()
        if cmdline and path in cmdline[0] and cmdline[-1].endswith(name):
            # ['/home/robert/projects/eplusp11/eplusp11/bin/python', 'bin/start_openerp']
            result.append([p.pid, cmdline])
    return result

def collect_options(opts):
    """
    """
    # return list of posible suboptions
    # and if a valid otion is selected
    actual = opts.subparser_name
    _o = opts._get_kwargs()
    skip = [
        'name',
        'subparser_name',
        'dockerdbpw',
        'dockerdbuser',
        'dbhost',
        'dbpw',
        'dbuser',
        'rpchost',
        'rpcport',
        'rpcuser',
        'rpcpw']
    keys = [k[0] for k in _o if k[0] not in skip]
    is_set = [k for k in _o if not (k[1] is False) and (k[0] not in skip)]
    return actual, is_set, keys


# ----------------------------------
# collect_addon_paths
# go trough the addons in syte.py and collect
# addon_path info for the actual site. This info
# is stored in default_values
def collect_addon_paths(handler):
    """
    go trough the addons in syte.py and collect
    addon_path info for the actual site. This info
    is stored in default_values
    """
    addons = handler.site.get('addons', [])
    base_path = handler.site.get('docker', {}).get(
        'base_path', '/mnt/extra-addons')
    apps = []
    for addon in addons:
        if addon.get('add_path'):
            apps.append('%s/%s' % (base_path, addon['add_path']))

    handler.default_values['add_path'] = ''
    if apps:
        handler.default_values['add_path'] = ',' + ','.join(apps)


# ----------------------------------
# create_server_config
# create server config file in erp_workbench/SITENAME/openerp.conf
# @default_values   : default value
# @foldernames      : list of folders to create within the site foler
# ----------------------------------
CONFIG_NAME = {
    'odoo': {
        'config': 'openerp-server.conf',
        'val_dic': {
            'server_wide_modules': 'web,web_kanban',
            'xmlrpc_port': 8069,
            'longpolling_port': 8072,
            'logfile': '/var/log/odoo/odoo_log',
            'data_dir': '/var/lib/odoo',
        }
    },
    'flectra': {
        'config': 'flectra.conf',
        'val_dic': {
            'server_wide_modules': '',
            'xmlrpc_port': 7073,
            'longpolling_port': 7072,
            'logfile': '/var/log/flectra/flectra_log',
            'data_dir': '/var/lib/flectra',
        }
    }
}


def create_server_config(handler):
    """
    create server config file in $erp_server_data_path$/SITENAME/openerp.conf
    @default_values   : default value
    @foldernames      : list of folders to create within the site foler
    """
    from templates.openerp_cfg_defaults import CONFIG_DEFAULTS
    name = handler.site_name
    if not name:
        # we need a site name to create a server config
        return
    erp_type = handler.site.get('erp_type', 'odoo')
    config_name = CONFIG_NAME[erp_type]['config']
    erp_admin_pw = handler.site.get('erp_admin_pw', '')
    base_info = handler.base_info 
    p = os.path.normpath('%s/%s' % (base_info['erp_server_data_path'], name))
    collect_addon_paths(handler)
    # now copy a template openerp-server.conf
    handler.default_values['erp_admin_pw'] = erp_admin_pw
    template = open(
        '%s/templates/%s' % (handler.default_values['sites_home'], config_name), 'r').read()
    if os.path.exists('%s/etc/' % p):
        f = open('%s/etc/%s' % (p, config_name), 'w')
        f.write(template % handler.default_values)
        # write rest of the values to the config file
        # get them either from site description site_settings.server_config stanza
        # or CONFIG_DEFAULTS
        server_config = handler.site.get(
            'site_settings', {}).get('server_config', {})
        def_dic = {}
        def_dic.update(handler.default_values)
        def_dic.update(CONFIG_NAME[erp_type]['val_dic'])
        for k, v in list(CONFIG_DEFAULTS.items()):
            vv = server_config.get(k, v)
            if isinstance(vv, str):
                vv = vv % def_dic
            line = '%s = %s\n' % (k,  vv)
            f.write(line)
        f.close()
    else:
        # should never happen
        print(bcolors.FAIL + 'ERROR: folder %s does not exist' % p + bcolors.ENDC)


# ----------------------------------
# get_single_value
# ask value from user
# @name         : name of the value
# @explanation  : explanation of the value
# @default      : default value
# @prompt       : prompt to display
# ----------------------------------
def get_single_value(
        name,
        explanation,
        default,
        prompt='%s [%s]:'):
    """
    ask value from user
    @name         : name of the value
    @explanation  : explanation of the value
    @default      : default value
    @prompt       : prompt to display
    """
    # get input from user for a single value. present expanation and default value
    print('*' * 50)
    print(explanation)
    result = input(prompt % (name, default))
    if not result:
        result = default
    return result


def set_base_info(info_dic, filename):
    "write base info back to the config folder"
    info = 'base_info = %s' % pformat(info_dic)
    open(filename, 'w').write(info)


def get_base_info(base_info, base_defaults):
    from config import BASE_INFO # avoid circular import
    "collect base info from user, update base_info"
    for k, v in list(base_defaults.items()):
        name, explanation, default = v
        # use value as stored, default otherwise
        default = BASE_INFO.get(k, default)
        base_info[k] = get_single_value(name, explanation, default)

# # ----------------------------------
# # update_base_info
# # collects localdata that will be stored in config/base_info.py
# # @base_info_path   : path to config/base_info.pyconfig/base_info.py
# # @default_values   : dictionary with default values
# # ----------------------------------


# def update_base_info(base_info_path, defaults):
#     """
#     collects localdata that will be stored in config/base_info.py
#     @base_info_path   : path to config/base_info.pyconfig/base_info.py
#     @default_values   : dictionary with default values
#     """
#     base_info = {}
#     get_base_info(base_info, defaults)
#     set_base_info(base_info, base_info_path)
#     print('%s created' % base_info_path)

# ----------------------------------
# list_sites
# list sitenames listed in the sites_dic
# @sites_dic    : dictionary with info about sites
#                 this is the combination of sites.py and local_sites.py
# ----------------------------------


def list_sites(sites_dic, quiet=False):
    """
    list sitenames listed in the sites_dic
    @sites_dic    : dictionary with info about sites
                    this is the combination of sites.py and local_sites.py
    quiet is set when testing
    """
    keys = list(sites_dic.keys())
    keys.sort()
    for key in keys:
        origin = sites_dic[key].get('site_list_name', '')
        if origin:
            origin = ':%s' % origin
        if sites_dic[key].get('is_local'):
            if not quiet:
                print('%s%s (local)' % (key, origin))
        else:
            if not quiet:
                print('%s%s' % (key, origin))

# ----------------------------------
# module_add
# add module to sites.py for a site, create it if opts.module_create
# if user is allowed to write to the apache directory, add it to
#   sites_available and sites_enabled
# if not, just print it out
# @opts             : option instance
# @default_values   : dictionary with default values
# @site_values      : values for this site as found in systes.py
# @module_name      : name of the new module
# ----------------------------------


def module_add(opts, default_values, site_values, module_name):
    """
    add module to sitey.py for a site, create it if opts.module_create
    if user is allowed to wite to the apache directory, add it to
      sites_available and sites_enabled
    if not, just print it out
    @opts             : option instance
    @default_values   : dictionary with default values
    @site_values      : values for this site as found in systes.py
    @module_name      : name of the new module
    """
    from config import BASE_INFO # avoid circular import
    # we start opening the sites.py as text file
    if default_values['is_local']:
        sites_path = '%s/sites_local' % BASE_INFO['sitesinfo_path']
    else:
        sites_path = '%s/sites_global' % BASE_INFO['sitesinfo_path']
    sites_str = open(sites_path, 'r').read()
    # startmach is a line with nothin but:
    #    "breitschtraeff9" : {
    start_match = re.compile(r'\s+"%(site_name)s"\s*:\s\{' % default_values)
    # startmach is a line with nothin but:
    #    },
    end_match = re.compile(r'^\s*},\s*$')
    # separate sites.py into lines before and after actual site
    lines = sites_str.split('\n')
    pref_lines = []
    sub_lines = []
    started = False
    before = True  # we add lines to before
    for line in lines:
        if start_match.match(line):
            started = True
        if started:
            # we only check if fiished, if started = true
            if end_match.match(line):
                started = False
                before = False
            continue
        # we are not within the started block
        if before:
            pref_lines.append(line)
        else:
            sub_lines.append(line)
    # add new module to the list of modules
    mlist = site_values.get('addons', [])
    if not module_name in mlist:
        mlist.append(module_name)
        site_values['addons'] = mlist
        # create dict as text to be patched between pref_ & sub_lines
        buff = StringIO()
        pprint(site_values, indent=8, stream=buff)
        site_string = buff.getvalue()
        # remove opening/closing brackets
        site_string = ' ' + site_string[1:-2] + ','
        new_site = SITE_TEMPLATE % {
            'data': site_string, 'site_name': default_values['site_name']}
        # construct new filecontent of systes.py by conatenating its three elements
        data = '\n'.join(pref_lines) + new_site + '\n'.join(sub_lines)
        # write that thing
        open(sites_path, 'w').write(data)
    # if opts.module_create we create the modul using odos scaffolding facility
    if opts.module_create:
        # check wheter the addon directory exists
        # this directory is create by dosetup.py
        addons_path = '%(inner)s/%(site_name)s_addons' % default_values
        module_path = '%s/%s' % (addons_path, module_name)
        if not os.path.exists(addons_path):
            print('%s does not exist')
            return
        if os.path.exists(module_path):
            print('module %s allready exists')
            return
        # fine, we can go ahead
        # hopefully odoo is at its standard place
        #odoo_path = '%(inner)s/parts/odoo/odoo.py' % default_values
        runner_path = '%(inner)s/bin/odoorunner.py' % default_values
        # usage: odoorunner.py scaffold [-h] [-t TEMPLATE] name [dest]
        cmdline = '%s scaffold %s %s' % (runner_path, module_name, addons_path)
        print(cmdline)
        cur_dir = os.getcwd()
        os.chdir(default_values['inner'])
        p = subprocess.Popen(cmdline, stdout=PIPE, shell=True)
        p.communicate()
        os.chdir(cur_dir)
        print('added skeleton to %s' % module_path)


# ----------------------------------
# find_addon_names
# find the names of an addon
# @addon        : addon to find out names
# an addon can have more than one name when more than one addon has to be
# installed from a folder of addons
# return: list of names
# ----------------------------------
def find_addon_names(addon):
    name = ''
    names = []
    a = addon
    try:
        if 'names' in a:
            names = a['names']
        elif 'name' in a:
            name = a['name']
        elif 'group' in a:
            name = a['group']
        elif 'add_path' in a:
            name = a['add_path']
        names = names + [name]
    except AttributeError:
        print(bcolors.FAIL, a, bcolors.ENDC)
        input('hit enter to continue')

    return [n.strip() for n in names if n]

# ----------------------------------
# checkout_sa
# get addons from repository
# @opts   : options as entered by the user
# ----------------------------------
"""
#!/bin/sh
#http://stackoverflow.com/questions/3258243/check-if-pull-needed-in-git

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull"
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi

# an other solution
[ $(git rev-parse HEAD) = $(git ls-remote $(git rev-parse --abbrev-ref @{u} | \
sed 's/\// /g') | cut -f1) ] && echo up to date || echo not up to date
"""


def set_git_remote(repo, reset_git_to=''):
    # make sure we have tracking info
    # this fails, if allready defined
    target = repo.target_dir
    is_new = not os.path.exists(target)
    os.chdir(target)
    url = repo.url
    if is_new:
        repo.log_call(['git', 'init', target])
    if reset_git_to:
        try:
            repo.log_call(['git', 'remote', 'rm', BUILDOUT_ORIGIN])
        except Exception as e:
            # was probaly removed ..
            pass
        url = reset_git_to
    repo.log_call(['git', 'remote', 'add' if (is_new or reset_git_to) else 'set-url',
                   BUILDOUT_ORIGIN, url],
                  log_level=logging.DEBUG)


def need_git_pull(name, target, branch, changes=[], changes_only=False, reset_git=False):
    # first we check, if the folder with the git repository is available
    if not os.path.exists(target):
        # we must update it
        return True
    # the folder exists, we assume, that it is a git repository
    # it can be in several states
    # - in sync
    # - locally changed
    # - remotely changed
    # - diverged (both sides updated, merge needed)
    # UPSTREAM = "${1:-'@{u}'}"
    cur_dir = os.getcwd()
    res_dic = {}
    repo = Repo(target)
    if reset_git:
        set_git_remote(repo, target)
    try:
        repo.git.execute('git branch --set-upstream-to=origin/%s %s' %
                         (branch, branch), shell=True)
    except Exception as e:
        str(e)
    for k, cmdline in [
        ('LOCAL', 'git rev-parse @'),
        ('REMOTE', 'git rev-parse @{u}'),
            ('BASE', 'git merge-base @ @{u}')]:
        os.chdir(target)  # probably not neccessary
        p = subprocess.Popen(cmdline, stdout=PIPE, shell=True)
        res = p.communicate()
        res_dic[k] = res[0]

    os.chdir(cur_dir)

    if res_dic['BASE'] == res_dic['REMOTE']:
        # local has changed
        try:
            changes = repo.git.diff('HEAD~1..HEAD', name_only=True)
        except:
            pass
        if changes_only:
            return changes
    if res_dic['LOCAL'] == res_dic['REMOTE']:
        # is in sync
        return False
    elif res_dic['LOCAL'] == res_dic['BASE']:
        # remote has changed
        return True
    elif res_dic['BASE'] != res_dic['REMOTE']:
        # has diverged
        print(GIT_REPO_DIVERGED % repo.remotes[0].url)
        return False

    return True


def repo_get_tag_sha(repo_path, tag, verbose=False):
    if not os.path.exists(repo_path):
        print(bcolors.WARNING)
        print('*******************************')
        print(repo_path, 'not yet initialized')
        print('can not check what branch exists')
        print('please rerun after the repro is initialized')
        return
    else:
        repo = git.Repo(repo_path)
        try:
            tag_info = repo.tag('refs/tags/%s' % tag)
        except ValueError as e:
            # tag does not exist
            return None
    return str(tag_info.commit) # '669bc1f5949bc028f2a75c3e6e20fab9f20f2cfd'
    

def repo_has_branch(repo_path, branch, verbose=False):
    if not os.path.exists(repo_path):
        print(bcolors.WARNING)
        print('*******************************')
        print(repo_path, 'not yet initialized')
        print('can not check what branch exists')
        print('please rerun after the repro is initialized')
        return
    else:
        repo = git.Repo(repo_path)
    remote_branches = []
    if verbose:
        print('------------------------------------------')
        print(repo_path)
    for ref in repo.git.branch('-r').split('\n'):
        br = ref.split('/')[-1]
        if verbose:
            print(br)
        remote_branches.append(br)
    if verbose:
        print('>>>>>>>>>>', branch in remote_branches)
    return branch in remote_branches


def checkout_sa(opts):
    """
    get addons from repository
    @opts   : options as entered by the user
    """
    from config import BASE_INFO # avoid circular import    
    if not opts.name:
        # need a  site_name to do anythin sensible
        return
    from .git_check import gitcheck, argopts
    result = {'failed': [], 'need_reload': []}
    site_addons = []
    is_local = SITES_LOCAL.get(opts.name) is not None
    _s = SITES.get(opts.name)
    if not _s:
        return
    if is_local:
        _s = SITES_LOCAL.get(opts.name)
    site_addons = _s.get('addons', [])
    skip_list = _s.get('skip', {}).get('addons', [])
    flag_info = _s.get('tags', {})
    dev_list = []
    # whether we want to override branches
    use_branch = opts.use_branch
    # we need to construct a dictonary with path elements to fix
    # the access urls according to the way we want to access the code repositories
    # we construct an sa_dic with
    #    {'gitlab.redcor.ch': 'ssh://git@gitlab.redcor.ch:10022/', 'github...', 'access url', ..}
    sa_string = BASE_INFO.get('repo_mapper', '')
    if sa_string.endswith('/'):
        sa_string = sa_string[:-1]
    sa_dic = {}
    if sa_string:
        parts = sa_string.split(',')
        for part in parts:
            if '=' in part:
                pp = part.split('=')
                sa_dic[pp[0]] = pp[1]
    # restrict list of modules to update
    only_these_modules = []

    if opts.module_update:
        only_these_modules = opts.module_update.split(',')


    downloaded = [] # list of downloaded modules, shown when -v
    ubDic = {} # dic with branch per module
    for site_addon in site_addons:
        if (not site_addon.get('url')) or (not site_addon):
            continue
        names = find_addon_names(site_addon)
        # name
        url = site_addon['url'] % sa_dic
        # 'ssh://git@gitlab.redcor.ch:10022//afbs/afbs_extra_data.git'
        addon_name = site_addon.get('addon_name', url.split('/')[-1].split('.git')[0])
        # if we want to handle only some modules
        if only_these_modules:
            if addon_name and addon_name not in only_these_modules:
                continue
            only_these_modules.pop(only_these_modules.index(addon_name))
            if not only_these_modules:
                only_these_modules = [''] # so it is not empty        
        
        # Updating bae3b03..4bc383f
        # if the addon is in the project folders addon_path, we assume it is under developement,
        # and we do not download it
        temp_target = os.path.normpath(
            '%s/%s/%s/%s_addons/%%s' % (BASE_INFO['project_path'], opts.name, opts.name, opts.name))
        target = os.path.normpath(
            '%s/%s/addons' % (BASE_INFO['erp_server_data_path'], opts.name))
        # when we have a folder full of addons, as it is the case with OCA modules
        # they will be downloaded to download_target
        download_target = ''
        if 'target' in site_addon:
            download_target = '%s/%s' % (target, site_addon['target'])
            download_target = os.path.normpath(download_target)
        if 'group' in site_addon:
            target = '%s/%s' % (target, site_addon['group'])
        target = os.path.normpath(target)
        
        # if we want to use a branch
        if use_branch or flag_info.get(addon_name):
            # if we are checking out a flag, there is no use 
            # bother whether a branch exists, as we will end 
            # positioning our self on comit which is pointed to
            # by the flag
            if use_branch and use_branch.startswith('all'):
                # we want to check whether a module
                # has a branch, if yes use it, if not
                # use the branch from the site description
                branch = use_branch.split(':')[-1]
                target = download_target or target
                if repo_has_branch(target, branch):
                    url = site_addon['url'] % sa_dic
                    ubDic[url] = branch   
            elif use_branch:
                # we use a branch for selected addons
                if not ubDic:
                    # we need do do this only once
                    for binfo in use_branch.split(','):
                        if binfo:
                            bl = binfo.split(':')
                            if len(bl) == 2:
                                ubDic[bl[0]] = bl[1]              
        # get the branch either ..
        # - from the -b option  
        # - the addon description
        # - from the flag 
        # - or default to master
        branch = ubDic.get(
            # is there a branch asked for
            addon_name,
                # do we have a branch for the url
                ubDic.get(url,
                    # is there a flag for the addon
                    flag_info.get(addon_name,
                        # or does the site description use a branch
                        # finally as  default, use master
                        site_addon.get('branch', 'master'))))
        downloaded.append([addon_name, branch])
        
        if not dev_list or addon_name in dev_list:
            real_target = download_target or target
            cpath = os.getcwd()
            gr = GitRepo(real_target, url)
            # GitRepo can not easily tell actual branch
            try:
                # when we create this module, there is not yet anything
                if os.path.exists(real_target):
                    actual_branch = str(
                        git.Repo(real_target).active_branch)
                else:
                    actual_branch = None
            except TypeError as e:
                # when the repo does not exist yet
                # or the head is detached pointing to a flag
                message = e.message
                if 'detached' in message:
                    # "HEAD is a detached symbolic reference as it points to '669bc1f5949bc028f2a75c3e6e20fab9f20f2cfd'"
                    sha = eval(e.message.split()[-1])
                    try:
                        if sha == repo_get_tag_sha(real_target, flag_info.get(addon_name), opts.verbose):
                            actual_branch = flag_info.get(addon_name)
                    except ValueError as e:
                        if 'does not exist' in str(e):
                            pass
                        else:
                            raise
                else:
                    actual_branch = None
            # do we need to checkout a tag?
            
            if not os.path.exists(real_target) or branch != actual_branch:
                # create sandbox and check out
                try:
                    gr(branch)
                except subprocess.CalledProcessError as e:
                    print(bcolors.FAIL)
                    print('*' * 80)
                    print('target:', real_target)
                    print('actual_branch:', actual_branch)
                    print('target branch:', branch)
                    print(str(e))
                    print('*' * 80)
                    print(bcolors.ENDC)
                    continue
            os.chdir(real_target)
            #argopts['verbose'] = True
            argopts['checkremote'] = True
            return_counts = {}
            # if needed we reset the remote url
            reset_git_to = opts.__dict__.get('reset_git') and url or '' # this option does not exist, robert okt 2018
            set_git_remote(gr, reset_git_to)
            action_needed = gitcheck(return_counts)
            os.chdir(cpath)
            if action_needed:
                # what action is needed we find in return_counts
                if return_counts.get('to_pull'):
                    gr(branch)

        for name in names:            
            # we have to download all modules, also the ones in the skiplist
            # we only should not install them
            # if name and name in skip_list:
                # continue
            # if we did download the files to a target directory, we must create symlinks
            # from the target directory to the real_target
            if download_target:
                # make sure that target exists. this is not the case when we land here the first time
                if not os.path.exists(target):
                    os.mkdir(target)
                if not os.path.exists('%s/%s' % (target, name)):
                    # check if name exists in download_target
                    if os.path.exists('%s/%s' % (download_target, name)):
                        # construct the link
                        os.symlink('%s/%s' % (download_target,
                                              name), '%s/%s' % (target, name))
                    else:
                        # hopalla, nothing here to link to
                        # this is an error!
                        print(bcolors.FAIL)
                        print(('*' * 80))
                        print('%s/%s' % (download_target,
                                         name), 'does not exist')
                        print(bcolors.ENDC)
    if only_these_modules and only_these_modules[0]:
        print(bcolors.WARNING)
        print(('*' * 80))
        print('%s where not handled, maybe these are submodules and you should name it in its addons block' % only_these_modules)
        print(bcolors.ENDC)
    if opts.verbose:
        print((bcolors.OKGREEN))
        print(('*' * 80))
        for d in downloaded:
            print(d)
        print((bcolors.ENDC))     
    return result

# docker_handler ??
def XXupdate_docker_info(default_values, name, url='unix://var/run/docker.sock', required=False, start=True):
    """
    """
    cli = default_values.get('docker_client')
    if not cli:
        from docker import Client
        cli = Client(base_url=url)
        default_values['docker_client'] = cli
    registry = default_values.get('docker_registry', {})
    info = cli.containers(filters={'name': name}, all=1)
    if info:
        info = info[0]
        if info['State'] != 'running':
            if start:
                cli.restart(name)
                info = cli.containers(filters={'name': name})
                if not info:
                    raise ValueError('could not restart container %s', name)
                info = info[0]
            elif required:
                raise ValueError(
                    'container %s is stoped, no restart is requested', name)
        registry[name] = info
    else:
        if required:
            raise ValueError('required container:%s does not exist' % name)
    default_values['docker_registry'] = registry


# docker_handler ??
def XXupdate_container_info(default_values, opts):
    """
    """
    sys.path.insert(0, '..')
    try:
        from docker import Client
    except ImportError:
        print('*' * 80)
        print('could not import docker')
        print('please run bin/pip install -r install/requirements.txt')
        return
    name = opts.name
    site_info = SITES[name]
    docker = site_info.get('docker')
    if not docker or not docker.get('container_name'):
        print('the site description for %s has no docker description or no container_name' % opts.name)
        return
    # collect info on database container which allways is named 'db'
    update_docker_info(default_values, 'db', required=True)
    update_docker_info(default_values, docker['container_name'])
    # check whether we are a slave
    if site_info.get('slave_info'):
        master_site = site_info.get('slave_info').get('master_site')
        if master_site:
            update_docker_info(default_values, master_site)



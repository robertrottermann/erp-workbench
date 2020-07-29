#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import re
import socket
import subprocess
import sys
from copy import deepcopy
from io import StringIO
from pprint import pformat, pprint
from socket import gaierror
from subprocess import PIPE

import git
import psutil

import templates
from scripts.bcolors import bcolors
from scripts.messages import *
from scripts.vcs.base import UpdateError
from scripts.vcs.git import BUILDOUT_ORIGIN, GitRepo, logging

try:
    from git import Repo
except ImportError as e:
    print(MODULE_MISSING % "git")
    sys.exit()

"""
create_new_project.py
---------------------
create a new odoo project so we can easily maintain a local and a remote
set of configuration files and keep them in sync.

It knows enough about odoo to be able to treat some special values correctly

"""

# after start tag we start to look for values
START_TAG = "[login_info]"
# delimiter defines start of new value
DELIMITER = "##----"
# base path is the path from where this script is loaded
# it is wehere all config info is stored
SITE_TEMPLATE = """
    "%(site_name)s" : {
%(data)s
    },
"""


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
        "name",
        "subparser_name",
        "dockerdbpw",
        "dockerdbuser",
        "dbhost",
        "dbpw",
        "dbuser",
        "rpchost",
        "rpcport",
        "rpcuser",
        "rpcpw",
    ]
    keys = [k[0] for k in _o if k[0] not in skip]
    is_set = [k for k in _o if not (k[1] is False) and (k[0] not in skip)]
    return actual, is_set, keys


# ----------------------------------
# create_server_config
# create server config file in erp_workbench/SITENAME/openerp.conf
# @default_values   : default value
# @foldernames      : list of folders to create within the site foler
# ----------------------------------
CONFIG_NAME = {
    "odoo": {
        "config": "openerp-server.conf",
        "val_dic": {
            "server_wide_modules": "",
            "xmlrpc_port": 8069,
            "longpolling_port": 8072,
            "logfile": "/var/log/odoo/odoo_log",
            "data_dir": "/var/lib/odoo",
        },
    }
}


def create_server_config(handler):
    """
    create server config file in $erp_server_data_path$/SITENAME/openerp.conf
    this is the config file used by docker, or not at all ??
    with all variables set as environment variables
    @default_values   : default value
    @foldernames      : list of folders to create within the site foler
    """
    from templates.openerp_cfg_defaults import CONFIG_DEFAULTS

    name = handler.site_name
    if not name:
        # we need a site name to create a server config
        return
    erp_type = handler.site.get("erp_type", "odoo")
    config_name = CONFIG_NAME[erp_type]["config"]
    # FIX: must NOT be read from site
    erp_admin_pw = handler.site.get("odoo_admin_pw", "")
    base_info = handler.base_info
    p = os.path.normpath("%s/%s" % (base_info["erp_server_data_path"], name))
    # make sure we use an updated addons_path
    handler.default_values["docker_site_addons_path"] = handler.docker_site_addons_path
    # now copy a template openerp-server.conf
    handler.default_values["erp_admin_pw"] = erp_admin_pw
    template = open("%s/%s" % (templates.__path__[0], config_name), "r").read()
    if os.path.exists("%s/etc/" % p):
        f = open("%s/etc/%s" % (p, config_name), "w")
        f.write(template % handler.default_values)
        # write rest of the values to the config file
        # get them either from site description site_settings.server_config stanza
        # or CONFIG_DEFAULTS
        server_config = handler.site.get("site_settings", {}).get("server_config", {})
        def_dic = {}
        def_dic.update(handler.default_values)
        def_dic.update(CONFIG_NAME[erp_type]["val_dic"])
        for k, v in list(CONFIG_DEFAULTS.items()):
            vv = server_config.get(k, v)
            if isinstance(vv, str):
                vv = vv % def_dic
            line = "%s = %s\n" % (k, vv)
            f.write(line)
        f.close()
    else:
        # should never happen
        print(bcolors.FAIL + "ERROR: folder %s does not exist" % p + bcolors.ENDC)


# ----------------------------------
# get_single_value
# ask value from user
# @name         : name of the value
# @explanation  : explanation of the value
# @default      : default value
# @prompt       : prompt to display
# ----------------------------------
def get_single_value(name, explanation, default, prompt="%s [%s]:"):
    """
    ask value from user
    @name         : name of the value
    @explanation  : explanation of the value
    @default      : default value
    @prompt       : prompt to display
    """
    # get input from user for a single value. present expanation and default value
    print("*" * 50)
    print(explanation)
    result = input(prompt % (name, default))
    if not result:
        result = default
    return result


def list_sites(sites_dic, quiet=False, name=""):
    """
    list sitenames listed in the sites_dic
    @sites_dic    : dictionary with info about sites
                    this is the combination of sites.py and local_sites.py
    quiet is set when testing
    """
    keys = list(sites_dic.keys())
    keys.sort()
    for key in keys:
        origin = sites_dic[key].get("site_list_name", "")
        if origin:
            origin = ":%s" % origin
        if sites_dic[key].get("is_local"):
            if not quiet:
                if name in key:
                    print("%s%s (local)" % (key, origin))
        else:
            if not quiet:
                if name in key:
                    print("%s%s" % (key, origin))


# ----------------------------------
# find_addon_names
# find the names of an addon
# @addon        : addon to find out names
# an addon can have more than one name when more than one addon has to be
# installed from a folder of addons
# return: list of names
# ----------------------------------
def find_addon_names(addon):
    name = ""
    names = []
    a = addon
    try:
        if "names" in a:
            names = a["names"]
        elif "name" in a:
            name = a["name"]
        elif "group" in a:
            name = a["group"]
        elif "add_path" in a:
            name = a["add_path"]
        names = names + [name]
    except AttributeError:
        print(bcolors.FAIL, a, bcolors.ENDC)
        input("hit enter to continue")

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


def set_git_remote(repo, reset_git_to=""):
    # make sure we have tracking info
    # this fails, if allready defined
    target = repo.target_dir
    is_new = not os.path.exists(target)
    os.chdir(target)
    url = repo.url
    if is_new:
        repo.log_call(["git", "init", target])
    if reset_git_to:
        try:
            repo.log_call(["git", "remote", "rm", BUILDOUT_ORIGIN])
        except Exception as e:
            # was probaly removed ..
            pass
        url = reset_git_to
    repo.log_call(
        [
            "git",
            "remote",
            "add" if (is_new or reset_git_to) else "set-url",
            BUILDOUT_ORIGIN,
            url,
        ],
        log_level=logging.DEBUG,
    )


def need_git_pull(
    name, target, branch, changes=[], changes_only=False, reset_git=False
):
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
        repo.git.execute(
            "git branch --set-upstream-to=origin/%s %s" % (branch, branch), shell=True
        )
    except Exception as e:
        str(e)
    for k, cmdline in [
        ("LOCAL", "git rev-parse @"),
        ("REMOTE", "git rev-parse @{u}"),
        ("BASE", "git merge-base @ @{u}"),
    ]:
        os.chdir(target)  # probably not neccessary
        p = subprocess.Popen(cmdline, stdout=PIPE, shell=True)
        res = p.communicate()
        res_dic[k] = res[0]

    os.chdir(cur_dir)

    if res_dic["BASE"] == res_dic["REMOTE"]:
        # local has changed
        try:
            changes = repo.git.diff("HEAD~1..HEAD", name_only=True)
        except:
            pass
        if changes_only:
            return changes
    if res_dic["LOCAL"] == res_dic["REMOTE"]:
        # is in sync
        return False
    elif res_dic["LOCAL"] == res_dic["BASE"]:
        # remote has changed
        return True
    elif res_dic["BASE"] != res_dic["REMOTE"]:
        # has diverged
        print(GIT_REPO_DIVERGED % repo.remotes[0].url)
        return False

    return True


def repo_get_tag_sha(repo_path, tag, verbose=False):
    if not os.path.exists(repo_path):
        print(bcolors.WARNING)
        print("*******************************")
        print(repo_path, "not yet initialized")
        print("can not check what branch exists")
        print("please rerun after the repro is initialized")
        return
    else:
        repo = git.Repo(repo_path)
        try:
            tag_info = repo.tag("refs/tags/%s" % tag)
        except ValueError as e:
            # tag does not exist
            return None
    return str(tag_info.commit)  # '669bc1f5949bc028f2a75c3e6e20fab9f20f2cfd'


def repo_has_branch(repo_path, branch, verbose=False):
    if not os.path.exists(repo_path):
        print(bcolors.WARNING)
        print("*******************************")
        print(repo_path, "not yet initialized")
        print("can not check what branch exists")
        print("please rerun after the repro is initialized")
        return
    else:
        repo = git.Repo(repo_path)
    remote_branches = []
    if verbose:
        print("------------------------------------------")
        print(repo_path)
    for ref in repo.git.branch("-r").split("\n"):
        br = ref.split("/")[-1]
        if verbose:
            print(br)
        remote_branches.append(br)
    if verbose:
        print(">>>>>>>>>>", branch in remote_branches)
    return branch in remote_branches


def checkout_sa(opts, handler):
    """
    get addons from repository
    @opts   : options as entered by the user
    """
    if not opts.name:
        # need a  site_name to do anything sensible
        return
    from .git_check import gitcheck, argopts

    site = handler.site
    result = {"failed": [], "need_reload": []}
    site_addons = []
    is_local = site.get("is_local")
    _s = site
    site_addons = _s.get("addons", [])
    skip_list = _s.get("skip", {}).get("addons", [])
    flag_info = _s.get("tags", {})
    dev_list = []
    # whether we want to override branches
    use_branch = opts.use_branch
    # we need to construct a dictonary with path elements to fix
    # the access urls according to the way we want to access the code repositories
    # we construct an sa_dic with
    #    {'gitlab.redcor.ch': 'ssh://git@gitlab.redcor.ch:10022/', 'github...', 'access url', ..}
    base_info = handler.base_info
    sa_string = base_info.get("repo_mapper", "")
    if sa_string.endswith("/"):
        sa_string = sa_string[:-1]
    sa_dic = {}
    if sa_string:
        parts = sa_string.split(",")
        for part in parts:
            if "=" in part:
                pp = part.split("=")
                sa_dic[pp[0]] = pp[1]
    # restrict list of modules to update
    only_these_modules = []

    if opts.module_update:
        only_these_modules = opts.module_update.split(",")

    downloaded = []  # list of downloaded modules, shown when -v
    ubDic = {}  # dic with branch per module
    for site_addon in site_addons:
        if (not site_addon.get("url")) or (not site_addon):
            continue
        names = find_addon_names(site_addon)
        # name
        try:
            url = site_addon["url"] % sa_dic
        except KeyError as e:
            print(bcolors.FAIL)
            print("*" * 80)
            print("Error: is the config.yaml/repo_mapper in place?")
            print(str(e))
            print(bcolors.ENDC)
            sys.exit()
        # 'ssh://git@gitlab.redcor.ch:10022//afbs/afbs_extra_data.git'
        addon_name = site_addon.get("addon_name", url.split("/")[-1].split(".git")[0])
        # if we want to handle only some modules
        if only_these_modules:
            if addon_name and addon_name not in only_these_modules:
                continue
            only_these_modules.pop(only_these_modules.index(addon_name))
            if not only_these_modules:
                only_these_modules = [""]  # so it is not empty

        # Updating bae3b03..4bc383f
        # if the addon is in the project folders addon_path, we assume it is under developement,
        # and we do not download it
        temp_target = os.path.normpath(
            "%s/%s/%s/%s_addons/%%s"
            % (base_info["project_path"], opts.name, opts.name, opts.name)
        )
        target = os.path.normpath(
            "%s/%s/addons" % (base_info["erp_server_data_path"], opts.name)
        )
        # when we have a folder full of addons, as it is the case with OCA modules
        # they will be downloaded to download_target
        download_target = ""
        if "target" in site_addon:
            download_target = "%s/%s" % (target, site_addon["target"])
            download_target = os.path.normpath(download_target)
        if "group" in site_addon:
            target = "%s/%s" % (target, site_addon["group"])
        target = os.path.normpath(target)

        # if we want to use a branch
        if use_branch or flag_info.get(addon_name):
            # if we are checking out a flag, there is no use
            # bother whether a branch exists, as we will end
            # positioning our self on comit which is pointed to
            # by the flag
            if use_branch and use_branch.startswith("all"):
                # we want to check whether a module
                # has a branch, if yes use it, if not
                # use the branch from the site description
                branch = use_branch.split(":")[-1]
                target = download_target or target
                if repo_has_branch(target, branch):
                    url = site_addon["url"] % sa_dic
                    ubDic[url] = branch
            elif use_branch:
                # we use a branch for selected addons
                if not ubDic:
                    # we need do do this only once
                    for binfo in use_branch.split(","):
                        if binfo:
                            bl = binfo.split(":")
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
            ubDic.get(
                url,
                # is there a flag for the addon
                flag_info.get(
                    addon_name,
                    # or does the site description use a branch
                    # finally as  default, use master
                    site_addon.get("branch", "master"),
                ),
            ),
        )
        downloaded.append([addon_name, branch])

        if not dev_list or (addon_name in dev_list):
            real_target = download_target or target
            if os.path.realpath(real_target) == os.path.realpath(
                handler.local_addon_path_prefix[1:]
            ):
                real_target = os.path.normpath(
                    "%s/%s" % (real_target, handler.site_name)
                )
            cpath = os.getcwd()
            gr = GitRepo(real_target, url)
            # GitRepo can not easily tell actual branch
            try:
                # when we create this module, there is not yet anything
                if os.path.exists(real_target):
                    actual_branch = str(git.Repo(real_target).active_branch)
                else:
                    actual_branch = None
            except TypeError as e:
                # when the repo does not exist yet
                # or the head is detached pointing to a flag
                message = e.message
                if "detached" in message:
                    # "HEAD is a detached symbolic reference as it points to '669bc1f5949bc028f2a75c3e6e20fab9f20f2cfd'"
                    sha = eval(e.message.split()[-1])
                    try:
                        if sha == repo_get_tag_sha(
                            real_target, flag_info.get(addon_name), opts.verbose
                        ):
                            actual_branch = flag_info.get(addon_name)
                    except ValueError as e:
                        if "does not exist" in str(e):
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
                    print("*" * 80)
                    print("target:", real_target)
                    print("actual_branch:", actual_branch)
                    print("target branch:", branch)
                    print(str(e))
                    print("*" * 80)
                    print(bcolors.ENDC)
                    continue
            os.chdir(real_target)
            # argopts['verbose'] = True
            argopts["checkremote"] = True
            return_counts = {}
            # if needed we reset the remote url
            reset_git_to = (
                opts.__dict__.get("reset_git") and url or ""
            )  # this option does not exist, robert okt 2018
            set_git_remote(gr, reset_git_to)
            action_needed = gitcheck(return_counts)
            os.chdir(cpath)
            if action_needed:
                # what action is needed we find in return_counts
                if return_counts.get("to_pull"):
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
                if not os.path.exists("%s/%s" % (target, name)):
                    # check if name exists in download_target
                    if os.path.exists("%s/%s" % (download_target, name)):
                        # construct the link
                        os.symlink(
                            "%s/%s" % (download_target, name), "%s/%s" % (target, name)
                        )
                    else:
                        # hopalla, nothing here to link to
                        # this is an error!
                        print(bcolors.FAIL)
                        print(("*" * 80))
                        print("%s/%s" % (download_target, name), "does not exist")
                        print(bcolors.ENDC)
    if only_these_modules and only_these_modules[0]:
        print(bcolors.WARNING)
        print(("*" * 80))
        print(
            "%s where not handled, maybe these are submodules and you should name it in its addons block"
            % only_these_modules
        )
        print(bcolors.ENDC)
    if opts.verbose:
        print((bcolors.OKGREEN))
        print(("*" * 80))
        for d in downloaded:
            print(d)
        print((bcolors.ENDC))
    return result


# docker_handler ??
def XXupdate_docker_info(
    default_values, name, url="unix://var/run/docker.sock", required=False, start=True
):
    """
    """
    cli = default_values.get("docker_client")
    if not cli:
        from docker import Client

        cli = Client(base_url=url)
        default_values["docker_client"] = cli
    registry = default_values.get("docker_registry", {})
    info = cli.containers(filters={"name": name}, all=1)
    if info:
        info = info[0]
        if info["State"] != "running":
            if start:
                cli.restart(name)
                info = cli.containers(filters={"name": name})
                if not info:
                    raise ValueError("could not restart container %s", name)
                info = info[0]
            elif required:
                raise ValueError(
                    "container %s is stoped, no restart is requested", name
                )
        registry[name] = info
    else:
        if required:
            raise ValueError("required container:%s does not exist" % name)
    default_values["docker_registry"] = registry


# docker_handler ??
def XXupdate_container_info(default_values, opts):
    """
    """
    sys.path.insert(0, "..")
    try:
        from docker import Client
    except ImportError:
        print("*" * 80)
        print("could not import docker")
        print("please run bin/pip install -r install/requirements.txt")
        return
    name = opts.name
    site_info = SITES[name]
    docker = site_info.get("docker")
    if not docker or not docker.get("container_name"):
        print(
            "the site description for %s has no docker description or no container_name"
            % opts.name
        )
        return
    # collect info on database container which allways is named 'db'
    update_docker_info(default_values, "db", required=True)
    update_docker_info(default_values, docker["container_name"])
    # check whether we are a slave
    if site_info.get("slave_info"):
        master_site = site_info.get("slave_info").get("master_site")
        if master_site:
            update_docker_info(default_values, master_site)


# =============================================================
# get server info from site description
# =============================================================
def get_remote_server_info(opts, use_name=None, SITES={}, REMOTE_SERVERS={}):
    """
    get server info from site description
    """
    xx  # sites und remoteserver übergeben
    import socket

    serverDic = {}
    if not use_name:
        name = opts.name
    else:
        # in transfer, we do not want to use the name
        # provided in opts ..
        name = use_name
        if not SITES.get(name):
            print("*" * 80)
            print("provided use_name=%s is not valid on this server" % use_name)
            raise ValueError(
                "provided use_name=%s is not valid on this server" % use_name
            )

    if opts.use_ip:
        try:
            addr = socket.gethostbyname(opts.use_ip)
        except gaierror:
            print((bcolors.FAIL))
            print(("*" * 80))
            print(("% is not a vali ip" % opts.use_ip))
            print((bcolors.ENDC))
            return
        serverDic = REMOTE_SERVERS.get(addr)
    else:
        d = deepcopy(SITES[name])
        serverDic = d.get("remote_server")
        if not serverDic:
            print("*" * 80)
            print(
                "the site description for %s has no remote_server description"
                % opts.name
            )
            print("please add one")
            print("*" * 80)
            serverDic = {
                "remote_url": d["remote_url"],
                "remote_data_path": d["remote_data_path"],
                "remote_user": d["remote_user"],
            }
    if opts.use_ip_target:
        try:
            addr = socket.gethostbyname(opts.use_ip_target)
        except gaierror:
            print((bcolors.FAIL))
            print(("*" * 80))
            print(("% is not a vali ip" % opts.use_ip_target))
            print((bcolors.ENDC))
            return
        serverDic_target = REMOTE_SERVERS.get(addr)
    if not serverDic:
        print("*" * 80)
        print("the ip %s has no site description" % ip)
        print("please add one using bin/s support --add-server %s" % ip)
        print("*" * 80)
        sys.exit()
    # if the remote url is overridden, replace it now
    if opts.use_ip:
        if not serverDic.get("remote_url_orig"):
            # do not overwrite if we land here a second time
            serverDic["remote_url_orig"] = SITES[name]["remote_server"]["remote_url"]
        serverDic["remote_url"] = opts.use_ip
    if opts.use_ip_target:
        serverDic["serverDic_target"] = serverDic_target

    return serverDic

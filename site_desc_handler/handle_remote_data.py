import os
import docker
from copy import deepcopy
from docker import Client
from socket import gaierror
from scripts.bcolors import bcolors
from config import REMOTE_SERVERS

    # @property
    # def remote_servers(self):
    #     return REMOTE_SERVERS
        
    # @property
    # def remote_user(self):
    #     # from the list of remote servers
    #     return self.remote_servers.get(
    #         # find as what user we access that remote server
    #         self.remote_url, {}).get('remote_user', '')

    # @property
    # def remote_user_pw(self):
    #     # from the list of remote servers
    #     return self.remote_servers.get(
    #         # and finally find what pw to use on the remote server
    #         # this pw is patched in at runtime
    #         self.remote_url, {}).get('remote_pw', '')

    # @property
    # def remote_data_path(self):
    #     # refacture the following as the above props
    #     # we first check whether config/localdata.py has an remote path set.
    #     remote_dic = self.remote_server
    #     remote_data_path = remote_dic.get(
    #         'remote_data_path', remote_dic.get('remote_path'))
    #     if remote_data_path:
    #         return remote_data_path
    #     # then we check whether config/localdata.py has an remote path set.
    #     remote_data_path =  self.remote_servers.get(
    #         # and finally find what pw to use on the remote server
    #         # this pw is patched in at runtime
    #         self.remote_url, {}).get('remote_data_path', '')
    #     return remote_data_path

    # # was an alias to remote_url
    # @property
    # def remote_server(self):
    #     return self.site.get('remote_server', {})

    # @property
    # def remote_sites_home(self):
    #     return self.site.get('sites_home', '/root/erp_workbench')

    # @property
    # def remote_url(self):
    #     return self.remote_server.get('remote_url', '')

# get server info from site description
# =============================================================
def get_remote_server_info(opts, sites, use_name=None):
    """
    get server info from site description
    """
    import socket
    serverDic = {}
    if not use_name:
        name = opts.name
    else:
        # in transfer, we do not want to use the name
        # provided in opts ..
        name = use_name
        if not sites.get(name):
            print('*' * 80)
            print('provided use_name=%s is not valid on this server' % use_name)
            raise ValueError(
                'provided use_name=%s is not valid on this server' % use_name)

    if opts.use_ip:
        try:
            addr = socket.gethostbyname(opts.use_ip)
        except gaierror:
            print((bcolors.FAIL))
            print(('*' * 80))
            print(('% is not a valid ip' % opts.use_ip))
            print((bcolors.ENDC))
            return
        serverDic = REMOTE_SERVERS.get(addr)
    else:
        d = deepcopy(sites[name])
        serverDic = d.get('remote_server')
        if not serverDic:
            print('*' * 80)
            print('the site description for %s has no remote_server description' % opts.name)
            print('please add one')
            print('*' * 80)
            serverDic = {
                'remote_url': d['remote_url'],
                'remote_data_path': d['remote_data_path'],
                'remote_user': d['remote_user'],
            }
    if opts.use_ip_target:
        try:
            addr = socket.gethostbyname(opts.use_ip_target)
        except gaierror:
            print((bcolors.FAIL))
            print(('*' * 80))
            print(('% is not a vali ip' % opts.use_ip_target))
            print((bcolors.ENDC))
            return
        serverDic_target = REMOTE_SERVERS.get(addr)

    # if the remote url is overridden, replace it now
    if opts.use_ip:
        if not serverDic.get('remote_url_orig'):
            # do not overwrite if we land here a second time
            serverDic['remote_url_orig'] = sites[name]['remote_server']['remote_url']
        serverDic['remote_url'] = opts.use_ip
    if opts.use_ip_target:
        serverDic['serverDic_target'] = serverDic_target

    return serverDic

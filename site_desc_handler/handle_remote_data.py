import os
import docker
from docker import Client

def collect_remote_info(self, site):
    """collect remote info from the site description
    
    Arguments:
        sites {dict} -- site description
    """

    # old setting
    if 'site_name' in site.keys():
        remote_server = site['remote_server']
        self._remote_url = remote_server.get('remote_url', '')
        self._remote_data_path = remote_server.get('remote_data_path', '')
        self._remote_user = remote_server.get('remote_user', '')
        self._remote_sites_home = remote_server.get('remote_sites_home', '')
        self._redirect_email_to = remote_server.get('redirect_emil_to', '')
    else:
        pass

# =============================================================
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
            print(('% is not a vali ip' % opts.use_ip))
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
    if not serverDic:
        print('*' * 80)
        print('the ip %s has no site description' % ip)
        print('please add one using bin/s support --add-server %s' % ip)
        print('*' * 80)
        sys.exit()
    # if the remote url is overridden, replace it now
    if opts.use_ip:
        if not serverDic.get('remote_url_orig'):
            # do not overwrite if we land here a second time
            serverDic['remote_url_orig'] = sites[name]['remote_server']['remote_url']
        serverDic['remote_url'] = opts.use_ip
    if opts.use_ip_target:
        serverDic['serverDic_target'] = serverDic_target

    return serverDic

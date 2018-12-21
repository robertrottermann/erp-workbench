import os
import docker
from docker import Client

def collect_remote_info(self, site):
    """collect remote info from the site description
    
    Arguments:
        sites {dict} -- site description
    """

    # old setting
    if 'docker_hub' in site.keys():
        docker_hub = site['docker_hub']
        docker = site.get('docker', {})
        # docker hub
        self._docker_hub_user = docker_hub.get('hub_name', '')
        self._docker_hub_user_pw = docker_hub.get('docker_hub_pw')
        
        # docker
        self._docker_base_image = docker.get('base_image', 'camptocamp/odoo-project:%s-latest' % self.erp_version),
        erp_image_version = docker.get('erp_image_version', docker.get('odoo_image_version'))
        if not erp_image_version:
            erp_image_version = 'no-erp_image_version-defined'
        self._docker_image_version = erp_image_version
        self._docker_container_name = docker.get('container_name', self.site_name)
        self._docker_rpc_port = docker.get(
            'erp_port', docker.get('odoo_port'))
        docker_long_polling_port = docker.get('erp_longpoll', docker.get('odoo_longpoll'))
        if not docker_long_polling_port:
                long_polling_port = int(self.docker_rpc_port) + 10000
        self._docker_long_polling_port = docker_long_polling_port     
        self._docker_external_user_group_id = docker.get('external_user_group_id', '104:107')
        self._docker_hub_name =  docker.get('docker_hub_name', '')
        if self.subparser_name == 'docker':
            self._docker_db_admin = self.opts.dockerdbuser or self.docker_defaults.get('dockerdbuser', '')
        else:
            self._docker_db_admin = self.docker_defaults.get('dockerdbuser', '')                                                                                 
    else:
        pass

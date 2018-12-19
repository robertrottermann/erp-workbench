import docker
from docker import Client


def collect_docker_info(self, opts, sites, parsername):
    pass

class DockerHandlerMixin(object):
    docker_registry = None

    def setup_docker_env(self):
        collect_docker_info(self, opts, sites, parsername)

    @property
    def container_name(self):
        return self.docker_info['container_name']

    @property
    def erp_image_version(self):
        erp_image_version = self.docker_info.get('erp_image_version', self.docker_info.get('odoo_image_version'))
        if not erp_image_version:
            erp_image_version = DOCKER_DEFAULTS.get('erp_image_version', 'no-erp_image_version-defined')
        return erp_image_version
        
    @property
    def docker_postgres_port(self):
        if self.parsername == 'docker':
            return self.postgres_port
        # does it make sense to return a default at all??
        return '8069'

    @property
    def db_container_ip(self):
        if self.parsername == 'docker':
            return self.db_ip
        # does it make sense to return a default at all??
        return 'localhost'
    
    @property
    def docker_default_port(self):
        return PROJECT_DEFAULTS.get('docker_default_port', 9000)

    @property
    def docker_info(self):
        return self.site.get('docker', {})
    
    @property
    def docker_hub_name(self):
        return self.docker_info.get('hub_name', '')
        
    @property
    def docker_rpc_port(self):
        return self.docker_info.get(
            'erp_port', self.docker_info.get('odoo_port'))

    @property
    def docker_long_polling_port(self):
        long_polling_port = self.docker_info.get('erp_longpoll', self.docker_info.get('odoo_longpoll'))
        if not long_polling_port:
            long_polling_port = int(self.docker_rpc_port) + 10000
        return long_polling_port

#!bin/python
# -*- encoding: utf-8 -*-
import os
import sys
import shutil
import docker

from scripts.bcolors import bcolors
from docker_handler.docker_handler import DockerHandler
from scripts.messages import DOCKER_IMAGE_CREATE_PLEASE_WAIT, DOCKER_IMAGE_CREATE_FAILED, DOCKER_BITNAMI_IMAGE_CREATE_DONE
"""
https://medium.com/programming-kubernetes/building-stuff-with-the-kubernetes-api-1-cc50a3642
"""
"""
https://github.com/ljakimczuk/pyhelm is using pyhelm
concepts:
    a pod runs an docker image!!
        it runs a docker container

    deployments are the central metaphor for what we consider an app
    They are described as a collection of resources and references
    They are typically described in yaml format


    A deployment has:
        Define the deployment
            What containers we use
            What services these containers do offer
            Where do they come from

            A deployment can have any number of pods

        Expose its services
            What tcp port
                -> --type=NodePort
                in deployment.yaml -> - containerPort: 8080
                    kubectl expose deployment tomcat-deployment --type=NodePort
                    minikube service tomcat-deployment --url --> http://192.168.99.102:31281

            What http services
            Where to reach them

        Deploy it to the cluster

    questions to dave:
        how do we structure our namespace?

1.
from pyhelm.repo import from_repo

chart_path = chart_versions = from_repo('https://kubernetes-charts.storage.googleapis.com/', 'mariadb')
print(chart_path)

2.
from pyhelm.chartbuilder import ChartBuilder

chart = ChartBuilder({'name': 'mongodb', 'source': {'type': 'directory', 'location': '/tmp/pyhelm-kibwtj8d/mongodb'}})

# than we can get chart meta data etc
In [9]: chart.get_metadata()
Out[9]:
name: "mongodb"
version: "0.4.0"
description: "Chart for MongoDB"

3.
from pyhelm.chartbuilder import ChartBuilder
from pyhelm.tiller import Tiller

chart = ChartBuilder({'name': 'mongodb', 'source': {'type': 'directory', 'location': '/tmp/pyhelm-kibwtj8d/mongodb'}})
t.install_release(chart.get_helm_chart(), dry_run=False, namespace='default')



Chart.yaml:
-----------
appVersion: 11.0.20181215
description: A suite of web based open source business apps.
engine: gotpl
home: https://www.odoo.com/
icon: https://bitnami.com/assets/stacks/odoo/img/odoo-stack-110x117.png
keywords:
- odoo
- crm
- www
- http
- web
maintainers:
- email: containers@bitnami.com
  name: Bitnami
name: odoo
sources:
- https://github.com/bitnami/bitnami-docker-odoo
version: 5.0.2

    The above lines have the following meaning:
    -------------------------------------------
    appVersion: 11.0.20181215:
        It is a way of specifying the version of the application
        Has nothing to do with the version field.

    description: ...

    engine: gotpl
        The name of the template engine (optional, defaults to gotpl)

    home: https://www.odoo.com/
        The URL of this project's home page (optional)
    
    icon: ...

    keywords:
        A list of keywords about this project (optional)

    name: odoo ..
    maintainers: ..

    sources:
        A list of URLs to source code for this project (optional)

    version: 5.0.2
        Charts and Versioning

        Every chart must have a version number. 
        A version must follow the SemVer 2 standard. Unlike Helm Classic, Kubernetes Helm uses 
        version numbers as release markers. Packages in repositories are identified by name plus version.

        For example, an nginx chart whose version field is set to version: 1.2.3 will be named:

        nginx-1.2.3.tgz


"""
"""The following table lists the configurable parameters of the Odoo chart and their default values.

|               Parameter               |                Description                                  |                   Default                      |
|---------------------------------------|-------------------------------------------------------------|------------------------------------------------|
| `global.imageRegistry`                | Global Docker image registry                                | `nil`                                          |
| `image.registry`                      | Odoo image registry                                         | `docker.io`                                    |
| `image.repository`                    | Odoo Image name                                             | `bitnami/odoo`                                 |
| `image.tag`                           | Odoo Image tag                                              | `{VERSION}`                                    |
| `image.pullPolicy`                    | Image pull policy                                           | `Always`                                       |
| `image.pullSecrets`                   | Specify docker-registry secret names as an array            | `[]` (does not add image pull secrets to deployed pods) |
| `odooUsername`                        | User of the application                                     | `user@example.com`                             |
| `odooPassword`                        | Admin account password                                      | _random 10 character long alphanumeric string_ |
| `odooEmail`                           | Admin account email                                         | `user@example.com`                             |
| `smtpHost`                            | SMTP host                                                   | `nil`                                          |
| `smtpPort`                            | SMTP port                                                   | `nil`                                          |
| `smtpUser`                            | SMTP user                                                   | `nil`                                          |
| `smtpPassword`                        | SMTP password                                               | `nil`                                          |
| `smtpProtocol`                        | SMTP protocol [`ssl`, `tls`]                                | `nil`                                          |
| `service.type`                        | Kubernetes Service type                                     | `LoadBalancer`                                 |
| `service.port`                        | Service HTTP port                                           | `80`                                           |
| `service.loadBalancer`                | Kubernetes LoadBalancerIP to request                        | `nil`                                          |
| `service.externalTrafficPolicy`       | Enable client source IP preservation                        | `Cluster`                                      |
| `service.nodePort`                    | Kubernetes http node port                                   | `""`                                           |
| `ingress.enabled`                     | Enable ingress controller resource                          | `false`                                        |
| `ingress.hosts[0].name`               | Hostname to your Odoo installation                          | `odoo.local`                                   |
| `ingress.hosts[0].path`               | Path within the url structure                               | `/`                                            |
| `ingress.hosts[0].tls`                | Utilize TLS backend in ingress                              | `false`                                        |
| `ingress.hosts[0].certManager`        | Add annotations for cert-manager                            | `false`                                        |
| `ingress.hosts[0].tlsSecret`          | TLS Secret (certificates)                                   | `odoo.local-tls-secret`                        |
| `ingress.hosts[0].annotations`        | Annotations for this host's ingress record                  | `[]`                                           |
| `ingress.secrets[0].name`             | TLS Secret Name                                             | `nil`                                          |
| `ingress.secrets[0].certificate`      | TLS Secret Certificate                                      | `nil`                                          |
| `ingress.secrets[0].key`              | TLS Secret Key                                              | `nil`                                          |
| `resources`                           | CPU/Memory resource requests/limits                         | Memory: `512Mi`, CPU: `300m`                   |
| `persistence.storageClass`            | PVC Storage Class                                           | `nil` (uses alpha storage class annotation)    |
| `persistence.accessMode`              | PVC Access Mode                                             | `ReadWriteOnce`                                |
| `persistence.size`                    | PVC Storage Request                                         | `8Gi`                                          |
| `postgresql.postgresqlPassword`       | PostgreSQL password                                         | `nil`                                          |
| `postgresql.persistence.enabled`      | Enable PostgreSQL persistence using PVC                     | `true`                                         |
| `postgresql.persistence.storageClass` | PVC Storage Class for PostgreSQL volume                     | `nil` (uses alpha storage class annotation)    |
| `postgresql.persistence.accessMode`   | PVC Access Mode for PostgreSQL volume                       | `ReadWriteOnce`                                |
| `postgresql.persistence.size`         | PVC Storage Request for PostgreSQL volume                   | `8Gi`                                          |
| `livenessProbe.enabled`               | Enable/disable the liveness probe                           | `true`                                         |
| `livenessProbe.initialDelaySeconds`   | Delay before liveness probe is initiated                    | 300                                            |
| `livenessProbe.periodSeconds`         | How often to perform the probe                              | 30                                             |
| `livenessProbe.timeoutSeconds`        | When the probe times out                                    | 5                                              |
| `livenessProbe.failureThreshold`      | Minimum consecutive failures to be considered failed        | 6                                              |
| `livenessProbe.successThreshold`      | Minimum consecutive successes to be considered successful   | 1                                              |
| `readinessProbe.enabled`              | Enable/disable the readiness probe                          | `true`                                         |
| `readinessProbe.initialDelaySeconds`  | Delay before readinessProbe is initiated                    | 30                                             |
| `readinessProbe.periodSeconds   `     | How often to perform the probe                              | 10                                             |
| `readinessProbe.timeoutSeconds`       | When the probe times out                                    | 5                                              |
| `readinessProbe.failureThreshold`     | Minimum consecutive failures to be considered failed        | 6                                              |
| `readinessProbe.successThreshold`     | Minimum consecutive successes to be considered successful   | 1                                              |

"""



from scripts.bcolors import bcolors

try:
    import pint
    from kubernetes import client as ku_cli
    from kubernetes import config as ku_con
    from kubernetes import watch as ku_watch
except ImportError as e:
    print(bcolors.FAIL)
    print('*' * 80)
    print('some library could not be installed')
    print('please run: pip install -r install/requirements.txt')
    print(str(e))
    print(bcolors.ENDC)
    sys.exit()

try:
    import grpc
    from pyhelm import tiller
    from pyhelm import chartbuilder
    from pyhelm.repo import from_repo
    HasPyhelm = True
except ImportError as e:
    print(bcolors.FAIL)
    print('*' * 80)
    print('pyhelm could not be installed')
    print('please download and install it from:')
    print('https://github.com/redcor/pyhelm.git')
    print(str(e))
    HasPyhelm = False
    print(bcolors.ENDC)

class KuberHandlerHelm(DockerHandler):
    """KuberHandlerHelm
    just calls helm using popen calls
    
    Arguments:
        object {[type]} -- [description]
    """
    def __init__(self, opts, sites, parsername='', config_data = {}):
        super().__init__(opts, sites, parsername)
        """initialize KuberHandlerHelm 
        with an url to the repository and a name of the chart to deal with      
        
        Arguments:
            url {string} -- either an url starting with http[s]:// or a well known helm repo like stable
            chart_name {string} -- name of the chart we deal with
        """
        self._chart_url = config_data.get('chart_url', 'stable')
        self._chart_name = config_data.get('chart_name', 'odoo')
        default_target = os.path.normpath('%s/helm' % (self.site_data_dir))
        helm_target = config_data.get('helm_target', default_target)
        self._helm_target = helm_target
        # make sure the target path exists
        os.makedirs(helm_target, exist_ok=True)
        self._config_data = config_data
    
    _chart_url = ''
    @property
    def chart_url(self):
        return self._chart_url

    _chart_name = ''
    @property
    def chart_name(self):
        return self._chart_name

    _config_data = ''
    @property
    def config_data(self):
        return self._config_data
    
    _helm_target = ''
    @property
    def helm_target(self):
        return self._helm_target

    def fetch(self, target=None, result={}):
        """execute the helm fetch command
        
        Keyword Arguments:
            target {string} -- target folder to extract the cahsrt into (default: {None})
                               If target is none, install it in the sitedescriptions helm folder
            result {dict} -- container to return used settings, mostly for testing
        """
        # construct what chart to download
        if self.chart_url.startswith('http://') or self.chart_url.startswith('https://'):
            chart_path = '' # FIX!!
        else:
            chart_path = '%s/%s' % (self.chart_url, self.chart_name)
        helm_cmd = shutil.which('helm')
        cmd_line = [helm_cmd, 'fetch', chart_path, '-d', self.helm_target]
        if not helm_cmd:
            print(bcolors.FAIL)
            print('*' * 80)
            print('helm could not be found. Is it installed?')
            print(bcolors.ENDC)
            return
        if self.config_data.get('untar'):
            cmd_line.append('--untar')
        result = self.run_commands_run([cmd_line])
        return {'result' : result, 'cmd_line' : cmd_line, 'chart_path' : chart_path, 'helm_target' : self.helm_target}

    def build_image(self):
        """
        build image using the bitnamy docker file
        """

        # get path to the bitnami github path
        bitnami_git_url = self.bitnamy_defaults.get('bitnami_git_url')
        bitnami_folder = self.bitnamy_defaults.get('bitnami_folder_name')
        bitnami_docker_file_path = self.bitnamy_defaults.get('bitnami_docker_file_path')

        # make sure bitnami_folder exists
        os.makedirs(bitnami_folder, exist_ok=True)
        # cd into this folder
        act_dir = os.getcwd()
        os.chdir(bitnami_folder)

        version = self.erp_version
        minor = self.erp_minor
        try:
            version = str(int(float(version)))
        except:
            print(bcolors.FAIL)
            print('*' * 80)
            print(DOCKER_IMAGE_CREATE_MISING_HUB_USER % self.site_name)
            print("%s is not a valid version. Please fix it in the sitedescription for site %s" % (version, self.site))
            print(bcolors.ENDC)
        if minor:
            version = ('%s.%s' % (version, minor)).replace('..', '.')

        print(bcolors.WARNING)
        print('*' * 80)
        print("Git clonig odoo source V%s to be included in the image to %s/src" %
              (version, os.getcwd()))
        print(bcolors.ENDC)
        cmd_lines = [
            'git init .',
            'git submodule init',
            'git submodule add %s' % bitnami_git_url
        ]
        self.run_commands(cmd_lines=cmd_lines)
        print(DOCKER_IMAGE_CREATE_PLEASE_WAIT)
        tag = self.erp_image_version
        return_info = []
        try:
            docker_target_path = os.path.normpath('%s/%s' % (bitnami_folder, bitnami_docker_file_path,))
            os.chdir(docker_target_path)
            docker_file = '%s/Dockerfile' % docker_target_path
            result = self.docker_client.build(
                docker_target_path, 
                tag = tag, 
                dockerfile=docker_file)
            is_ok = self._print_docker_result(result, docker_file, docker_target_path, return_info)
            if not is_ok:
                return
        except docker.errors.NotFound:
            print(DOCKER_IMAGE_CREATE_FAILED % (self.site_name, self.site_name))
        else:
            result = return_info[0].split(' ')[-1]
            # the last line is something like:
            # {"stream":"Successfully built 97cea8884220\n"}
            print(DOCKER_BITNAMI_IMAGE_CREATE_DONE % (self.site_name, result))

class KuberHandler(object):
    def __init__(self, opts, sites, parsername='', config_data = {}):
        if     HasPyhelm:
            super.__init__(opts, sites, parsername)
            self._host = config_data.get('host', 'localhost')
            self._port = config_data.get('port', '8069')
            self._resource_name = config_data.get('resource_name', '')
            self._chart = config_data.get('chart', {})
            self._values = config_data.get('values', {})
            self._namespace = config_data.get('namespace', 'default')
            
            self._tserver = tiller.Tiller(self.host, self.port)

    _host = 'localhost'
    @property
    def host(self):
        return self._host
    
    _port = '8069'
    @property
    def port(self):
        return self._port
    
    _resource_name = ''
    @property
    def resource_name(self):
        return self._resource_name
    
    _chart = {}
    @property
    def chart(self):
        return self._chart
    
    _values = {}
    @property
    def values(self):
        return self._values
    
    _namespace = ''
    @property
    def namespace(self):
        return self._namespace
    
    _tserver = None
    @property
    def tserver(self):
        return self._tserver

    def install(self, tserver = None):
        if not HasPyhelm:
            print(bcolors.FAIL)
            print('*' * 80)
            print('pyhelm is not installed')
            print(bcolors.ENDC)
            return
        if not tserver:
            tserver = self.tserver
        changed = False
        name = self.resource_name
        values = self.values
        chart = self.chart
        namespace = self.namespace

        if chart:
            url, cart_name = chart
            chart_path = chart_versions = from_repo(url, cart_name)
            chart_obj = chartbuilder.ChartBuilder({'name': 'mongodb', 'source': {'type': 'directory', 'location': chart_path}})
            #chartb = chartbuilder.ChartBuilder(chart_path)
            r_matches = (x for x in tserver.list_releases()
                        if x.name == name and x.namespace == namespace)
            installed_release = next(r_matches, None)
            if installed_release:
                if installed_release.chart.metadata.version != chart['version']:
                    tserver.update_release(chartb.get_helm_chart(), False,
                                        namespace, name=name, values=values)
                    changed = True
            else:
                tserver.install_release(chartb.get_helm_chart(), namespace,
                                        dry_run=False, name=name,
                                        values=values)
                changed = True

        return changed


    def delete(self, tserver, purge=False):
        changed = False
        params = module.params

        if not module.params['name']:
            module.fail_json(msg='Missing required field name')

        name = module.params['name']
        disable_hooks = params['disable_hooks']

        try:
            tserver.uninstall_release(name, disable_hooks, purge)
            changed = True
        except grpc._channel._Rendezvous as exc:
            if 'not found' not in str(exc):
                raise exc

        return dict(changed=changed)



def main():
    # setup the namespace
    ns = os.getenv("K8S_NAMESPACE")
    if ns is None:
        ns = ""

    # use package pint to handle volume quantities
    unit = pint.UnitRegistry()
    unit.define('gibi = 2**30 = Gi')
    max_claims = unit.Quantity("150Gi")
    total_claims = unit.Quantity("0Gi")

    # configure client 
    config.load_kube_config()
    api = client.CoreV1Api()

    # Print PVC list
    pvcs = api.list_namespaced_persistent_volume_claim(namespace=ns, watch=False)
    print("")
    print("---- PVCs ---")
    print("%-16s\t%-40s\t%-6s" % ("Name", "Volume", "Size"))
    for pvc in pvcs.items:
        print("%-16s\t%-40s\t%-6s" %
              (pvc.metadata.name, pvc.spec.volume_name, pvc.spec.resources.requests['storage']))
    print("")


    # setup watch
    w = watch.Watch()
    for item in w.stream(api.list_namespaced_persistent_volume_claim, namespace=ns, timeout_seconds=0):
        pvc = item['object']
        

        # parse PVC events
        # new PVC added
        if item['type'] == 'ADDED':
            size = pvc.spec.resources.requests['storage']
            claimQty = unit.Quantity(size)
            total_claims = total_claims + claimQty

            print("PVC Added: %s; size %s" % (pvc.metadata.name, size))

            if total_claims >= max_claims:
                print("---------------------------------------------")
                print("WARNING: claim overage reached; max %s; at %s" % (max_claims, total_claims))
                print("**** Trigger over capacity action ***")
                print("---------------------------------------------")
        
        # PVC is removed
        if item['type'] == 'DELETED':
            size = pvc.spec.resources.requests['storage']
            claimQty = unit.Quantity(size)
            total_claims = total_claims - claimQty

            print("PVC Deleted: %s; size %s" % (pvc.metadata.name, size))

            if total_claims <= max_claims:
                print("---------------------------------------------")
                print("INFO: claim usage normal; max %s; at %s" % (max_claims, total_claims))
                print("---------------------------------------------")

        
        # PVC is UPDATED
        if item['type'] == "MODIFIED":
            print("MODIFIED: %s" % (pvc.metadata.name))

        print("INFO: total PVC at %4.1f%% capacity" % ((total_claims/max_claims)*100))

if __name__ == '__main__':
    main()

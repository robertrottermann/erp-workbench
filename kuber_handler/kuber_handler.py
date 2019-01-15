#!bin/python
# -*- encoding: utf-8 -*-
import os
import sys

"""
https://medium.com/programming-kubernetes/building-stuff-with-the-kubernetes-api-1-cc50a3642
"""
"""
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

"""

from scripts.bcolors import bcolors

try:
    import pint
    from kubernetes import client as ku_cli
    from kubernetes import config as ku_con
    from kubernetes import watch as ku_watch
except ImportError:
    print(xxx)

try:
    import grpc
    from pyhelm import tiller
    from pyhelm import chartbuilder
    HAS_PYHELM = True
except ImportError as exc:
    HAS_PYHELM = False
    raise

class KuberHandler(object):


    def __init__(self, params={}):
             self._host = params.get('host', 'localhost')
             self._port = params.get('port', 'localhost')
             self._release_name = params.get('name', 'localhost')
             self._chart = params.get('chart', {})
             self._state = params.get('state', '')
             self._values = params.get('values', {})
             self._namespace = params.get('namespace', 'default')
             self._disable_hooks = params.get('disable_hooks', False)
             self._tserver = tiller.Tiller(self.host, self.port)


    _chart = ''
    @property
    def chart(self):
        return self._chart
        
    _host = ''
    @property
    def host(self):
        return self._host

    _namespace = ''
    @property
    def namespace(self):
        return self._namespace

    _port = ''
    @property
    def port(self):
        return self._port

    _release_name = ''
    @property
    def release_name(self):
        return self._release_name

    _tserver = ''
    @property
    def tserver(self):
        return self._tserver

    _values = ''
    @property
    def values(self):
        return self._values

    def install(self, tserver=None):
        if not tserver:
            tserver = self.tserver
        changed = False
        name = self.release_name
        values = self.values
        chart = self.chart
        namespace = self.namespace

        chartb = chartbuilder.ChartBuilder(chart)
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

        return dict(changed=changed)


    def delete(self, module, tserver, purge=False):
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

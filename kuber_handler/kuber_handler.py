#!bin/python
# -*- encoding: utf-8 -*-
import os
import sys
<<<<<<< HEAD
from scripts.bcolors import bcolors
=======
>>>>>>> 54c4fda70a96891812fb1e5901770e8ca50872cc

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
except ImportError as e:
    print(bcolors.FAIL)
    print('*' * 80)
    print('some library could not be installed')
    print('please run: pip install -r install/requirements.txt')
    print(str(e))
    sys.exit()

try:
    import pyhelm
except ImportError as e:
    print(bcolors.FAIL)
    print('*' * 80)
    print('pyhelm could not be installed')
    print('please download and install it from:')
    print('https://github.com/redcor/pyhelm.git')
    print(str(e))
    sys.exit()


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

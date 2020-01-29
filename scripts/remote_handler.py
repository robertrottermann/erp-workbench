#!bin/python
# -*- encoding: utf-8 -*-
import warnings
import sys
import os
import logging
from optparse import OptionParser
import subprocess
from subprocess import PIPE
from config import (
    FOLDERNAMES,
    SITES,
    SITES_LOCAL,
    BASE_PATH,
    BASE_INFO,
    ACT_USER,
    MARKER,
)
from scripts.bcolors import bcolors
from copy import deepcopy

from scripts.create_handler import InitHandler
from scripts.utilities import collect_options

HA = """
    %s
    """
HL = "    ServerAlias %s\n"


class RemoteHandler(InitHandler):
    def __init__(self, opts, sites=SITES):
        super(RemoteHandler, self).__init__(opts, sites)

        # ----------------------------------
        # add_site_to_apache
        # create virtual host entry for apache
        # if user is allowed to write to the apache directory, add it to
        #   sites_available and sites_enabled
        # if not, just print it out
        # @opts             : option instance
        # @default_values   : dictionary with default values
        # ----------------------------------

    _subparser_name = "remote"

    @property
    def subparser_name(self):
        return self._subparser_name

    def add_site_to_apache(self):
        """
        create virtual host entry for apache
        if user is allowed to wite to the apache directory, add it to
          sites_available and sites_enabled
        if not, just print it out
        @opts             : option instance
        @default_values   : dictionary with default values
        """
        # is the path to the apache executable set?
        apache_path = self.http_server_fs_path
        if not apache_path:
            print(bcolors.FAIL)
            print('*' * 80)
            print('no path to the apache configuration defined')
            print('please do so in the server description of this host')
            print('like: http_server_fs_path: /etc/apache2')
            print('the ip is: %s' % self.remote_server_ip)
            print(bcolors.ENDC)
            return

        opts = self.opts
        default_values = self.default_values
        default_values["marker"] = MARKER
        site_name = self.site_name
        if site_name not in SITES:
            print("%s is not known in sites.py" % site_name)
            return
        df = deepcopy(default_values)
        site_info = self.flatten_site_dic(site_name)
        df["vservername"] = site_info.get("vservername", "    www.%s.ch" % site_name)
        aliases_string = ""
        for alias in site_info.get("vserveraliases", []):
            aliases_string += HL % alias
        df["serveralias"] = aliases_string.rstrip()
        df['odoo_port'] = df['erp_port']
        df.update(site_info)
        template = (
            open("%s/templates/apache.conf" % default_values["sites_home"], "r").read()
            % df
        )
        # template = template % d

        print(template)
        apa = "%s/sites-available/%s.conf" % (self.http_server_fs_path, site_name)
        ape = "%s/sites-enabled/%s.conf" % (self.http_server_fs_path, site_name)
        try:
            open(apa, "w").write(template)
            if os.path.exists(ape):
                try:
                    os.unlink(ape)
                except:
                    pass  # exists ??
            try:
                os.symlink(apa, ape)
            except:
                pass
            print("%s added to apache" % site_name)
            print("restart apache to activate")
        except:
            print("could not write %s" % apa)

    # ----------------------------------
    # add_site_to_nginx
    # create virtual host entry for nginx
    # if user is allowed to write to the nginx directory, add it to
    #   sites_available and sites_enabled
    # if not, just print it out
    # @opts             : option instance
    # @default_values   : dictionary with default values
    # ----------------------------------
    def add_site_to_nginx(self):
        """
        create virtual host entry for nginx
        if user is allowed to wite to the nginx directory, add it to
          sites_available and sites_enabled
        if not, just print it out
        @opts             : option instance
        @default_values   : dictionary with default values
        """
        opts = self.opts
        default_values = self.default_values
        default_values["marker"] = MARKER
        site_name = self.site_name

        if site_name not in SITES:
            print("%s is not known in sites.py" % site_name)
            return

        values = {
            "docker_rpc_port": self.docker_rpc_port,
            "docker_long_polling_port": self.docker_long_polling_port,
            "site_name": self.site_name,
            "remote_http_url": self.remote_http_url,
        }

        template_80 = (
            open(
                "%s/templates/nginx.conf.80" % default_values["sites_home"], "r"
            ).read()
            % values
        )
        apa_80 = "%s/sites-available/%s-80" % (self.http_server_fs_path, site_name)
        ape_80 = "%s/sites-enabled/%s-80" % (self.http_server_fs_path, site_name)
        try:
            with open(apa_80, "w") as f:
                f.write(template_80)
            if os.path.exists(ape_80):
                try:
                    os.unlink(ape_80)
                except:
                    pass  # exists ??
            try:
                os.symlink(apa_80, ape_80)
            except:
                pass
            print("%s added to nginx" % site_name)
            print("restart nginx to activate")
        except:
            print("could not write %s" % ape_80)

    # ----------------------------------
    # flatten_site_dic
    # check whether a site dic has all substructures
    # flatten them into a dictonary without substructures
    # @ site_name       : dictonary to flatten
    # ----------------------------------
    def flatten_site_dic(self, site_name, sites=SITES):
        """
        check whether a site dic has all substructures
        flatten them into a dictonary without substructures
        @ site_name       : dictonary to flatten
        """
        res = {}
        site_dic = sites.get(site_name)
        if not site_dic:
            print("error: %s not found in provided list of sites" % site_name)
            return
        sd = site_dic.copy()
        parts = ["docker", "remote_server", "apache"]
        vparts = ["slave_info"]
        both = parts + vparts
        for k, v in list(sd.items()):
            if not k in both:
                res[k] = v
        for p in parts:
            pDic = sd.get(p)
            if not pDic:
                print("error: %s not found site description for %s" % (p, site_name))
                return
            for k, v in list(pDic.items()):
                res[k] = v
        for p in vparts:
            pDic = sd.get(p, {})
            for k, v in list(pDic.items()):
                res[k] = v
        return res

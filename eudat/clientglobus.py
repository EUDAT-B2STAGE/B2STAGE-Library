#!/usr/bin/env python

"""
Client to manage Globus activities (endpoint activation, transfer..)
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

import os
import sys
import time
from datetime import datetime, timedelta

from abstractclient import AbstractClient
from globusonline.transfer.api_client import TransferAPIClient
from globusonline.transfer.api_client import x509_proxy
from globusonline.transfer.api_client import Transfer
from globusonline.transfer.api_client import create_client_from_args


class ClientGlobus(AbstractClient):
    def __init__(self, auth, http_session=None):
        self.auth = auth
        self.http_session = http_session
        self.myproxy_username = ''
        self.api = None
        if len(self.auth) > 0:
            self.proxy_name = 'credential-' + self.auth[0] + '.pem'


    def login(self):
        """ Globus login with username and certificates"""
        if len(self.auth) > 2 and self.auth[0] and self.auth[2] \
                and self.auth[3]:
            try:
                self.api = TransferAPIClient(username=self.auth[0],
                                             cert_file=self.auth[2],
                                             key_file=self.auth[3])
                self.api.set_debug_print(False, False)
                print "Successfully logged in with Globus!"
            except Exception as e:
                raise Exception("GSI authentication failed: {0}".format(e))

    def endpoint_activation(self, endpoint_name, myproxy_username):
        """ Method to activate endpoints (maybe could be an internal method)"""
        #_, _, data = self.api.endpoint(endpoint_name)
        #if data["activated"]:
        #    print "Endpoint {0} already activated!".format(endpoint_name)
        #    return

        self.check_proxy()
        user_credential_path = os.path.join(os.getcwd(), self.proxy_name)
        print "==Activating endpoint: {0}==".format(endpoint_name)

        # Trying with autoactivation
        print "==Trying autoactivation=="
        code, message, data = self.api.endpoint_autoactivate(
            endpoint_name)

        if not data["code"].startswith("AutoActivationFailed"):
            print "Endpoint {0} activated!".format(endpoint_name)
            print "result: {0} ({1})".format(data["code"], data["message"])
            return

        # Trying with myproxy
        print "==Trying activating myproxy for {0}==".format(myproxy_username)

        data.set_requirement_value("myproxy", "username",
                                   myproxy_username)
        from getpass import getpass
        passphrase = getpass()
        data.set_requirement_value("myproxy", "passphrase", passphrase)
        try:
            status, message, data = self.api.endpoint_activate(endpoint_name, data)
            if not data["code"].startswith("AutoActivationFailed"):
                print "Endpoint {0} activated!".format(endpoint_name)
                print "result: {0} ({1})".format(data["code"], data["message"])
                return
        except Exception as e:
            print "Error: {0}".format(e)


        # Trying activating local proxy
        print "==Trying local proxy activation=="
        _, _, reqs = self.api.endpoint_activation_requirements(
            endpoint_name, type="delegate_proxy")
        public_key = reqs.get_requirement_value("delegate_proxy", "public_key")
        #print public_key

        proxy = x509_proxy.create_proxy_from_file(user_credential_path,
                                                  public_key, lifetime_hours=3)

        #proxy = x509_proxy.create_proxy_from_file(user_credential_path,
        #                                          public_key)
        #print proxy
        reqs.set_requirement_value("delegate_proxy", "proxy_chain", proxy)
        try:
            code, message, data = self.api.endpoint_activate(endpoint_name,
                                                             reqs)
            if not data["code"].startswith("AutoActivationFailed"):
                print "Endpoint {0} activated!".format(endpoint_name)
                print "result: {0} ({1})".format(data["code"], data["message"])
                return
        except Exception as e:
            print "Error: {0}".format(e)
            print "Can not active the endpoint {0}".format(endpoint_name)


    def put(self, src_endpoint, dst_endpoint, item, dst_dir):
        """ Transfer a file from one endpoint to another. Return the Globus
        task_id. Should maybe be called transfer instead of put"""
        # Can work without myproxy?!?! Probabilly better to set
        #  myproxy_username as a class variable
        print "Please enter your myproxy username (\'none\' if you do not" \
              " have one)."
        myproxy_username = sys.stdin.readline().rstrip()
        if src_endpoint:
            self.endpoint_activation(src_endpoint, myproxy_username)
        if dst_endpoint:
            self.endpoint_activation(dst_endpoint, myproxy_username)

        # submit a transfer
        #oldstdout=sys.stdout
        #sys.stdout = open(os.devnull,'w')
        code, message, data = self.api.transfer_submission_id()
        #sys.stdout = oldstdout # enable output

        submission_id = data["value"]
        #deadline = datetime.utcnow() + timedelta(minutes=10)
        t = Transfer(submission_id, src_endpoint, dst_endpoint)#, deadline)
        print "==Transferring {0} from endpoint {1} to endpoint {2}==".format(
            item, src_endpoint, dst_endpoint)
        t.add_item(item, os.path.join(dst_dir, os.path.basename(item)))
        code, reason, data = self.api.transfer(t)
        task_id = data["task_id"]
        self.display_task(task_id)
        return task_id

    def display_tasksummary(self):
        code, reason, data = self.api.tasksummary()
        print "Task Summary for %s:" % self.api.username
        for k, v in data.iteritems():
            if k == "DATA_TYPE":
                continue
            print "%3d %s" % (int(v), k.upper().ljust(9))

    def _print_task(self, data, indent_level=0):
        indent = " " * indent_level
        indent += " " * 2
        for k, v in data.iteritems():
            if k in ("DATA_TYPE", "LINKS"):
                continue
            print indent + "%s: %s" % (k, v)

    def display_task(self, task_id, show_successful_transfers=True):
        code, reason, data = self.api.task(task_id)
        print "Task %s:" % task_id
        self._print_task(data, 0)

        if show_successful_transfers:
            try:
                code, reason, data = self.api.task_successful_transfers(
                    task_id)
                transfer_list = data["DATA"]
                print "Successful Transfers (src -> dst)"
                for t in transfer_list:
                    print " %s -> %s" % (t[u'source_path'],
                                         t[u'destination_path'])
            except Exception as e:
                "Error verifying successful transfer: {0}".format(e)

    def check_proxy(self):
        """  Check for a local x509 proxy"""

        grid_proxy_init_options = ' -out ' + self.proxy_name
        #if arguments.cert:
        #    grid_proxy_init_options=grid_proxy_init_options+' -cert '+arguments.cert
        #if arguments.key:
        #    grid_proxy_init_options=grid_proxy_init_options+' -key '+arguments.key
        #if arguments.certdir:
        #    grid_proxy_init_options=grid_proxy_init_options+' -certdir '+arguments.certdir
        #print "grid_proxy_init_options: "+grid_proxy_init_options
        print
        print "==Checking for a valid proxy=="
        if os.path.exists(self.proxy_name):
            print self.proxy_name + ' exists..'
            try:
                ret_val = os.system('grid-proxy-info -exists -f ' + self.proxy_name)
                if ret_val == 0:
                    print "Proxy found!"
                else:
                    print "Proxy expired. I will try to create a new one.."
                    os.system('grid-proxy-init' + grid_proxy_init_options)
            except:
                print "Proxy invalid. New one, please!"
                os.system('grid-proxy-init' + grid_proxy_init_options)
        else:
            print self.proxy_name + " does not exist. I will try to create it.."
            os.system('grid-proxy-init' + grid_proxy_init_options)
        print

    def get(self):
        pass

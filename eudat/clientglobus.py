#!/usr/bin/env python

"""
Client to manage Globus activities (endpoint activation, transfer..)
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

import os
import sys
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
        user_credential_path = self.auth[3]
        print "==Activating endpoint: {0}==".format(endpoint_name)

        # Trying with autoactivation
        print "==Trying autoactivation=="
        code, message, data = self.api.endpoint_autoactivate(
            endpoint_name)

        if data["code"].startswith("AutoActivated.CachedCredential"):
            # maybe better to check if doesn't start with AutoActivationFailed
            print "Endpoint {0} activated!".format(endpoint_name)
            print "result: {0} ({1})".format(data["code"], data["message"])
            return

        # Trying with myproxy
        print "==Trying myproxy for {0}==".format(myproxy_username)

        data.set_requirement_value("myproxy", "username",
                                   myproxy_username)
        from getpass import getpass
        passphrase = getpass()
        data.set_requirement_value("myproxy", "passphrase", passphrase)
        status, message, data = self.api.endpoint_activate(endpoint_name, data)
        if data["code"].startswith("AutoActivated.CachedCredential"):
            # maybe better to check if doesn't start with AutoActivationFailed
            print "Endpoint {0} activated!".format(endpoint_name)
            print "result: {0} ({1})".format(data["code"], data["message"])
            return

        # Trying activating local proxy
        print "==Local proxy activation=="
        _, _, reqs = self.api.endpoint_activation_requirements(
            endpoint_name, type="delegate_proxy")
        public_key = reqs.get_requirement_value("delegate_proxy",
                                                "public_key")
        proxy = x509_proxy.create_proxy_from_file(user_credential_path,
                                                  public_key)
        reqs.set_requirement_value("delegate_proxy", "proxy_chain",
                                   proxy)
        code, message, data = self.api.endpoint_activate(endpoint_name, reqs)
        if data["code"].startswith("AutoActivated.CachedCredential"):
            # maybe better to check if doesn't start with AutoActivationFailed
            print "Endpoint {0} activated!".format(endpoint_name)
            print "result: {0} ({1})".format(data["code"], data["message"])
            return

    def put(self, item,  src_endpoint, dst_endpoint, dst_dir):
        """ To transfer a file from one endpoint to another. Return the Globus
        task_id"""
        # Can work without myproxy?!?! Probabilly better to set
        #  myproxy_username as a class variable
        print "Please enter your myproxy username (\'none\' if you do not" \
              " have one)."
        myproxy_username = sys.stdin.readline().rstrip()
        self.endpoint_activation(src_endpoint, myproxy_username)
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
                code, reason, data = self.api.task_successful_transfers(task_id)
                transfer_list = data["DATA"]
                print "Successful Transfers (src -> dst)"
                for t in transfer_list:
                    print " %s -> %s" % (t[u'source_path'],
                                         t[u'destination_path'])
            except Exception as e:
                "Error verifying successful transfer: {0}".format(e)




    def get(self):
        pass

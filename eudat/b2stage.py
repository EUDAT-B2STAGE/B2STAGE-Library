#!/usr/bin/env python

"""
Python API for B2STAGE.
Client to manage Globus activities (endpoint activation, data transfer..)
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

import os
import sys
import ConfigParser
from urlparse import urlparse
import time
from datetime import datetime, timedelta

from baseclient import BaseClient
from globusonline.transfer.api_client import TransferAPIClient
from globusonline.transfer.api_client import x509_proxy
from globusonline.transfer.api_client import Transfer
from globusonline.transfer.api_client import create_client_from_args


class ClientGlobus():
    def __init__(self, auth, http_session=None):
        """
        Initialize the Globus session: login with username and certificates

        :param auth: a list containing username[0], certfile[1] and keyfile[2]
        :param http_session:
        """
        self.auth = auth
        if len(self.auth) < 4: #or !self.auth[0] or !self.auth[2] or !self.auth[3]:
             print "Can not init session: some parameters are missing.."
        self.auth = auth
        self.http_session = http_session
        self.myproxy_username = ''
        self.api = None
        if len(self.auth) > 0:
            self.proxy_name = 'credential-' + self.auth[0] + '.pem'

        try:
            self.api = TransferAPIClient(username=self.auth[0],
                                         cert_file=self.auth[2],
                                         key_file=self.auth[3])
            self.api.set_debug_print(False, False)
            print "Successfully logged in with Globus online!"
        except Exception as e:
            raise Exception("GSI authentication failed: {0}".format(e))

    def display_endpoint_list(self):
        code, reason, endpoint_list = self.api.endpoint_list(limit=100)
        print "Found %d endpoints for user %s:" \
            % (endpoint_list["length"], self.api.username)
        for ep in endpoint_list["DATA"]:
            self._print_endpoint(ep)

    def _print_endpoint(self, ep):
        name = ep["canonical_name"]
        print name
        if ep["activated"]:
            print "  activated (expires: %s)" % ep["expire_time"]
        else:
            print "  not activated"
        if ep["public"]:
            print "  public"
        else:
            print "  not public"
        if ep["myproxy_server"]:
            print "  default myproxy server: %s" % ep["myproxy_server"]
        else:
            print "  no default myproxy server"
        servers = ep.get("DATA", ())
        print "  servers:"
        for s in servers:
            uri = s["uri"]
            if not uri:
                uri = "GC endpoint, no uri available"
            print "    " + uri,
            if s["subject"]:
                print " (%s)" % s["subject"]
            else:
                print

    def endpoint_activation(self, endpoint_name, myproxy_username=''):
        """
        Activate a GridFTP endpoint

        :param endpoint_name: name of the endpoint to activate
        :param myproxy_username: myproxy user name
        """

        #code, reason, data = self.api.endpoint(endpoint_name)
        #self._print_endpoint(data)
        #self.display_endpoint_list();
        print
        print "Checking if endpoint {0} is already activated\n".format(
             endpoint_name)
        _, _, data = self.api.endpoint(endpoint_name)
        if data["activated"]:
            print "Endpoint {0} is already active!\n".format(endpoint_name)
            return True

        # Trying with autoactivation
        print "Trying autoactivation\n"
        code, message, data = self.api.endpoint_autoactivate(
            endpoint_name)

        if not data["code"].startswith("AutoActivationFailed"):
            print "Endpoint {0} activated!\n".format(endpoint_name)
            print "result: {0} ({1})\n".format(data["code"], data["message"])
            return True

        print "Trying activating with myproxy\n"

        data.set_requirement_value("myproxy", "username", myproxy_username)

        # Remove interactive messages: add arguments to manage this part
        from getpass import getpass
        passphrase = getpass()
        data.set_requirement_value("myproxy", "passphrase", passphrase)
        try:
            status, message, data = self.api.endpoint_activate(endpoint_name,
                                                               data,
                                                               if_expires_in=600)
            if not data["code"].startswith("AutoActivationFailed"):
                print "Endpoint {0} activated!\n".format(endpoint_name)
                print "result: {0} ({1})\n".format(data["code"], data["message"])
                return True
        except Exception as e:
            print "Error: {0}".format(e)

        # Trying activating a delegate proxy
        self.check_proxy()
        user_credential_path = os.path.join(os.getcwd(), self.proxy_name)
        print
        print "Trying delegate proxy activation\n"
        _, _, reqs = self.api.endpoint_activation_requirements(
            endpoint_name, type="delegate_proxy")
        public_key = reqs.get_requirement_value("delegate_proxy", "public_key")
        #print public_key

        proxy = x509_proxy.create_proxy_from_file(user_credential_path,
                                                  public_key, lifetime_hours=3)

        #print proxy
        reqs.set_requirement_value("delegate_proxy", "proxy_chain", proxy)
        try:
            code, message, data = self.api.endpoint_activate(endpoint_name,
                                                             reqs)

            if not data["code"].startswith("AutoActivationFailed"):
                print "Endpoint {0} activated!\n".format(endpoint_name)
                print "result: {0} ({1})\n".format(data["code"], data["message"])
                return True
        except Exception as e:
            print "Error: {0}".format(e)
            print "Can not active the endpoint {0}\n".format(endpoint_name)
            if "proxy is not valid until" in str(e):
                print "This error may be related to clock time skew. " \
                      "Please, check if your client clock is server " \
                      "synchronized and not ahead (you could check with " \
                      "\"www.time.is\")"
            return False

    def transfer(self, src_endpoint, dst_endpoint, item, dst_dir):
        """
        Transfer a file from one endpoint to another. Return the Globus
        task_id.

        :param src_endpoint: source endpoint name (i.e. user#endpoint)
        :param dst_endpoint: destination endpoint name (i.e. user#endpoint)
        :param item: object to be transferred
        :param dst_dir: destination directory
        :return: Globus task_id
        """

        if src_endpoint:
            self.endpoint_activation(src_endpoint)
        if dst_endpoint:
            self.endpoint_activation(dst_endpoint)

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
        """  Check for a local x509 prox. If not found or expired it creates
        a new one."""

        grid_proxy_init_options = ' -out ' + self.proxy_name
        print
        print "==Checking for a valid proxy=="
        if os.path.exists(self.proxy_name):
            print self.proxy_name + ' exists..'
            try:
                ret_val = os.system('grid-proxy-info -exists -f ' + self.proxy_name)
                if ret_val == 0:
                    print "Proxy found!"
                else:
                    # Remove interactive message: add arguments to manage the
                    # request for GRID pass phrase
                    print "Proxy expired. I will try to create a new one.."
                    os.system('grid-proxy-init' + grid_proxy_init_options)
            except:
                print "Proxy invalid. New one, please!"
                os.system('grid-proxy-init' + grid_proxy_init_options)
        else:
            print self.proxy_name + " does not exist. I'll try to create it.."
            os.system('grid-proxy-init' + grid_proxy_init_options)
        print

    #def get(self):
    #    pass

    def get_endpoint_from_url(self, url):
        """
        Read the endpoints.cfg configuration file to discover which endpoint
        is associated to the url.
        At the moment it is not possible to discover which is the Globus
        endpoint that can be used to access a resource. Resolving the PID
        it is possible to get the physical URL of the resource (iRODS URL),
        but the information about the endpoint is missing. For now a
        configuration file can be used to set the association between
        iRODS URL and Globus endpoint.

        :param url: physical URL of the resource
        :return: Globus endpoint name
        """
        # get minimal url
        o = urlparse(url)
        simple_url = o.netloc.rsplit(':')[0]

        config = ConfigParser.SafeConfigParser()
        config.read(os.path.join(os.getcwd(), "endpoints.cfg"))
        res = ''

        try:
            res = config.get('irods_endpoints', simple_url)
            print "Found endpoint {0} associated to URL {1}".format(res,
                                                                     simple_url)
        except ConfigParser.NoOptionError:
            print "Endpoint not found for URL {0}. You can add more endpoints " \
                  "editing the config file 'endpoints.cfg'.".format(
                simple_url)

        return res


def main():
    """ Main function to test the script """
    auth = ['rmucci00', '', '/home/rmucci00/.globus/usercert.pem',
            '/home/rmucci00/.globus/userkey.pem']
    globus = ClientGlobus(auth);
    globus.display_endpoint_list()
    globus.endpoint_activation('cineca#GALILEO', 'rmucci00')


if __name__ == '__main__':
    main()

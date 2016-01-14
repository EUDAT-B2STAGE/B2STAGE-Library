#!/usr/bin/env python

"""
Python API for B2STAGE.
Client to manage Globus activities (endpoint activation, data transfer..)
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

import os
import ConfigParser
from urlparse import urlparse
import json
import time
from globusonline.transfer.api_client import TransferAPIClient
from globusonline.transfer.api_client import x509_proxy
from globusonline.transfer.api_client.goauth import get_access_token
from globusonline.transfer.api_client import Transfer
import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(NullHandler())



class ClientGlobus():
    def __init__(self, auth=['', ''], resource_file_path='', debug=False):
        """
        Initialize the Globus session: login with Globus username and password
        Credentials can also be passed through a resource json file like this:

        {
            "globus_username":"",
            "globus_password":"",
            "myproxy_username": "",
            "myproxy_password": "",
            "PEM_passphrase": ""
        }

        :param auth: a list containing username[0], password[1], certfile[2]
        and keyfile[3]
        :param resource_file_path: path to a json file containing the credentials
        :param debug: set True to enable debug messages
        """

        if debug:
            LOGGER.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            LOGGER.addHandler(ch)


        # Read resources from file:
        self.globus_init = None
        if resource_file_path and os.path.isfile(resource_file_path):
            self.globus_init = json.load(open(resource_file_path))
            if not auth[0]:
                auth[0] = self.globus_init['globus_username']
            if not auth[1]:
                auth[1] = self.globus_init['globus_password']

        if not auth[0] or not auth[1]:
            print "Can not init session without a username and password.."
            return

        self.api = None
        self.proxy_name = 'credential-' + auth[0] + '.pem'
        try:
            result = get_access_token(username=auth[0], password=auth[1])
            goauth = result.token
            self.api = TransferAPIClient(username=auth[0],
                                         goauth=goauth)
            self.api.set_debug_print(False, False)
            LOGGER.info("Successfully logged in with Globus Online!")
        except Exception as e:
            print "Globus Online authentication failed: {0}".format(e)

    def display_endpoint_list(self):
        code, reason, endpoint_list = self.api.endpoint_list(limit=100)
        LOGGER.info("Found %d endpoints for user %s:" \
                    % (endpoint_list["length"], self.api.username))
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

    def endpoint_activation(self, endpoint_name, myproxy_username='',
                            myproxy_password=''):
        """
        Activate a GridFTP endpoint.
        Different attempts will be made: autocativation, using myproxy and using
        a delegate proxy (in the latter case \'grid-proxy-init\' is needed to
        generate a X.509 proxy).
        Myproxy username and password will be used to try the authentication
        with myproxy: they will be prompted if not passed as parameter or not
        found in the resource json file.
        The passphrase of the user certificate (needed for generating an X.509
        proxy certificate) will be prompted if not found in the resource json
        file.


        :param endpoint_name: name of the endpoint to activate
        :param myproxy_username: myproxy user name (optional, if empty end needed
        it will be prompted)
        :param myproxy_password: myproxy user password (optional, if empty end
        needed it will be prompted)
        """

        if self.api is None:
            print "You need to be authenticated with Globus Online to perform " \
                  "this operation. "
            return False

        LOGGER.debug("Checking if endpoint {0} is already activated..".format(
            endpoint_name))
        _, _, data = self.api.endpoint(endpoint_name)
        if data["activated"]:
            LOGGER.info(
                "Endpoint {0} is already active!".format(endpoint_name))
            return True

        # Trying with autoactivation
        LOGGER.debug("Trying autoactivation..")
        code, message, data = self.api.endpoint_autoactivate(
            endpoint_name)

        if not data["code"].startswith("AutoActivationFailed"):
            LOGGER.info("Endpoint {0} activated!".format(endpoint_name))
            LOGGER.debug("result: {0} ({1})".format(data["code"],
                                                    data["message"]))
            return True

        LOGGER.debug("Trying activating with myproxy..")
        if not myproxy_username and self.globus_init:
            myproxy_username = self.globus_init['myproxy_username']
            if not myproxy_username and self.globus_init:
                myproxy_username = raw_input(
                    "Please insert your \'myproxy\' username:")

        if not myproxy_password and self.globus_init:
            myproxy_password = self.globus_init['myproxy_password']
            if not myproxy_password:
                from getpass import getpass
                myproxy_password = getpass(
                    'Please insert your \'myproxy\' password:')

        data.set_requirement_value("myproxy", "username", myproxy_username)
        data.set_requirement_value("myproxy", "passphrase", myproxy_password)
        try:
            status, message, data = self.api.endpoint_activate(endpoint_name,
                                                               data,
                                                               if_expires_in=600)
            if not data["code"].startswith("AutoActivationFailed"):
                LOGGER.info("Endpoint {0} activated!\n".format(endpoint_name))
                LOGGER.debug("result: {0} ({1})\n".format(data["code"],
                                                          data["message"]))
                return True
        except Exception as e:
            print "Error: {0}".format(e)

        # Trying activating a delegate proxy
        # Verify if there is a workaround not to use grid-proxy-init
        # (https://github.com/globusonline/transfer-api-client-python/tree/master/mkproxy)
        self.check_proxy()
        user_credential_path = os.path.join(os.getcwd(), self.proxy_name)


        LOGGER.debug("Trying delegate proxy activation..")
        _, _, reqs = self.api.endpoint_activation_requirements(
            endpoint_name, type="delegate_proxy")
        public_key = reqs.get_requirement_value("delegate_proxy", "public_key")
        # print public_key

        proxy = x509_proxy.create_proxy_from_file(user_credential_path,
                                                  public_key, lifetime_hours=3)

        # print proxy
        reqs.set_requirement_value("delegate_proxy", "proxy_chain", proxy)
        try:
            code, message, data = self.api.endpoint_activate(endpoint_name,
                                                             reqs)

            if not data["code"].startswith("AutoActivationFailed"):
                LOGGER.info("Endpoint {0} activated!\n".format(endpoint_name))
                LOGGER.debug("result: {0} ({1})\n".format(data["code"],
                                                          data["message"]))
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

    def transfer(self, src_endpoint, dst_endpoint, src_item, dst_dir, recursive=False):
        """
        Transfer a file from one endpoint to another and return the Globus
        task_id.
        Set @recursive to True to transfer a folder.

        :param src_endpoint: source endpoint name (i.e. user#endpoint)
        :param dst_endpoint: destination endpoint name (i.e. user#endpoint)
        :param src_item: object to be transferred
        :param dst_dir: destination directory
        :param recursive: flag to enable folder transfer
        :return: Globus task_id
        """

        if src_endpoint:
            self.endpoint_activation(src_endpoint)
        if dst_endpoint:
            self.endpoint_activation(dst_endpoint)

        # submit a transfer
        code, message, data = self.api.transfer_submission_id()

        submission_id = data["value"]
        t = Transfer(submission_id, src_endpoint, dst_endpoint)  # , deadline)
        LOGGER.info(
            "Transferring {0} from endpoint {1} to endpoint {2}".format(
                src_item, src_endpoint, dst_endpoint))

        t.add_item(src_item, os.path.join(dst_dir, os.path.basename(src_item)),
                   recursive=recursive)
        code, reason, data = self.api.transfer(t)
        task_id = data["task_id"]
        return task_id

    def wait_for_task(self, task_id, timeout=120, poll_interval=30):
        """
        Wait for a task to be completed within @timeout seconds, polling every
        @poll_interval seconds. If the task completed in the timeout,
        return the status ("SUCCEEDED" or "FAILED"). If it did not complete,
        returns None. Caller is responsible for cancelling incomplete task
        as appropriate.
        Set @timeout to 0 to exclude timeout (warning: globus online will try
        many times to perform the transfer before set it to FAILED)

        :param task_id: id of the started task
        :param timeout: maximum waiting time (0 to disable timeout)
        :param poll_interval: interval between status checks
        :return status: SUCCEEDED, FAILED or None
        """

        # If timeout is 0, exits only with SUCCEEDED or FAILED status
        no_timeout = False
        if timeout == 0:
            LOGGER.warning('Timeout disabled!')
            no_timeout = True
        else:
            assert timeout % poll_interval == 0, \
                "Timeout must be multiple of poll_interval"
        timeout_left = timeout
        while no_timeout or timeout_left >= 0:
            code, reason, data = self.api.task(task_id, fields="status")
            status = data["status"]
            LOGGER.debug("Checking task {0} status: {1}".format(task_id,
                                                                status))
            if status in ("SUCCEEDED", "FAILED"):
                return status
            if timeout_left > 0 or no_timeout:
                time.sleep(poll_interval)
            timeout_left -= poll_interval

        return None

    def display_task_summary(self):
        code, reason, data = self.api.tasksummary()
        LOGGER.info("Task Summary for %s:" % self.api.username)
        for k, v in data.iteritems():
            if k == "DATA_TYPE":
                continue
            LOGGER.info("%3d %s" % (int(v), k.upper().ljust(9)))

    def _print_task(self, data, indent_level=0):
        indent = " " * indent_level
        indent += " " * 2
        for k, v in data.iteritems():
            if k in ("DATA_TYPE", "LINKS"):
                continue
            print indent + "%s: %s" % (k, v)

    def display_task(self, task_id, show_successful_transfers=True):
        """
        Prints the status of a transfer.

        :param task_id: id of the transfer
        :param show_successful_transfers:
        """

        code, reason, data = self.api.task(task_id)
        print 'Task {0}'.format(task_id)
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

    def display_successful_transfer(self, task_id):
        """
        Print successful transfers given the task id

        :param task_id:
        """
        try:
            code, reason, data = self.api.task_successful_transfers(
                    task_id)
            transfer_list = data["DATA"]
            print "Successful Transfers (src -> dst)"
            for t in transfer_list:
                print " %s -> %s" % (t[u'source_path'], t[u'destination_path'])
        except Exception as e:
            "Error verifying successful transfer: {0}".format(e)

    def check_proxy(self):
        """  Check for a local x509 prox. If not found or expired it creates
        a new one."""

        grid_proxy_init_options = ' -out ' + self.proxy_name
        passphrase = ''

        if self.globus_init:
            passphrase = self.globus_init['PEM_passphrase']

        LOGGER.debug("Checking for a valid proxy")
        if os.path.exists(self.proxy_name):
            LOGGER.debug(self.proxy_name + ' exists..')
            try:
                ret_val = os.system(
                    'grid-proxy-info -exists -f ' + self.proxy_name)
                if ret_val == 0:
                    LOGGER.info("Proxy found!")
                else:
                    # Remove interactive message: add arguments to manage the
                    # request for GRID pass phrase
                    LOGGER.debug(
                        "Proxy expired. I will try to create a new one..")
                    os.system('grid-proxy-init' + grid_proxy_init_options)
            except:
                print "Proxy invalid. New one, please!"
                if passphrase:
                    os.system('echo ' + passphrase + ' | ' + 'grid-proxy-init'
                              + ' -pwstdin' + grid_proxy_init_options)
                else:
                    os.system('grid-proxy-init' + grid_proxy_init_options)
        else:
            LOGGER.debug(
                self.proxy_name + " does not exist. I'll try to create it..")
            if passphrase:
                os.system('echo \'' + passphrase + '\' | ' + 'grid-proxy-init'
                              + ' -pwstdin' +grid_proxy_init_options)
            else:
                os.system('grid-proxy-init' + grid_proxy_init_options)

    # def get(self):
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
            LOGGER.info("Found endpoint {0} associated to URL {1}".format(res,
                                                                          simple_url))
        except ConfigParser.NoOptionError:
            print "Endpoint not found for URL {0}. You can add more endpoints " \
                  "editing the config file 'endpoints.cfg'.".format(
                simple_url)

        return res


def main():
    """ Main function to test the script """
    # auth = ['', '', '/home/rmucci00/.globus/usercert.pem',
    #        '/home/rmucci00/.globus/userkey.pem']
    globus = ClientGlobus(resource_file_path='globus_online_init.json');
    #globus.display_endpoint_list()
    globus.endpoint_activation('cineca#GALILEO', 'rmucci00')


if __name__ == '__main__':
    main()

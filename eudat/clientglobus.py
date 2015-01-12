#!/usr/bin/env python

"""
Client which uses Globus API
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

from abstractclient import AbstractClient
from globusonline.transfer.api_client import TransferAPIClient
from globusonline.transfer.api_client import x509_proxy


class ClientGlobus(AbstractClient):
    def __init__(self, auth, http_session=None):
        self.auth = auth
        self.http_session = http_session
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
        """ Method to activate endpoints"""
        user_credential_path = self.auth[3]
        print "==Activating endpoint: {0}==".format(endpoint_name)

        # Trying with autoactivation
        print "==Trying autoactivation=="
        code, message, result = self.api.endpoint_autoactivate(
            endpoint_name)

        if result["code"].startswith("AutoActivated.CachedCredential"):
            # maybe better to check if doesn't start with AutoActivationFailed
            print "Endpoint {0} activated!".format(endpoint_name)
            print "result: {0} ({1})".format(result["code"], result["message"])
            return

        # Trying with myproxy
        print "==Trying myproxy for {0}==".format(myproxy_username)
        #status, message, data = self.api.endpoint_autoactivate(
        #    endpoint_name)
        data.set_requirement_value("myproxy", "username",
                                   myproxy_username)
        from getpass import getpass
        passphrase = getpass()
        data.set_requirement_value("myproxy", "passphrase", passphrase)
        status, message, result = self.api.endpoint_activate(endpoint_name, data)
        if result["code"].startswith("AutoActivated.CachedCredential"):
            # maybe better to check if doesn't start with AutoActivationFailed
            print "Endpoint {0} activated!".format(endpoint_name)
            print "result: {0} ({1})".format(result["code"], result["message"])
            return

        #Trying activating local proxy
        print "==Local proxy activation=="
        _, _, reqs = self.api.endpoint_activation_requirements(
            endpoint_name, type="delegate_proxy")
        public_key = reqs.get_requirement_value("delegate_proxy",
                                                "public_key")
        proxy = x509_proxy.create_proxy_from_file(user_credential_path,
                                                  public_key)
        reqs.set_requirement_value("delegate_proxy", "proxy_chain",
                                   proxy)
        code, message, result = self.api.endpoint_activate(endpoint_name, reqs)
        if result["code"].startswith("AutoActivated.CachedCredential"):
            # maybe better to check if doesn't start with AutoActivationFailed
            print "Endpoint {0} activated!".format(endpoint_name)
            print "result: {0} ({1})".format(result["code"], result["message"])
            return


    """def preferred_activation(self, endpoint_name, myproxy_username):

        #user_credential_path=os.getcwd()+"/credential-"+username+".pem"
        user_credential_path = self.auth[2]
        print "==Activating endpoint: {0}==".format(endpoint_name)
        #api = TransferAPIClient(username, cert_file=user_credential_path)
        #api.set_debug_print(False, False)
        try:
            code, message, data = self.api.endpoint(endpoint_name)
            if not data["activated"]:
                try:
                    print "==Try autoactivation=="
                    code, message, data = self.api.endpoint_autoactivate(
                        endpoint_name)
                except:
                    print "Cannot autoactivate"
        except:
            data = {'activated': "Unavailable"}
            #pass

        #try:
        #    code, message, data = api.endpoint(endpoint_name)
        #except:
        #    data={'activated': "Unavailable"}

        if not data["activated"]: # and data["activated"] == "Unavailable":
            try:
                if myproxy_username != "none":
                    print "==Try myproxy for {0}==".format(myproxy_username)
                    status, message, data = self.api.endpoint_autoactivate(
                        endpoint_name)
                    data.set_requirement_value("myproxy", "username",
                                               myproxy_username)
                    from getpass import getpass
                    passphrase = getpass()
                    data.set_requirement_value("myproxy", "passphrase",
                                               passphrase)
                    self.api.endpoint_activate(endpoint_name, data)
                    #activer=[username,"-c",os.getcwd()+"/credential.pem"]
                    #api, _ = create_client_from_args(activer)
                    #conditional_activation(endpoint_name,myproxy_username)
                    code, message, data = self.api.endpoint(endpoint_name)
                else:
                    raise
            except:
                print "==Local proxy activation=="
                _, _, reqs = self.api.endpoint_activation_requirements(
                    endpoint_name, type="delegate_proxy")
                #print "endpoint_name",endpoint_name
                #print reqs
                public_key = reqs.get_requirement_value("delegate_proxy",
                                                        "public_key")
                #print public_key
                proxy = x509_proxy.create_proxy_from_file(user_credential_path,
                                                          public_key)
                #print "proxy"
                #print proxy
                reqs.set_requirement_value("delegate_proxy", "proxy_chain",
                                           proxy)
                #print reqs
                result = self.api.endpoint_activate(endpoint_name, reqs)
                #print result
                #status, message, data = api.endpoint_autoactivate(endpoint_name)
                #print data["code"]"""

    def display_activation(self, endpoint_name):
        """ Display endopoint's informtion"""
        print "=== Endpoint pre-activation ==="
        self.display_endpoint(endpoint_name)

        code, reason, result = self.api.endpoint_autoactivate(endpoint_name,
                                                         if_expires_in=600)
        if result["code"].startswith("AutoActivationFailed"):
            print "Auto activation failed, ls and transfers will likely fail!"
        print "result: %s (%s)" % (result["code"], result["message"])
        print "=== Endpoint post-activation ==="
        self.display_endpoint(endpoint_name)
        print

    def display_endpoint(self, endpoint_name):
        code, reason, data = self.api.endpoint(endpoint_name)
        self._print_endpoint(data)

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

    def active_endpoint(self):
        pass

    def put(self):
        pass

    def get(self):
        pass

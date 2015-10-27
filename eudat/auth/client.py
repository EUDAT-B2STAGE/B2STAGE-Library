#!/usr/bin/env python

"""
Manage authentication to Globus or HTTP API
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it), ' \
             'Giuseppe Fiameni (g.fiameni@cineca.it)'

from globusonline.transfer.api_client import TransferAPIClient


class Client():

    def __init__(self, auth, http_session=None):
        """ Store the object containing the information needed for
        the authentication """

        # Need to find a smart method to check if auth is a list or an object
        if len(auth) < 2:
            print "/'auth/' object must contain at least 2 values"

        self.auth = auth
        self.session = http_session
        if self.auth[0]:
            print "user name set as {0}".format(self.auth[0])
        if self.auth[1]:
            print "password set as ************".format(self.auth[1])

        if len(self.auth) > 2:
            if self.auth[2]:
                print "cert file set as {0}".format(self.auth[2])
            if self.auth[3]:
                print "key file set as {0}".format(self.auth[3])

    def login(self):
        """ Perform the login via GSI or username and password """
        api = None
        if len(self.auth) > 2 and self.auth[0] and self.auth[2] and self.auth[3]:
            try:
                api = TransferAPIClient(username=self.auth[0],
                                        cert_file=self.auth[2],
                                        key_file=self.auth[3])
            except Exception as e:
                raise Exception("GSI authentication failed: {0}".format(e))

        elif self.auth[0] and self.auth[1]:
            # authentication with username and password not supported yet
            raise Exception("Authentication with username and password not "
                            "supported yet..")

        return api

    def display_activation(self, endpoint_name):
        print "=== Endpoint pre-activation ==="
        self.display_endpoint(endpoint_name)

        print
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

"""
    def _get_auth_token(self, content):
        for line in content.splitlines():
            if line.startswith('Auth='):
                return line[5:]
        return None

    def _add_xml_header(self, data):
        return "<?xml version='1.0' encoding='UTF-8'?>%s" % data.decode()

"""



"""
       def __init__(self, username, server_ca_file=None,
                 cert_file=None, key_file=None,
                 base_url=DEFAULT_BASE_URL,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 httplib_debuglevel=0, max_attempts=1,
                 header_auth=None, goauth=None):
"""


def login(email, password):
    """Login to Google API using `email` and `password`.

    This is a shortcut function which instantiates :class:`Client`
    and performes login right away.

    :returns: :class:`Client` instance.

    """
    client = Client(auth=(email, password))
    client.login()
    return client


def login(username, cert_file, key_file):
    client = Client(auth=(username, cert_file, key_file, 'GSI'))
    client.login()
    return client


def authorize(credentials):
    """Login to Google API using OAuth2 credentials.

    This is a shortcut function which instantiates :class:`Client`
    and performes login right away.

    :returns: :class:`Client` instance.

    """
    # https://github.com/google/oauth2client/
    client = Client(auth=credentials)
    client.login()
    return client


def main():
    """ Main function to test the library """
    pass
    username = 'rmucci00'
    cert_file = '/home/fiameni/Documents/Personal/reserved/certificates/infn/expires_2015/usercert.pem'
    key_file = '/home/fiameni/Documents/Personal/reserved/certificates/infn/expires_2015/userkey.pem'

    api = TransferAPIClient(username, cert_file, key_file)

    print api.endpoint_list()

    # client = Client(auth=('username', 'cert_file', 'key_file', 'GSI'))
    # client.login()


if __name__ == '__main__':
    main()

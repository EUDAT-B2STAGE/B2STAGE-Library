import re

'''
from xml.etree import ElementTree
from . import __version__
from .. import find
'''

from globusonline.transfer import api_client

from globusonline.transfer.api_client import TransferAPIClient
from globusonline.transfer.api_client.goauth import get_access_token

_url_key_re_v1 = re.compile(r'key=([^&#]+)')
_url_key_re_v2 = re.compile(r'spreadsheets/d/([^&#]+)/edit')

from gspread import *


class Client(object):

    def __init__(self, auth, http_session=None):
        self.auth = auth
        self.session = http_session

    def login(self):
        try:
            self.api = TransferAPIClient(username=self.auth[0], cert_file= self.auth[1], key_file=self.auth[2])
        except:
            raise AuthenticationError("Unable to authenticate.")

    """Authorize client using ClientLogin protocol.

        The credentials provided in `auth` parameter to class' constructor will be used.

        This method is using API described at:
        http://code.google.com/apis/accounts/docs/AuthForInstalledApps.html

        :raises AuthenticationError: if login attempt fails.

        """


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


if __name__ == '__main__':
    username = 'gfiameni'
    cert_file = '/home/fiameni/Documents/Personal/reserved/certificates/infn/expires_2015/usercert.pem'
    key_file = '/home/fiameni/Documents/Personal/reserved/certificates/infn/expires_2015/userkey.pem'

    api = TransferAPIClient(username, cert_file, key_file)

    print api.endpoint_list()

    # client = Client(auth=('username', 'cert_file', 'key_file', 'GSI'))
    # client.login()
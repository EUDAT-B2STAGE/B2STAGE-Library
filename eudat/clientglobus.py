#!/usr/bin/env python

"""
Client which uses Globus API
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

from abstractclient import AbstractClient
from globusonline.transfer.api_client import TransferAPIClient


class ClientGlobus(AbstractClient):
    def __init__(self, auth, http_session=None):
        self.auth = auth
        self.http_session = http_session
        self.api = None

    def login(self):
        if len(self.auth) > 2 and self.auth[0] and self.auth[2] \
                and self.auth[3]:
            try:
                self.api = TransferAPIClient(username=self.auth[0],
                                             cert_file=self.auth[2],
                                             key_file=self.auth[3])
                print "Successfully logged in with Globus!"
            except Exception as e:
                raise Exception("GSI authentication failed: {0}".format(e))

    def active_endpoint(self):
        pass

    def put(self):
        pass

    def get(self):
        pass

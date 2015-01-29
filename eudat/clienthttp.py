#!/usr/bin/env python

"""
Client which uses HTTP API
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

from baseclient import AbstractClient


class ClientHTTP(AbstractClient):
    def __init__(self, auth, http_session=None):
        self.auth = auth
        self.http_session = http_session

    def login(self):
        pass

    def put(self):
        pass

    def get(self):
        pass
#!/usr/bin/env python

"""
Client abstract class
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

from abc import ABCMeta, abstractmethod


class AbstractClient(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, auth, http_session=None):
        """ Store the object containing the information needed for
        the authentication """
        pass

        """# Need to find a smart method to check if auth is a list or an object
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
                """

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def put(self):
        pass

    @abstractmethod
    def get(self):
        pass

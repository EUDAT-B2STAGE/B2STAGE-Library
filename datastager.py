#!/usr/bin/env python

"""
Module Docstring
Docstrings: http://www.python.org/dev/peps/pep-0257/
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

import os
#import datamover


class DataStager:

    def __init__(self):
        #define useful variables
        self.user_name = None
        self.password = None
        self.cert_path = None

    def auth_user_pass(self, username, password):
        """ Store username and password for authentication """
        if not username:
            print "Warning: username is empty!"
        if not password:
            print "Warning: password is empty!"

        self.user_name = username
        self.password = password

    def auth_gsi(self, certpath):
        """ Store path to certificate for authentication via GSI """
        if not certpath:
            print "Warning: certpath is empty!"
        if not os.path.isfile(certpath):
            print "Warning: certpath file not found!"

        self.cert_path = certpath

    def put_globus_ftp(self, source, destination, destination_dir):
        """ Upload a resource using GO api """
        if not source:
            print "Warning: source not defined!"
        if not destination:
            print "Warning: destination not defined!"
        if not destination_dir:
            print "Warning: destination_dir not defined!"

        #manage the stage in



def main():
    """ Main function to test the library """
    pass


if __name__=='__main__':
    main()
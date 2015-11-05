#!/usr/bin/env python

"""
Test  b2stage.py
"""

__author__ = 'rmucci00'

from nose.tools import assert_equals
from eudat import b2stage


def test_globus_login():
    """ B2STAGE: Globus online login """
    # globus client (passing cert paths)
    auth = ['rmucci00', '', '/home/rmucci00/.globus/usercert.pem',
            '/home/rmucci00/.globus/userkey.pem']
    globus = b2stage.ClientGlobus(auth);

    assert_equals(globus.api.cert_file, '/home/rmucci00/.globus/usercert.pem')


# Problem: how can I automatically activate endpoints to perform tests??
'''
def test_globus_endpoint_activation():
    """ B2STAGE: Globus endpoint activation """
    # globus client (passing cert paths)
    auth = ['rmucci00', '', '/home/rmucci00/.globus/usercert.pem',
            '/home/rmucci00/.globus/userkey.pem']
    globus = b2stage.ClientGlobus(auth);
    result = globus.endpoint_activation('cineca#GALILEO', 'rmucci00')

    assert_equals(result, True)


def test_globus_transfer():
    """ B2STAGE: Globus online login """


task_id = client.put('rmucci00#FERMI','cineca#PICO', '/fermi/home/userinternal/rmucci00/aniTest.avi', '/~/')
'''
#!/usr/bin/env python

"""
Test  b2stage.py
"""

__author__ = 'rmucci00'

import os
from nose.tools import assert_equals
from eudat import b2stage


def test_globus_login():
    """ B2STAGE: Globus online login """
    resource_file = os.path.join(os.getcwd(),
                                 'eudat/test/b2stage_credentials_test_template.json')
    globus = b2stage.ClientGlobus(resource_file_path=resource_file);

    assert globus.api is not None


def test_globus_endpoint_activation():
    """ B2STAGE: Globus online GridFTP endpoint activation """
    resource_file = os.path.join(os.getcwd(),
                                 'eudat/test/b2stage_credentials_test_template.json')
    globus = b2stage.ClientGlobus(resource_file_path=resource_file);
    result = globus.endpoint_activation('cineca#GALILEO')
    assert_equals(result, True)



def test_globus_transfer():
    """ B2STAGE: Globus online data transfer """

    resource_file = os.path.join(os.getcwd(),
                                 'eudat/test/b2stage_credentials_test_template.json')
    globus = b2stage.ClientGlobus(resource_file_path=resource_file);
    task_id = globus.transfer('cineca#DataRepository','cineca#PICO',
                              '/CINECA01/home/cin_staff/rmucci00/DSI_Test/',
                              '/pico/home/userinternal/rmucci00/DSI_Test/')

    assert task_id is not None

    #globus.display_task(task_id, False)
    status = globus.wait_for_task(task_id, timeout=60, poll_interval=10)
    assert_equals(status, "SUCCEEDED")
    globus.display_task(task_id)
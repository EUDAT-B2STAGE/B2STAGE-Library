#!/usr/bin/env python

"""
Test b2stage.py
"""

__author__ = 'rmucci00'

import os
import json
from nose.tools import assert_equals
from eudat import b2stage

# Credentials and other necessary values that should not be public:
RESOURCES_FILE = os.path.join(os.getcwd(),
                                 'eudat/test/b2stage_credentials_test_template.json')
testvalues = json.load(open(RESOURCES_FILE))


def test_globus_login():
    """ B2STAGE: Globus online login """
    globus = b2stage.ClientGlobus(resource_file_path=RESOURCES_FILE);

    assert globus.api is not None


def test_globus_endpoint_activation():
    """ B2STAGE: Globus online GridFTP endpoint activation """

    globus = b2stage.ClientGlobus(resource_file_path=RESOURCES_FILE);
    result = globus.endpoint_activation(testvalues['dst_endpoint'])
    assert_equals(result, True)


def test_globus_transfer():
    """ B2STAGE: Globus online folder transfer """

    globus = b2stage.ClientGlobus(resource_file_path=RESOURCES_FILE);
    # src_item must be a folder, since recursive is set to True
    task_id = globus.transfer(testvalues['src_endpoint'],
                              testvalues['dst_endpoint'],
                              testvalues['src_item'],
                              testvalues['dst_dir'], recursive=True)

    assert task_id is not None

    status = globus.wait_for_task(task_id, timeout=60, poll_interval=10)
    assert_equals(status, "SUCCEEDED")
    globus.display_successful_transfer(task_id)
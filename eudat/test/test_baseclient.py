#!/usr/bin/env python

"""
Test  baseclient.py
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


from nose import with_setup
from nose.tools import assert_equals
from eudat.baseclient import BaseClient


def test_get_info_by_metadata():
    """ get info by metadata for community aleph"""
    client = BaseClient()
    datasets = client.get_info_by_metadata(community='aleph')

    assert_equals(datasets[0][0]['value'], '635491664')


def test_get_pid_by_metadata():
    """ get pids by metadata for community aleph """
    client = BaseClient()
    pids = client.get_pid_by_metadata(community='aleph')

    assert_equals(pids[0], 'http://hdl.handle.net/11100/1f765c5e-cbe5-11e3-98a6-e41f13eb41b2')


def test_resolve_pid():
    """ get info resolving pid """
    client = BaseClient()
    pid = '11100/0beb6af8-cbe5-11e3-a9da-e41f13eb41b2'
    results = client.resolve_pid(pid)

    assert_equals(results[0]['data']['value'],
                  'irods://data.repo.cineca.it:1247/CINECA01/home/EUDAT_STAFF/Aleph_Test/ZD4000.59.AL')

def test_get_url_by_pid():
    """ get url by pid """
    client = BaseClient()
    pid = '11100/0beb6af8-cbe5-11e3-a9da-e41f13eb41b2'
    url = client.get_url_by_pid(pid)

    assert_equals(url[0],
                  'irods://data.repo.cineca.it:1247/CINECA01/home/EUDAT_STAFF/Aleph_Test/ZD4000.59.AL')




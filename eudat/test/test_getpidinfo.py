#!/usr/bin/env python

"""
Test  getpidinfo.py
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


from nose.tools import assert_equals
import eudat.find.getpidinfo as pidinfo


def test_get_pid_info():
    """ Get pid info """
    results = pidinfo.get_pid_info('11100/0beb6af8-cbe5-11e3-a9da-e41f13eb41b2')

    assert_equals(results[0]['data']['value'],
                  'irods://data.repo.cineca.it:1247/CINECA01/home/EUDAT_STAFF/Aleph_Test/ZD4000.59.AL')


def test_get_pid_info_wrong_URL():
    """ Get pid info with wrong URL"""
    results = pidinfo.get_pid_info('11100/0beb6af8-cbe5-11e3-a9da-e41f13eb41b2',
                                   handle_url='wrong.url')

    assert_equals(results, None)


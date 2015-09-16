#!/usr/bin/env python

"""
Test  getdatasetinfo.py
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


from nose.tools import assert_equals
import eudat.find.getdatasetinfo as info


def test_get_dataset_info_aleph():
    datasets = info.get_dataset_info(ckan_url='eudat-b1.dkrz.de',
                                     community='aleph',
                                     pattern=[],
                                     ckan_limit=1000)

    assert_equals(datasets[0][0]['value'], '635491664')
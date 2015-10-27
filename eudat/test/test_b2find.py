#!/usr/bin/env python

"""
Test  b2find.py
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


from nose.tools import assert_equals
import eudat.b2find as b2find



def test_get_dataset_info_aleph():
    """ B2SAFE: get info by community aleph """
    datasets = b2find.get_dataset_info(ckan_url='eudat-b1.dkrz.de',
                                     community='aleph',
                                     pattern=[],
                                     ckan_limit=1000)

    assert_equals(datasets[0][0]['value'], '635491664')


def test_get_dataset_info_wrong_url():
    """ B2SAFE: get info with wrong ckan URL """
    datasets = b2find.get_dataset_info(ckan_url='wrong.url',
                                     community='aleph')

    assert_equals(datasets, None)


def test_get_dataset_info_by_tags():
    """ B2SAFE: get info by pattern """
    datasets = b2find.get_dataset_info(pattern=['tags:climate'])

    assert_equals(len(datasets), 4)


def test_get_dataset_source_aleph():
    """ B2SAFE: get source by community aleph """
    datasets = b2find.get_dataset_source(ckan_url='eudat-b1.dkrz.de',
                                     community='aleph',
                                     pattern=[],
                                     ckan_limit=1000)

    assert_equals(len(datasets), 185)
    assert_equals(datasets[0], 'irods://data.repo.cineca.it:1247/CINECA01/home/EUDAT_STAFF/Aleph_Test/ZD4000.60.AL')
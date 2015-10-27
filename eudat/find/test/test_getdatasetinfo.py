#!/usr/bin/env python

"""
Test  getdatasetinfo.py
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


from nose.tools import assert_equals
import eudat.find.getdatasetinfo as datasetinfo



def test_get_dataset_info_aleph():
    """ Get info by community aleph """
    datasets = datasetinfo.get_dataset_info(ckan_url='eudat-b1.dkrz.de',
                                     community='aleph',
                                     pattern=[],
                                     ckan_limit=1000)

    assert_equals(datasets[0][0]['value'], '635491664')


def test_get_dataset_info_wrong_url():
    """ Get info with wrong ckan URL """
    datasets = datasetinfo.get_dataset_info(ckan_url='wrong.url',
                                     community='aleph')

    assert_equals(datasets, None)


def test_get_dataset_info_by_tags():
    """ Get info by pattern """
    datasets = datasetinfo.get_dataset_info(pattern=['tags:climate'])

    assert_equals(len(datasets), 4)


def test_get_dataset_source_aleph():
    """ Get source by community aleph """
    datasets = datasetinfo.get_dataset_source(ckan_url='eudat-b1.dkrz.de',
                                     community='aleph',
                                     pattern=[],
                                     ckan_limit=1000)

    assert_equals(len(datasets), 185)
    assert_equals(datasets[0], 'irods://data.repo.cineca.it:1247/CINECA01/home/EUDAT_STAFF/Aleph_Test/ZD4000.60.AL')
#!/usr/bin/env python

"""
Client abstract class
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

from abc import ABCMeta, abstractmethod
import find.getdatasetinfo as datasetinfo


class AbstractClient(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, auth, http_session=None):
        """ Store the object containing the information needed for
        the authentication """
        pass

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def put(self):
        pass

    @abstractmethod
    def get(self):
        pass

    def find_by_metadata(self, ckan_url='eudat-b1.dkrz.de', community='',
                         pattern=[], ckan_limit=1000):
        """
        Retrieve datasets information by given search criteria.
        Returns a list of datasets (each dataset is a list of dictionary
        composed by key and value).

        ckan_url : string
            CKAN portal address, to which search requests are submitted
            (default is eudat-b1.dkrz.de).
        community : string
            Community where you want to search in.
        pattern : list
            CKAN search pattern, i.e. (a list of) field:value terms.
        ckan_limit : int
            Limit of listed datasets (default is 1000).
        """
        results = datasetinfo.get_dataset_info(ckan_url=ckan_url,
                                               community=community,
                                               pattern=pattern,
                                               ckan_limit=ckan_limit)
        return results

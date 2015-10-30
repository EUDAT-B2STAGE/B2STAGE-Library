#!/usr/bin/env python

"""
Base client that furnish all the functionality: login, data transfer, find over
metadata, get PID, resolve PID...
Some methods are abstract and implemented in specific classes.
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


import b2find as datasetinfo
import getpidinfo as pidinfo


class BaseClient(object):

    def __init__(self, auth='', http_session=None):
        """ Store the object containing the information needed for
        the authentication """
        pass

    def login(self):
        pass

    def put(self):
        pass

    def get(self):
        pass

    def get_info_by_metadata(self, ckan_url='eudat-b1.dkrz.de', community='',
                         pattern=[], ckan_limit=1000):
        """
        Retrieve dataset info by given search criteria using CKAN portal.

        :param ckan_url: CKAN portal address, to which search requests are
        submitted (default is eudat-b1.dkrz.de).
        :param community: Community where you want to search in.
        :param pattern: CKAN search pattern i.e. (a list of) field:value terms.
        :param ckan_limit: Limit of listed datasets (default is 1000).
        :return: list of datasets (each dataset is a list of dictionary
        composed by key and value) considering only the datasets containing
        a pid value.
        """
        results = datasetinfo.get_dataset_info(ckan_url=ckan_url,
                                               community=community,
                                               pattern=pattern,
                                               ckan_limit=ckan_limit)
        return results


    def get_pid_by_metadata(self, ckan_url='eudat-b1.dkrz.de', community='',
                         pattern=[], ckan_limit=1000):
        """
        Retrieve dataset PIDs by given search criteria using CKAN portal.

        :param ckan_url: CKAN portal address, to which search requests are
        submitted (default is eudat-b1.dkrz.de).
        :param community: Community where you want to search in.
        :param pattern: CKAN search pattern i.e. (a list of) field:value terms.
        :param ckan_limit: Limit of listed datasets (default is 1000).
        :return: list of PIDs (with handle URL).
        """
        results = datasetinfo.get_dataset_info(ckan_url=ckan_url,
                                               community=community,
                                               pattern=pattern,
                                               ckan_limit=ckan_limit)
        pid_list = []
        for ds in results:
            for extra in ds:
                if extra['key'] == 'PID':
                    pid_list.append(extra['value'])

        return pid_list

    def resolve_pid(self, pid, handle_url='hdl.handle.net'):
        """
        Resolve PIDs information accessing the handle resolution system provider
        using HTTP REST API.

        :param pid: PID that has to be resolved
        :param handle_url: Handle system provider address
        (default is hdl.handle.net).
        :return: list of dictionary containing PID information.
        """
        results = pidinfo.get_pid_info(pid, handle_url)
        return results

    def get_url_by_pid(self, pid, handle_url='hdl.handle.net'):
        """
        Resolve pid information accessing the handle resolution system provider
        using HTTP REST API.

        :param pid: PID that has to be resolved
        :param handle_url: Handle system provider address
        (default is hdl.handle.net).
        :return: physical URL of the data.
        """
        results = pidinfo.get_pid_info(pid, handle_url)

        pid_list = []
        for ds in results:
            if ds['type'] == 'URL':
                url = ds['data']['value']
                pid_list.append(url)

        return pid_list

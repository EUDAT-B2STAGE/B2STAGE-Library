#!/usr/bin/env python

"""
Python API for B2FIND.
Retrieve dataset info by given search criteria using CKAN portal
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


import json
import requests
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(NullHandler())


def get_dataset_source(ckan_url='eudat-b1.dkrz.de', community='', pattern=[],
                     ckan_limit=1000):
    """
    Retrieve datasets source by given search criteria using CKAN portal.

    :param ckan_url: CKAN portal address, to which search requests are submitted
        (default is eudat-b1.dkrz.de).
    :param community: Community where you want to search in.
    :param pattern: CKAN search pattern, i.e. (a list of) field:value terms.
    :param ckan_limit: Limit of listed datasets (default is 1000).
    :return: list of datasets source (each source should be physical URL to the
    data object).
    """

    if (not pattern) and (not community):
        print "[ERROR] Need at least a community or a search pattern as " \
              "argument!"
        return

    ckan_pattern = ''
    sand = ''
    pattern = ' AND '.join(pattern)
    if community:
        ckan_pattern += "groups:%s" % community
        sand = " AND "
    if pattern:
        ckan_pattern += sand + pattern

    LOGGER.debug("Search in %s for pattern %s\n....." % (ckan_url, ckan_pattern))
    answer = _action(ckan_url, {"q": ckan_pattern, "rows": ckan_limit,
                               "start": 0})

    if answer is None:
        return answer

    countURL = 0
    results = []
    for ds in answer['result']['results']:
            results.append(ds['url'])
            countURL += 1

    LOGGER.info("Found %d Sources\n" % (countURL))
    return results


def get_dataset_info(ckan_url='eudat-b1.dkrz.de', community='', pattern=[],
                     ckan_limit=1000):
    """
    Retrieve datasets info by given search criteria using CKAN portal.

    :param ckan_url: CKAN portal address, to which search requests are submitted
        (default is eudat-b1.dkrz.de).
    :param community: Community where you want to search in.
    :param pattern: CKAN search pattern, i.e. (a list of) field:value terms.
    :param ckan_limit: Limit of listed datasets (default is 1000).
    :return: list of datasets (each dataset is a list of dictionary
    composed by key and value) considering only the datasets containing a pid
    value.
    """
    if (not pattern) and (not community):
        print "[ERROR] Need at least a community or a search pattern as " \
              "argument!"
        return

    ckan_pattern = ''
    sand = ''
    pattern = ' AND '.join(pattern)
    if community:
        ckan_pattern += "groups:%s" % community
        sand = " AND "
    if pattern:
        ckan_pattern += sand + pattern

    LOGGER.debug("Search in %s for pattern %s\n....." % (ckan_url, ckan_pattern))
    answer = _action(ckan_url, {"q": ckan_pattern, "rows": ckan_limit,
                               "start": 0})

    if answer is None:
        return answer

    countPID = 0
    results = []
    for ds in answer['result']['results']:
            for extra in ds['extras']:
                if extra['key'] == 'PID':
                    # add dataset to list
                    results.append(ds['extras'])
                    countPID += 1
                    break

    LOGGER.info("Found %d PIDs\n" % (countPID))
    return results


def _action(host, data={}):
    return __action_api(host, 'package_search', data)


def __action_api(host, action, data_dict):
    # Make the HTTP request for data set generation.
    action_url = "http://{host}/api/3/action/{action}".format(host=host,
                                                              action=action)

    try:
        response = requests.get(action_url, params=data_dict)
    except requests.exceptions.RequestException as e:
        print e.message
        return
    except requests.exceptions.HTTPError as e:
        print e
        return
    if response.status_code != 200:
        print "Error code {0}. The server {1} couldn't fulfill the action {2}.\n"\
            .format(response.status_code, host, action)
        return
    out = json.loads(response.text)
    return out


def main():
    """ Main function to test the script """
    #get_dataset_info(pattern=['tags:MPIOM'])
    get_dataset_info(community='aleph')
    get_dataset_source(community='aleph')
    get_dataset_source(pattern=['tags:climate'])


if __name__ == '__main__':
    main()
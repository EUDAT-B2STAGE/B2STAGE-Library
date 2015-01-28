#!/usr/bin/env python

"""
Retrieve dataset info by given search criteria using CKAN portal
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


import json
import urllib
import urllib2


def get_dataset_info(ckan_url='eudat-b1.dkrz.de', community='', pattern=[],
                     ckan_limit=1000):
    """
    Retrieve dataset info by given search criteria using CKAN portal.
    Returns a list of datasets (each dataset is a list of dictionary
    composed by key and value).

    Retrieve datasets information by given search criteria.
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

    print "Search in\t%s\nfor pattern\t%s\n....." % (ckan_url, ckan_pattern)
    answer = action(ckan_url, {"q": ckan_pattern, "rows": ckan_limit,
                               "start": 0})
    tcount = answer['result']['count']
    print "=> %d datasets found" % tcount
    if tcount > ckan_limit:
        print "=> but maximal %d rows are returned " % ckan_limit
    ## print '    | %-4s | %-40s |\n    |%s|' % ('#','Dataset ID',"-" * 53)

    countpid = 0
    counter = 0
    cstart = 0
    results = []

    while cstart < tcount:
        if cstart > 0:
            answer = action(ckan_url, {"q": ckan_pattern, "rows": ckan_limit,
                                       "start": cstart})
        for ds in answer['result']['results']:
            counter += 1
            ## print'    | %-4d | %-40s |' % (counter,ds['name'])
            for extra in ds['extras']:
                if extra['key'] == 'PID':
                    # add dataset to list
                    results.append(ds['extras'])
                    countpid += 1
                    break

        cstart += len(answer['result']['results'])

    print "Found %d records and %d associated PIDs" % (counter, countpid)
    return results


def action(host, data={}):
    ## action (action, jsondata) - method
    # Call the api action <action> with the <jsondata> on the CKAN instance
    # which was defined by iphost
    # parameter of CKAN_CLIENT.
    #
    # Parameters:
    # -----------
    # (string)  action  - Action name of the API v3 of CKAN
    # (dict)    data    - Dictionary with json data
    #
    # Return Values:
    # --------------
    # (dict)    response dictionary of CKAN
    return __action_api(host, 'package_search', data)


def __action_api(host, action, data_dict):
    # Make the HTTP request for data set generation.
    response=''
    rvalue = 0
    action_url = "http://{host}/api/3/action/{action}".format(host=host,
                                                              action=action)

    # make json data in conformity with URL standards
    data_string = urllib.quote(json.dumps(data_dict))

    ##print('\t|-- Action %s\n\t|-- Calling %s\n\t|-- Object %s ' %
    # (action,action_url,data_dict))
    try:
       request = urllib2.Request(action_url)
       response = urllib2.urlopen(request,data_string)
    except urllib2.HTTPError as e:
        print "\t\tError code %s : The server %s couldn't fulfill the action" \
              " %s." % (e.code,host,action)
        if e.code == 403:
            print '\t\tAccess forbidden, maybe the API key is not valid?'
            exit(e.code)
        elif e.code == 409 and action == 'package_create':
            print '\t\tMaybe the dataset already exists or you have' \
                  ' a parameter error?'
            action('package_update', data_dict)
            return {"success": False}
        elif e.code == 409:
            print '\t\tMaybe you have a parameter error?'
            return {"success": False}
        elif e.code == 500:
            print '\t\tInternal server error'
            exit(e.code)
    except urllib2.URLError as e:
        exit('%s' % e.reason)
    else:
        out = json.loads(response.read())
        assert response.code >= 200
        return out

def main():
    """ Main function to test the script """
    #get_dataset_info(pattern=['tags:MPIOM'])
    get_dataset_info(community='aleph')



if __name__ == '__main__':
    main()
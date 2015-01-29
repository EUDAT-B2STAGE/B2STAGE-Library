#!/usr/bin/env python

"""
Retrieve pid information accessing the handle resolution system using HTTP
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


import json
#import urllib
import urllib2


def get_pid_info(pid, handle_url='hdl.handle.net'):
    """
    Resolve pid information accessing the handle resolution system provider
    using HTTP REST API.

    :param pid: PID that has to be resolved
    :param handle_url: Handle system provider address
     (default is hdl.handle.net).
    :return: a list of dictionary containing PID information.
    """
    if not pid:
        print "[ERROR] PID is needed to submit the request.. "
        return

    print "Search in\t%s\nfor pid\t%s\n....." % (handle_url, pid)
    answer = __action_api(handle_url, pid)
    values = answer['values']
    return values


def __action_api(host, pid):
    """ Make the HTTP request."""
    action_url = "http://{host}/api/handles/{pid}".format(host=host, pid=pid)

    try:
        request = urllib2.Request(action_url)
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        print "\t\tError code %s : The server %s responded with an error" \
              % (e.code, host)
        if e.code == 500:
            print '\t\tError. Something unexpected went wrong during handle ' \
                  'resolution. (HTTP 500 Internal Server Error)'
            exit(e.code)
        elif e.code == 404:
            print '\t\tHandle Not Found. (HTTP 404 Not Found)'
            exit(e.code)

    except urllib2.URLError as e:
        exit('%s' % e.reason)
    else:
        out = json.loads(response.read())
        if out['responseCode'] == 200:
            print 'Values Not Found. The handle exists but has no values ' \
                  '(or no values according to the types and indices specified)'

        assert response.code >= 200
        return out

def main():
    """ Main function to test the script """
    get_pid_info(pid='11100/0beb6af8-cbe5-11e3-a9da-e41f13eb41b2')



if __name__ == '__main__':
    main()
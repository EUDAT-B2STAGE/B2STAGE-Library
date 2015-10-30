#!/usr/bin/env python

"""
Factory class which creates an instance of the client (Globus or HTTP)
according to the authentication variables passed
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

import os
import time


class Context():
    """Class factory to create an instance of the client"""

    @staticmethod
    def create_client(auth=''):
        """Create an instance of the client"""
        # Need to find a smart method to understand which client has to be
        # created
        if len(auth) < 2:
            print "Credentials not specified: you will be able to use only " \
                  "services which don't require authentication."
            try:
                from baseclient import BaseClient
                base = BaseClient()
                return base
            except Exception as e:
                raise Exception('Error importing baseclient modules: '
                                '{0}'.format(e))
        if auth[0]:
            print "user name set as {0}".format(auth[0])
        if auth[1]:
            print "password set as ************".format(auth[1])

        if len(auth) == 4 and auth[0] and auth[2] and auth[3]:
            print "cert file set as {0}".format(auth[2])
            print "key file set as {0}".format(auth[3])
            try:
                from clientglobus import ClientGlobus
                globus = ClientGlobus(auth)
                return globus
            except Exception as e:
                raise Exception('Error importing clientglobus modules: '
                                '{0}'.format(e))
        elif auth[0] and auth[1] and auth[2]:
            print "HTTP API server set as {0}".format(auth[2])
            try:
                from clienthttp import ClientHTTP
                http = ClientHTTP(auth)
                return http
            except Exception as e:
                raise Exception('Error importing clienthttp modules: '
                                '{0}'.format(e))

        else:
            print "No client found initialisable with these parameters.."


def main():
    """ Main function to test the library """

    # Client without authentication
    client = Context.create_client()
    pid = '11100/0beb6af8-cbe5-11e3-a9da-e41f13eb41b2'
    url = client.get_url_by_pid(pid)
    for u in url:
        print "Here is the URL for pid {0}: {1}".format(pid, u)

    '''
    # HTTP client
    auth = ['rmucci00', 'saturnin0', 'fec03.cineca.it:8081']
    client = Context.create_client(auth)
    client.login()

    print
    print "Listing folder's element.."
    list = client.list('/CINECA/home/rmucci00/')
    for el in list:
        print el

    print
    print "Uploading an object.."
    client.put('/home/rmucci00/uploadTest.txt', 'CINECA/home/rmucci00/uploadTest.txt')

    print
    print "Downloading an object.."
    client.get('CINECA/home/rmucci00/uploadTest.txt', '/tmp/downtest_uploadTest.txt')

    print
    print "Listing folder's element.."
    list = client.list('/CINECA/home/rmucci00/')
    for el in list:
        print el

    print
    print "Deleting an object.."
    client.delete('CINECA/home/rmucci00/uploadTest.txt')

    # delete a folder
    # client.delete('CINECA/home/rmucci00/empty/')
    '''



    # globus client (passing cert paths)
    auth = ['rmucci00', '', '/home/rmucci00/.globus/usercert.pem',
            '/home/rmucci00/.globus/userkey.pem']



    # http client (passing username and pwd)
    #auth = ['rmucci00', '']

    client = Context.create_client(auth)
    client.login()

    datasets = client.get_info_by_metadata(community='aleph')
    for ds in datasets:
        print "Here is the dataset list info: {0}".format(ds)

    pids = client.get_pid_by_metadata(community='aleph')
    for pid in pids:
        print "Here is the PID: {0}".format(pid)

    pid = '11100/0beb6af8-cbe5-11e3-a9da-e41f13eb41b2'
    pids = client.get_url_by_pid(pid)
    for p in pids:
        print "Here is the URL for pid {0}: {1}".format(pid, p)

    client.get_endpoint_from_URL('irods://data.repo.cineca.it:1247/CINECA01/home/EUDAT_STAFF/Aleph_Test/ZD4000.59.AL')

    # 3rd party transfer
    #client.endpoint_activation('cineca#PICO', 'rmucci00')
    #client.endpoint_activation('rmucci00#FERMI', 'rmucci00')
    task_id = client.put('cineca#DataRepository','rmucci00#pdl', '/CINECA01/home/cin_staff/rmucci00/aniTest.avi', '/~/')
    #task_id = client.put('rmucci00#FERMI','cineca#PICO', '/fermi/home/userinternal/rmucci00/aniTest.avi', '/~/')

    time.sleep(10)
    client.display_task(task_id)

    #client.display_activation('rmucci00#iRODS-DEV')

    #status_code, status_message, data = globus.task_list()
    #print status_code, status_message
    #print data
    #client.display_activation("rmucci00#iRODS-DEV")


if __name__ == '__main__':
    main()

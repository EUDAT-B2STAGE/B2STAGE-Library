#!/usr/bin/env python

"""
Client which uses HTTP API
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

from baseclient import BaseClient
import base64
import urllib
import urllib2
from bs4 import BeautifulSoup


class ClientHTTP(BaseClient):
    def __init__(self, auth, http_session=None):
        """
        Initialize the HTTP client

        :param auth: a list containing username[0], password[1] and URL to
        the HTTP EUDAT server[2]
        :param http_session:
        """
        self.auth = auth
        if len(self.auth) < 3: #or !self.auth[0] or !self.auth[2] or !self.auth[3]:
             print "Can not authenticate user: some parameters are missing.."
        self.http_session = http_session

    def login(self):
        """ Login to the HTTP EUDAT server.
        Do I really need a login since I can always pass credentials in each
        HTTP request? Probably not.. """

        answer = self.__action_api(self.auth[2], self.auth[0], self.auth[1])
        #print "Login answer is --->", answer


    def put(self):
        pass

    def get(self, remote_object, dest_name):
        """
        Download an object

        :param remote_object: path to the object to be downloaded
        :param dest_dir: local folder in which the object will be stored

        """

        url = "http://{host}/{extra}".format(host=self.auth[2],
                                             extra=remote_object)

        print
        print "Downloading {0} to {1}".format(remote_object,  dest_name)

        request = urllib2.Request(url)
        base64string = base64.encodestring(
                '%s:%s' % (self.auth[0], self.auth[1])).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        file_name = url.split('/')[-1]
        u = urllib2.urlopen(request)
        f = open(dest_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)

        file_size_dl = 0
        block_sz = 8192
        while True:
            buf = u.read(block_sz)
            if not buf:
                break

            file_size_dl += len(buf)

            f.write(buf)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. /
                                           file_size)
            #status = status + chr(8)*(len(status)+1)
            print status

        f.close()

        """response = self.__action_api(self.auth[2], self.auth[0], self.auth[1],
                                     remote_object)

        output = open(dest_name, 'wb')
        output.write(response)
        output.close()
        """
        print
        print "{0} downloaded in {1}".format(remote_object, dest_name)



    def list(self, path):
        """
        List the content of a folder (weak implementation)

        :param path: path of the folder to be listed
        :return: list containing the elements of the folder
        """
        response = self.__action_api(self.auth[2], self.auth[0], self.auth[1],
                                     path)
        sub_soup = BeautifulSoup(response)

        #sub_soup = soup.find(style="list-style-type: none")

        elements = []

        for link in sub_soup.find_all('li'):
            el = link.find_all('a')[0].get('href')
            if path in el:
                elements.append(el)

        return elements



    def __action_api(self, host, username, password, extra_param=''):
        """
        Perform the HTTP request

        :param host: URL of the HTTP API
        :param username: username for the HTTP request
        :param password: password for the HTTP request
        :param extra_param: parameter to be added to the HTTP request
        :return: html response
        """
        action_url = "http://{host}/{extra}".format(host=host, extra=extra_param)

        try:
            request = urllib2.Request(action_url)

            base64string = base64.encodestring(
                '%s:%s' % (username, password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)

            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            print "\t\tError code %s : The server %s responded with an error" \
                  % (e.code, host)
            if e.code == 500:
                print '\t\tError. Something unexpected went wrong during handle ' \
                      'resolution. (HTTP 500 Internal Server Error)'
                exit(e.code)
            elif e.code == 401:
                print '\t\tThe authentication is invalid. ' \
                      '(HTTP 401 Unauthorized)'
                exit(e.code)
            elif e.code == 403:
                print '\t\tLack of authorization. (HTTP 403 Fobidden)'
                exit(e.code)
            elif e.code == 404:
                print '\t\tNot Found. (HTTP 404 Not Found)'
                exit(e.code)

        except urllib2.URLError as e:
            exit('%s' % e.reason)
        else:
            assert response.code >= 200
            return response.read()
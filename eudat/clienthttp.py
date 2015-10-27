#!/usr/bin/env python

"""
Client which uses HTTP API
"""

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

from baseclient import BaseClient
from bs4 import BeautifulSoup
import urllib2
import base64


class ClientHTTP(BaseClient):
    def __init__(self, auth, http_session=None):
        """
        Initialize the HTTP client

        :param auth: a list containing username[0], password[1] and URL to
        the HTTP EUDAT server[2]
        :param http_session:
        """
        self.auth = auth
        if len(self.auth) < 3: # or !self.auth[0] or !self.auth[2] or !self.auth[3]:
             print "Can not authenticate user: some parameters are missing.."
        self.http_session = http_session

    def login(self):
        """ Login to the HTTP EUDAT server.
        Do I really need a login methos since I can always pass credentials
        in each HTTP request? Probably no.. """

        answer = self.__action_api(self.auth[2])
        # print "Login answer is --->", answer

    def put(self, local_object, remote_destination):
        """
        Upload an object

        :param local_object: path to the local object to be uploaded
        :param remote_destination: remote destination directory

        """
        print
        print "Uploading {0} to {1}".format(local_object, remote_destination)

        fixed_path = self._fix_path(remote_destination)
        url = "http://{host}/{extra}".format(host=self.auth[2],
                                             extra=fixed_path)

        try:
            # file is read in memory: is there a way to avoid this?
            request = RequestWithMethod('PUT', url, file(local_object).read(),
                                      {'Content-Type': 'application/json'})

            base64string = base64.encodestring(
                    '%s:%s' % (self.auth[0], self.auth[1])).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)

            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            self._manage_http_error(e)

        except urllib2.URLError as e:
            exit('%s' % e.reason)
        else:
            assert response.code >= 200
            # print response.read()
            print "{0} uploaded in {1}".format(local_object,
                                               remote_destination)
            print

    def get(self, remote_object, dest_name):
        """
        Download an object

        :param remote_object: path to the object to be downloaded
        :param dest_name: local folder in which the object will be stored

        """

        print
        print "Downloading {0} to {1}".format(remote_object,  dest_name)

        fixed_path = self._fix_path(remote_object)
        url = "http://{host}/{extra}".format(host=self.auth[2],
                                             extra=fixed_path)

        try:
            request = urllib2.Request(url)
            base64string = base64.encodestring(
                    '%s:%s' % (self.auth[0], self.auth[1])).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)

            file_name = url.split('/')[-1]
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            self._manage_http_error(e)

        except urllib2.URLError as e:
            exit('%s' % e.reason)
        else:
            assert response.code >= 200
            #print response.read()

            f = open(dest_name, 'wb')
            meta = response.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            print "Downloading: %s Bytes: %s" % (file_name, file_size)

            file_size_dl = 0
            block_sz = 8192
            while True:
                buf = response.read(block_sz)
                if not buf:
                    break

                file_size_dl += len(buf)

                f.write(buf)
                status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. /
                                               file_size)
                # status = status + chr(8)*(len(status)+1)
                # print status

            f.close()
        print
        print "{0} downloaded in {1}".format(remote_object, dest_name)

    def list(self, path):
        """
        List the content of a folder (weak implementation)

        :param path: path of the folder to be listed
        :return: list containing the elements of the folder
        """
        print
        print "Listing {0}".format(path)

        fixed_path = self._fix_path(path)
        url = "http://{host}/{extra}".format(host=self.auth[2],
                                             extra=fixed_path)

        response = self.__action_api(self.auth[2], fixed_path)
        sub_soup = BeautifulSoup(response)

        #sub_soup = soup.find(style="list-style-type: none")

        elements = []

        for link in sub_soup.find_all('li'):
            el = link.find_all('a')[0].get('href')
            if path in el:
                elements.append(el)

        return elements

    def delete(self, path_to_resource):
        """
        Delete an object or a collection

        :param path_to_resource: path to the object to be deleted

        """

        fixed_path = self._fix_path(path_to_resource)
        url = "http://{host}/{extra}".format(host=self.auth[2],
                                             extra=fixed_path)

        print
        print "Deleting {0}".format(path_to_resource)
        try:
            request = RequestWithMethod('DELETE', url)

            base64string = base64.encodestring(
                    '%s:%s' % (self.auth[0], self.auth[1])).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)

            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            self._manage_http_error(e)

        except urllib2.URLError as e:
            exit('%s' % e.reason)
        else:
            assert response.code >= 200
            # print response.read()
            print "{0} deleted".format(path_to_resource)
            print




    def __action_api(self, host, extra_param=''):
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
                '%s:%s' % (self.auth[0], self.auth[1])).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)

            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            self._manage_http_error(e)

        except urllib2.URLError as e:
            exit('%s' % e.reason)
        #else:
        assert response.code >= 200
        return response.read()

    @staticmethod
    def _manage_http_error(e):
        """
        Internal function to manage Http error response

        :param error: exception received from the Http request
        """

        print "\t\tError code %s : The server responded with an error" \
                  % (e.code)
        if e.code == 500:
            print '\t\tError. (HTTP 500 Internal Server Error)'
            exit(e.code)
        elif e.code == 401:
            print '\t\tThe authentication is invalid. ' \
                  '(HTTP 401 Unauthorized)'
            exit(e.code)
        elif e.code == 403:
            print '\t\tLack of authorization. (HTTP 403 Forbidden)'
            exit(e.code)
        elif e.code == 404:
            print '\t\tNot Found. (HTTP 404 Not Found)'
            exit(e.code)
        elif e.code == 409:
            print '\t\tTarget already exists. (HTTP 409 Conflict)'
            exit(e.code)

    @staticmethod
    def _fix_path(path):
        """
        Remove first '/' if present

        :param path: original path
        :return: fixed path (without starting '/')
        """
        if path.startswith('/'):
            path = path[1:]
        return path


class RequestWithMethod(urllib2.Request):
    """
    Subclassed the urllib2.Request class to explicitly override the method
    """
    def __init__(self, method, *args, **kwargs):
        self._method = method
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self._method
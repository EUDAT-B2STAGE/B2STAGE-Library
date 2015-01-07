class Client(object):
    def __init__(self, auth, http_session=None):
        self.auth = auth
        self.session = http_session

    def login(self):
        if hasattr(self.auth, 'access_token'):
            print 'has'
        else:
            print 'no access token'
            setattr(self.auth, 'access_token', 'value')
            print self.auth.access_token

            if not self.auth.access_token or \
                    (hasattr(self.auth, 'access_token_expired') and self.auth.access_token_expired):
                self.auth.refresh()


if __name__ == '__main__':
    client = Client(auth=('username', 'cert_file', 'key_file', 'GSI'))
    client.login()
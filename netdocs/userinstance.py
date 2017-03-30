from netdocs.core import NetDocs

class UserInstance(NetDocs):
    """ NetDocs instance for a given user. """

    def set_user(self, refresh_token, scope="read"):
        """ Initialise a given user. """
        self.refresh_token = refresh_token
        self.get_new_access_token()
        self.set_scope(scope)

     def set_scope(self, scope):
        """ Set scope for access. """
        if scope in VALID_SCOPES:
            self.scope = scope

    def get_auth_url(self):
        """ Build authentication URL. """
        # Encode URL parameters...
        params = parse.urlencode({
            'client_id': self.client_id,
            'scope': parse.quote(self.scope, safe=''),
            'response_type': RESPONSE_TYPE
            })
        # ...apart from redirect_uri (server doesn't like this encoded)
        redirect_url = "=".join(['redirect_uri', self.redirect_uri])
        params = "&".join([params, redirect_url])

        return "?".join([self.auth_url, params])

    def get_refresh_token(self, authcode):
        self.authcode = authcode

        # Encode URL parameters
        params = {
            'grant_type': 'authorization_code',
            'code': authcode,
            'redirect_uri': self.redirect_uri
            }
        # ...apart from redirect_uri (server doesn't like this encoded)
        # redirect_url = "=".join(['redirect_uri', self.redirect_uri])
        # params = "&".join([params, redirect_url])


        url = self.refresh_url

        r = requests.post(url, headers=self.headers(), data=params)

        # print r.text
        try:
            params_dict = r.json()
            self.access_token = params_dict['access_token']
            self.refresh_token = params_dict['refresh_token']
            return self.refresh_token
        except:
            return None

    def get_new_access_token(self):
        # Encode URL parameters
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
            }

        url = self.refresh_url

        r = requests.post(url, headers=self.headers(), data=params)

        try:
            params_dict = r.json()
            self.access_token = params_dict['access_token']
            return "Success > token stored"
        except:
            return str(r.status_code)

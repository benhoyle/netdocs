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



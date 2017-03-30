class Error(Exception):
   """ Base class for other exceptions"""
   pass


class NDTokenError(Error):
    """ Error class for authentication errors. """
    pass


class NDAccessTokenError(NDTokenError):
    """ Error class for authentication errors. """
    pass


class NDRefreshTokenError(NDTokenError):
    """ Error class for authentication errors. """
    pass

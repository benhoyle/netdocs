import pytest

from netdocs.core import NetDocs

@pytest.yield_fixture(scope='session')
def nd():
    """
    Setup NetDocs object, this only gets executed once.

    :return: NetDocs object
    """
    nd = NetDocs("client_id", "client_secret")
    nd.configure_urls()

    yield nd

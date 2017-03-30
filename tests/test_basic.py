# -*- coding: utf-8 -*-
import pytest
import base64


class TestBasicSuite(object):
    """Basic test cases."""

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, nd):
        self.nd = nd

    def test_auth_headers(self):
        """ Test building auth headers. """
        headers = self.nd.auth_headers()
        assert len(headers) == 5

    def test_auth_url(self):
        """ Test generating an authentication URL. """
        auth_url = self.nd.get_auth_url()
        assert "client" in auth_url
        assert "localhost" in auth_url


    #def test_userdata(self):
        #""" Test successful connection via API and retrieval of user info. """
        #userdata = self.nd.get_user_data()
        #assert userdata[0] == 200
        #assert "email" in userdata[1].keys()

    #def test_cabinets(self):
        #""" Test retrieval of cabinet info. """
        #cabdata = self.nd.get_cabinets()
        #assert cabdata[0] == 200
        #assert "id" in cabdata[1][0].keys()



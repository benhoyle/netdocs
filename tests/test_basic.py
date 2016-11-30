# -*- coding: utf-8 -*-

from .context import netdocs
# Import other stuff here

import unittest

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        """Pre-test activities."""
        self.nd = netdocs.NetDocs()
    
    def test_userdata(self):
        """ Test successful connection via API and retrieval of user info. """
        userdata = self.nd.get_user_data()
        assert userdata[0] == 200
        assert "email" in userdata[1].keys()
    
    def test_cabinets(self):
        """ Test retrieval of cabinet info. """
        cabdata = self.nd.get_cabinets()
        assert cabdata[0] == 200
        assert "id" in cabdata[1][0].keys()
        

if __name__ == '__main__':
    unittest.main()
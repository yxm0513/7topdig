#!/usr/bin/python
import unittest
from .basic_tests import BasicTestCase, TestSetup
from .admin_tests import AdminTestCase



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    suite.addTest(unittest.makeSuite(BasicTestCase))
    suite.addTest(unittest.makeSuite(AdminTestCase))
    return suite

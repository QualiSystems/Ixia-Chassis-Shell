#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `TestCenterChassisDriver`
"""

import sys
import logging
import unittest

from shellfoundry.releasetools.test_helper import create_autoload_context


from src.driver import IxiaChassisDriver

client_install_path = 'C:/Program Files (x86)/Ixia/IxNetwork/8.01-GA'
client_install_path = 'C:/Program Files (x86)/Ixia/IxOS/8.30-EA'
client_install_path = ''
controller = ''
port = '8022'
port = '4555'
address = '192.168.42.170'
address = '192.168.42.61'


class TestIxiaChassisDriver(unittest.TestCase):

    def setUp(self):
        self.context = create_autoload_context(address, client_install_path, controller, port)
        self.driver = IxiaChassisDriver()
        self.driver.initialize(self.context)
        print self.driver.logger.handlers[0].baseFilename
        self.driver.logger.addHandler(logging.StreamHandler(sys.stdout))

    def tearDown(self):
        pass

    def testHelloWorld(self):
        pass

    def testAutoload(self):
        self.inventory = self.driver.get_inventory(self.context)
        for r in self.inventory.resources:
            print r.relative_address, r.model, r.name
        for a in self.inventory.attributes:
            print a.relative_address, a.attribute_name, a.attribute_value


if __name__ == '__main__':
    sys.exit(unittest.main())

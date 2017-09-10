#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `IxiaShellDriver`
"""

import sys
import logging
import unittest

from cloudshell.shell.core.driver_context import (ConnectivityContext, ResourceContextDetails, InitCommandContext)

from src.driver import IxiaChassisDriver

controller = 'localhost'
port = 8009
install_path = 'C:/Program Files (x86)/Ixia/IxNetwork/8.01-GA'

address = '192.168.42.168'
port = '8022'
install_path = 'C:/Program Files (x86)/Ixia/IxOS/8.30-EA'

address = '192.168.42.61'
port = ''
install_path = ''


class TestIxiaShellDriver(unittest.TestCase):

    def setUp(self):
        connectivity = ConnectivityContext(None, None, None, None)
        resource = ResourceContextDetails('testing', None, None, None, None, None, None, None, None, None)
        resource.address = address
        resource.attributes = {'Client Install Path': install_path,
                               'Controller Address': controller,
                               'Controller TCP Port': port}
        self.context = InitCommandContext(connectivity, resource)
        self.driver = IxiaChassisDriver()
        self.driver.initialize(self.context)
        print(self.driver.logger.handlers[0].baseFilename)
        self.driver.logger.addHandler(logging.StreamHandler(sys.stdout))

    def tearDown(self):
        pass

    def test_get_inventory(self):
        inventory = self.driver.get_inventory(self.context)
        for r in inventory.resources:
            print r.relative_address, r.model, r.name
        for a in inventory.attributes:
            print a.relative_address, a.attribute_name, a.attribute_value


if __name__ == '__main__':
    sys.exit(unittest.main())

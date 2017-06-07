#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `IxiaShellDriver`
"""

import unittest

from cloudshell.shell.core.driver_context import (ConnectivityContext, ResourceContextDetails, InitCommandContext)

from src.ixia_handler import IxiaHandler

address = '192.168.42.174'
port = '8022'
install_path = 'C:/Program Files (x86)/Ixia/IxOS/8.20-EA'

address = '192.168.42.61'
port = ''
install_path = ''

controller = 'localhost'
port = 8009
install_path = 'C:/Program Files (x86)/Ixia/IxNetwork/8.01-GA'


class TestIxiaShellDriver(unittest.TestCase):

    def setUp(self):
        self.connectivity = ConnectivityContext(None, None, None, None)
        self.resource = ResourceContextDetails(None, None, None, None, None, None, None, None, None, None)
        self.resource.address = address
        self.resource.attributes = {'Client Install Path': install_path,
                                    'Controller Address': controller,
                                    'Controller TCP Port': port}
        context = InitCommandContext(self.connectivity, self.resource)
        self.driver = IxiaHandler()
        self.driver.initialize(context)

    def tearDown(self):
        pass

    def test_get_inventory(self):
        context = InitCommandContext(self.connectivity, self.resource)
        inventory = self.driver.get_inventory(context)
        for r in inventory.resources:
            print r.relative_address, r.model, r.name
        for a in inventory.attributes:
            print a.relative_address, a.attribute_name, a.attribute_value


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

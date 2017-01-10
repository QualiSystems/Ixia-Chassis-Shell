#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `IxiaShellDriver`
"""

import unittest

from cloudshell.shell.core.driver_context import (ConnectivityContext, ResourceContextDetails, InitCommandContext)

from src.ixia_handler import IxiaHandler


class TestIxiaShellDriver(unittest.TestCase):

    def setUp(self):
        self.connectivity = ConnectivityContext(None, None, None, None)
        self.resource = ResourceContextDetails(None, None, None, None, None, None, None, None, None, None)
        self.resource.address = '192.168.42.61'
        context = InitCommandContext(self.connectivity, self.resource)
        self.driver = IxiaHandler()
        self.driver.initialize(context)

    def tearDown(self):
        pass

    def test_get_inventory_something(self):
        context = InitCommandContext(self.connectivity, self.resource)
        inventory = self.driver.get_inventory(context)
        for r in inventory.resources:
            print r.relative_address, r.model, r.name
        for a in inventory.attributes:
            print a.relative_address, a.attribute_name, a.attribute_value


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

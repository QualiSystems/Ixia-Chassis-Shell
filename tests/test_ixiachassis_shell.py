#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `IxiaShellDriver`
"""

import sys
import unittest

from cloudshell.api.cloudshell_api import CloudShellAPISession, ResourceAttributesUpdateRequest, AttributeNameValue

ixia_chassis = {
                'win-ixos': {'address': '192.168.42.61',
                             'controller': '',
                             'port': '',
                             'install_path': '',
                             'modules': 5,
                             },
                'lin-ixos': {'address': '192.168.42.172',
                             'controller': '',
                             'port': '8022',
                             'install_path': 'C:/Program Files (x86)/Ixia/IxOS/8.30-EA',
                             'modules': 1,
                             },
                'ixnetwork': {'address': '192.168.42.61',
                              'controller': 'localhost',
                              'port': '8009',
                              'install_path': 'C:/Program Files (x86)/Ixia/IxNetwork/8.01-GA',
                              'modules': 5,
                              },
                }


class TestIxiaShellDriver(unittest.TestCase):

    session = None

    def setUp(self):
        self.session = CloudShellAPISession('localhost', 'admin', 'admin', 'Global')

    def tearDown(self):
        for resource in self.session.GetResourceList('Testing').Resources:
            self.session.DeleteResource(resource.Name)

    def testHelloWorld(self):
        pass

    def test_get_inventory(self):
        for name, properties in ixia_chassis.items():
            self.resource = self.session.CreateResource(resourceFamily='Traffic Generator Chassis',
                                                        resourceModel='Ixia Chassis',
                                                        resourceName=name,
                                                        resourceAddress=properties['address'],
                                                        folderFullPath='Testing',
                                                        parentResourceFullPath='',
                                                        resourceDescription='should be removed after test')
            self.session.UpdateResourceDriver(self.resource.Name, 'IxiaChassisDriver')
            attributes = [AttributeNameValue('Client Install Path', properties['install_path']),
                          AttributeNameValue('Controller Address', properties['controller']),
                          AttributeNameValue('Controller TCP Port', properties['port'])]
            self.session.SetAttributesValues(ResourceAttributesUpdateRequest(self.resource.Name, attributes))
            self.session.AutoLoad(self.resource.Name)
            resource_details = self.session.GetResourceDetails(self.resource.Name)
            assert(len(resource_details.ChildResources) == properties['modules'])
            self.session.DeleteResource(self.resource.Name)


if __name__ == '__main__':
    sys.exit(unittest.main())

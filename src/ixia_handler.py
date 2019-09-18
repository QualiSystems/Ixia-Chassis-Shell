
import os

from cloudshell.shell.core.driver_context import AutoLoadDetails, AutoLoadResource, AutoLoadAttribute

from trafficgenerator.tgn_utils import ApiType
from ixexplorer.ixe_app import init_ixe
from ixnetwork.ixn_app import init_ixn, IxnApp


class IxiaHandler(object):

    def initialize(self, context, logger):
        """
        :type context: cloudshell.shell.core.driver_context.InitCommandContext
        """

        self.logger = logger

        port = context.resource.attributes['Controller TCP Port']
        client_install_path = context.resource.attributes['Client Install Path']

        if 'ixnetwork' in client_install_path.lower():
            self.ixia = init_ixn(ApiType.tcl, self.logger, client_install_path)
            controller_address = context.resource.attributes['Controller Address']
            if not controller_address:
                controller_address = 'localhost'
            if not port:
                port = 8009
            self.ixia.connect(tcl_server=controller_address, tcl_port=port)
        else:
            address = context.resource.address
            rsa_id = None
            if client_install_path:
                rsa_id = os.path.join(client_install_path, 'TclScripts/lib/ixTcl1.0/id_rsa')
                port = 8022
            # Not likely, but on Windows servers users can set the Tcl server port, so we can't assume 4555.
            if not port:
                port = 4555
            self.ixia = init_ixe(ApiType.socket, self.logger, host=address, port=int(port), rsa_id=rsa_id)
            self.ixia.connect()
            self.ixia.add(address)

    def get_inventory(self, context):
        """ Return device structure with all standard attributes

        :type context: cloudshell.shell.core.driver_context.AutoLoadCommandContext
        :rtype: cloudshell.shell.core.driver_context.AutoLoadDetails
        """

        self.resources = []
        self.attributes = []
        if type(self.ixia) is IxnApp:
            address = context.resource.address
            chassis = self.ixia.root.hw.get_chassis(address)
            chassis.get_inventory()
            self._get_chassis_ixn(chassis)
        else:
            self.ixia.discover()
            self._get_chassis_ixos(self.ixia.chassis_chain.values()[0])
        details = AutoLoadDetails(self.resources, self.attributes)
        return details

    def _get_chassis_ixn(self, chassis):

        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Model',
                                                 attribute_value=chassis.attributes['chassisType']))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Serial Number',
                                                 attribute_value=''))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Server Description',
                                                 attribute_value=''))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Vendor',
                                                 attribute_value='Ixia'))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Version',
                                                 attribute_value=chassis.attributes['chassisVersion']))

        for module_id, module in chassis.cards.items():
            self._get_module_ixn(module_id, module)

    def _get_module_ixn(self, module_id, module):
        """ Get module resource and attributes. """

        relative_address = 'M' + str(module_id)
        resource = AutoLoadResource(model='Generic Traffic Generator Module', name='Module' + str(module_id),
                                    relative_address=relative_address)
        self.resources.append(resource)
        self.attributes.append(AutoLoadAttribute(relative_address=relative_address,
                                                 attribute_name='Model',
                                                 attribute_value=module.attributes['description']))
        self.attributes.append(AutoLoadAttribute(relative_address=relative_address,
                                                 attribute_name='Serial Number',
                                                 attribute_value=''))
        self.attributes.append(AutoLoadAttribute(relative_address=relative_address,
                                                 attribute_name='Version',
                                                 attribute_value=''))

        for port_id, port in module.ports.items():
            self._get_port_ixn(relative_address, port_id, port)

    def _get_port_ixn(self, card_relative_address, port_id, port):
        """ Get port resource and attributes. """

        relative_address = card_relative_address + '/P' + str(port_id)
        resource = AutoLoadResource(model='Generic Traffic Generator Port', name='Port' + str(port_id),
                                    relative_address=relative_address)
        self.resources.append(resource)

    def _get_chassis_ixos(self, chassis):
        """ Get chassis resource and attributes. """

        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Model',
                                                 attribute_value=chassis.typeName))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Serial Number',
                                                 attribute_value=''))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Server Description',
                                                 attribute_value=''))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Vendor',
                                                 attribute_value='Ixia'))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Version',
                                                 attribute_value=chassis.ixServerVersion))
        for card_id, card in chassis.cards.items():
            self._get_module_ixos(card_id, card)

    def _get_module_ixos(self, card_id, card):
        """ Get module resource and attributes. """

        relative_address = 'M' + str(card_id)
        resource = AutoLoadResource(model='Generic Traffic Generator Module', name='Module' + str(card_id),
                                    relative_address=relative_address)
        self.resources.append(resource)
        self.attributes.append(AutoLoadAttribute(relative_address=relative_address,
                                                 attribute_name='Model',
                                                 attribute_value=card.typeName))
        self.attributes.append(AutoLoadAttribute(relative_address=relative_address,
                                                 attribute_name='Serial Number',
                                                 attribute_value=card.serialNumber.strip()))
        self.attributes.append(AutoLoadAttribute(relative_address=relative_address,
                                                 attribute_name='Version',
                                                 attribute_value=card.hwVersion))
        for port_id, port in card.ports.items():
            self._get_port_ixos(relative_address, port_id, port)

    def _get_port_ixos(self, card_relative_address, port_id, port):
        """ Get port resource and attributes. """

        relative_address = card_relative_address + '/P' + str(port_id)
        resource = AutoLoadResource(model='Generic Traffic Generator Port', name='Port' + str(port_id),
                                    relative_address=relative_address)
        self.resources.append(resource)
        supported_speeds = port.supported_speeds() if port.supported_speeds() else ['1000']
        self.attributes.append(AutoLoadAttribute(relative_address=relative_address,
                                                 attribute_name='Max Speed',
                                                 attribute_value=int(max(supported_speeds, key=int))))

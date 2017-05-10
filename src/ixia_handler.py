
import os
import logging

from cloudshell.shell.core.driver_context import AutoLoadDetails, AutoLoadResource, AutoLoadAttribute

from ixexplorer.ixe_app import IxeApp
from ixnetwork.api.ixn_python import IxnPythonWrapper
from ixnetwork.ixn_app import IxnApp


class IxiaHandler(object):

    def initialize(self, context):
        """
        :type context: cloudshell.shell.core.driver_context.InitCommandContext
        """

        self.logger = logging.getLogger('log')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.FileHandler('c:/temp/ixia_chassis_shell.log'))

        port = context.resource.attributes['Controller TCP Port']
        client_install_path = context.resource.attributes['Client Install Path']

        if 'ixnetwork' in client_install_path.lower():
            api = IxnPythonWrapper(self.logger, client_install_path)
            self.ixia = IxnApp(self.logger, api)
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
            self.ixia = IxeApp(self.logger, host=address, port=int(port), rsa_id=rsa_id)
            self.ixia.connect()

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
            self._get_chassis_ixos(self.ixia.chassis)
        details = AutoLoadDetails(self.resources, self.attributes)
        return details

    def _get_chassis_ixn(self, chassis):

        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Vendor',
                                                 attribute_value='Ixia'))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Model',
                                                 attribute_value=chassis.attributes['chassisType']))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Server Description',
                                                 attribute_value=''))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Version',
                                                 attribute_value=chassis.attributes['chassisVersion']))

        for module_id, module in chassis.modules.items():
            self._get_module_ixn(module_id, module)

    def _get_module_ixn(self, card_id, card):
        """ Get module resource and attributes. """

        resource = AutoLoadResource(model='Generic Traffic Generator Module', name='Card ' + card_id,
                                    relative_address=card_id)
        self.resources.append(resource)
        self.attributes.append(AutoLoadAttribute(relative_address=card_id,
                                                 attribute_name='Model',
                                                 attribute_value=card.attributes['description']))

        for port_id, port in card.ports.items():
            self._get_port_ixn(card_id, port_id, port)

    def _get_port_ixn(self, card_id, port_id, port):
        """ Get port resource and attributes. """

        resource = AutoLoadResource(model='Generic Traffic Generator Port', name='Port ' + port_id,
                                    relative_address=card_id + '/' + port_id)
        self.resources.append(resource)

    def _get_chassis_ixos(self, chassis):
        """ Get chassis resource and attributes. """

        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Vendor',
                                                 attribute_value='Ixia'))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Model',
                                                 attribute_value=chassis.type_name))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Server Description',
                                                 attribute_value=chassis.name))
        self.attributes.append(AutoLoadAttribute(relative_address='',
                                                 attribute_name='Version',
                                                 attribute_value=chassis.ix_server_version))
        for card in chassis.cards:
            if card is not None:
                self._get_module_ixos(card)

    def _get_module_ixos(self, card):
        """ Get module resource and attributes. """

        resource = AutoLoadResource(model='Generic Traffic Generator Module', name='Card ' + str(card.id),
                                    relative_address=card.id)
        self.resources.append(resource)
        self.attributes.append(AutoLoadAttribute(relative_address=card.id,
                                                 attribute_name='Model',
                                                 attribute_value=card.type_name))
        for port in card.ports:
            self._get_port_ixos(card, port)

    def _get_port_ixos(self, card, port):
        """ Get port resource and attributes. """

        resource = AutoLoadResource(model='Generic Traffic Generator Port', name='Port ' + str(port.id),
                                    relative_address=str(card.id) + '/' + str(port.id))
        self.resources.append(resource)
        self.logger.debug('supported_speeds = {}'.format(port.supported_speeds()))
#         supported_speed = max(port.supported_speeds(), key=int)
        supported_speed = '1000'
        self.attributes.append(AutoLoadAttribute(relative_address=str(card.id) + '/' + str(port.id),
                                                 attribute_name='Supported Speed',
                                                 attribute_value=int(supported_speed)))

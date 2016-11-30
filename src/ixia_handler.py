
import logging

from cloudshell.shell.core.driver_context import AutoLoadDetails, AutoLoadResource, AutoLoadAttribute

from ixia.pyixia import Ixia


class IxiaHandler(object):

    def initialize(self, context):
        """
        :type context: cloudshell.shell.core.driver_context.InitCommandContext
        """

        self.logger = logging.getLogger('log')
        self.logger.setLevel('DEBUG')
        self.ixia = Ixia(host=context.resource.address)
        self.ixia.connect()

    def get_inventory(self, context):
        """ Return device structure with all standard attributes

        :type context: cloudshell.shell.core.driver_context.AutoLoadCommandContext
        :rtype: cloudshell.shell.core.driver_context.AutoLoadDetails
        """

        self.ixia.discover()
        self.resources = []
        self.attributes = []
        self._get_chassis(self.ixia.chassis)
        details = AutoLoadDetails(self.resources, self.attributes)
        return details

    def load_config(self, context, config_file_name):
        """
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        """
        pass

    def start_traffic(self, context):
        """
        :type context: cloudshell.shell.core.driver_context.ResourceRemoteCommandContext
        """
        pass

    def stop_traffic(self, context):
        """
        :type context: cloudshell.shell.core.driver_context.ResourceRemoteCommandContext
        """
        pass

    def _get_chassis(self, chassis):
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
                self._get_module(card)

    def _get_module(self, card):
        """ Get module resource and attributes. """

        resource = AutoLoadResource(model='Generic Traffic Module', name='Card ' + str(card.id),
                                    relative_address=card.id)
        self.resources.append(resource)
        self.attributes.append(AutoLoadAttribute(relative_address=card.id,
                                                 attribute_name='Model',
                                                 attribute_value=card.type_name))
        for port in card.ports:
            self._get_port(card, port)

    def _get_port(self, card, port):
        """ Get port resource and attributes. """

        resource = AutoLoadResource(model='Generic Traffic Port', name='Port ' + str(port.id),
                                    relative_address=str(card.id) + '/' + str(port.id))
        self.resources.append(resource)

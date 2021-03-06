# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=no-member

from tortuga.cli.tortugaCli import TortugaCli
from tortuga.exceptions.invalidCliRequest import InvalidCliRequest
from tortuga.wsapi.nodeWsApi import NodeWsApi


class ShutdownNodeCli(TortugaCli):
    def parseArgs(self, usage=None):
        optionGroupName = _('Shutdown Node Options')
        self.addOptionGroup(optionGroupName, '')
        self.addOptionToGroup(optionGroupName, '--node',
                              dest='nodeName', required=True,
                              help=_('Name of node to shutdown'))

        super().parseArgs(usage=usage)

    def runCommand(self):
        self.parseArgs(_('Shuts down the given node'))

        api = self.configureClient(NodeWsApi)

        try:
            # Perform a "soft" shutdown
            api.shutdownNode(self.getArgs().nodeName, True)

        except Exception as msg:
            raise InvalidCliRequest(
                _("Can't shutdown node(s) - %s") % (msg))


def main():
    ShutdownNodeCli().run()

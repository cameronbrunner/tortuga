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

import socket
from typing import Dict, List, NoReturn, Optional

from sqlalchemy.orm.session import Session

from tortuga.exceptions.nodeNotFound import NodeNotFound
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.objects.node import Node
from tortuga.objects.parameter import Parameter
from tortuga.objects.provisioningInfo import ProvisioningInfo
from tortuga.objects.tortugaObject import TortugaObjectList

from .dbManager import DbManager
from .globalParameterDbApi import GlobalParameterDbApi
from .models.node import Node as NodeModel
from .nodesDbHandler import NodesDbHandler
from .tortugaDbApi import TortugaDbApi


OptionsDict = Dict[str, bool]


class NodeDbApi(TortugaDbApi):
    """
    Nodes DB API class.
    """

    def __init__(self):
        super().__init__()

        self._nodesDbHandler = NodesDbHandler()
        self._globalParameterDbApi = GlobalParameterDbApi()

    def getNode(self, name: str, optionDict: OptionsDict = None) -> Node:
        """
        Get node from the db.

            Returns:
                node
            Throws:
                NodeNotFound
                DbError
        """

        with DbManager().session() as session:
            try:
                return self.__convert_nodes_to_TortugaObjectList(
                    [self._nodesDbHandler.getNode(session, name)],
                    optionDict=optionDict)[0]
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def getNodesByAddHostSession(self, ahSession: str,
                                 optionDict: OptionsDict = None) \
            -> TortugaObjectList:
        """
        Get node(s) from db based their addhost session
        """

        with DbManager().session() as session:
            try:
                return self.__convert_nodes_to_TortugaObjectList(
                    self._nodesDbHandler.getNodesByAddHostSession(
                        session, ahSession), optionDict=optionDict)
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def getNodesByNameFilter(self, nodespec: str,
                             optionDict: OptionsDict = None) \
            -> TortugaObjectList:
        """
        Get node(s) from db based on the name filter
        """

        with DbManager().session() as session:
            try:
                return self.__convert_nodes_to_TortugaObjectList(
                    self.__expand_nodespec(session, nodespec),
                    optionDict=optionDict)
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def getNodeById(self, nodeId: int, optionDict: OptionsDict = None) \
            -> Node:
        """
        Get node by id
        """

        with DbManager().session() as session:
            try:
                return self.__convert_nodes_to_TortugaObjectList(
                    [self._nodesDbHandler.getNodeById(
                        session, nodeId)], optionDict=optionDict)[0]
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def getNodeByIp(self, ip: str, optionDict: OptionsDict = None) -> Node:
        """
        Get node by ip
        """

        with DbManager().session() as session:
            try:
                return self.__convert_nodes_to_TortugaObjectList(
                    [self._nodesDbHandler.getNodeByIp(
                        session, ip)], optionDict=optionDict)[0]
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def __convert_nodes_to_TortugaObjectList(
            self, nodes: List[NodeModel],
            optionDict: OptionsDict = None) -> TortugaObjectList:
        """
        Return TortugaObjectList of nodes with relations populated

        :param nodes: List of Nodes objects
        :param relations: dict of relations to be loaded
        :return: TortugaObjectList
        """

        nodeList = TortugaObjectList()

        for node in nodes:
            self.loadRelations(node, optionDict)

            # ensure 'resourceadapter' relation is always loaded. This one
            # is special since it's a relationship inside of a relationship.
            # It needs to be explicitly defined.
            self.loadRelation(node.hardwareprofile, 'resourceadapter')

            nodeList.append(Node.getFromDbDict(node.__dict__))

        return nodeList

    def getNodeList(self, tags: Optional[dict] = None,
                    optionDict: OptionsDict = None) \
            -> TortugaObjectList:
        """
        Get list of all available nodes from the db.

            Returns:
                [node]
            Throws:
                DbError
        """

        with DbManager().session() as session:
            try:
                return self.__convert_nodes_to_TortugaObjectList(
                    self._nodesDbHandler.getNodeList(session, tags=tags),
                    optionDict=optionDict)
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def getProvisioningInfo(self, nodeName: str) -> ProvisioningInfo:
        """
        Get the provisioing information for a given provisioned address

            Returns:
                [provisioningInformation structure]
            Throws:
                NodeNotFound
                DbError
        """

        with DbManager().session() as session:
            try:
                provisioningInfo = ProvisioningInfo()

                dbNode = self._nodesDbHandler.getNode(session, nodeName)

                if dbNode.softwareprofile:
                    self.loadRelations(dbNode.softwareprofile, {
                        'partitions': True,
                    })

                    for component in dbNode.softwareprofile.components:
                        self.loadRelations(component, {
                            'kit': True,
                            'os': True,
                            'family': True,
                            'os_components': True,
                            'osfamily_components': True,
                        })

                self.loadRelation(dbNode, 'hardwareprofile')

                provisioningInfo.setNode(
                    Node.getFromDbDict(dbNode.__dict__))

                globalParameters = \
                    self._globalParameterDbApi.getParameterList()

                # manually inject value for 'installer'
                p = Parameter(name='Installer')

                hostName = socket.gethostname().split('.', 1)[0]

                if '.' in dbNode.name:
                    nodeDomain = dbNode.name.split('.', 1)[1]

                    priInstaller = hostName + '.%s' % (nodeDomain)
                else:
                    priInstaller = hostName

                p.setValue(priInstaller)

                globalParameters.append(p)

                provisioningInfo.setGlobalParameters(globalParameters)

                return provisioningInfo
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def startupNode(self, nodespec: str,
                    remainingNodeList: Optional[List[str]] = None,
                    bootMethod: Optional[str] = 'n') -> NoReturn:
        """
        Start Node
        """

        with DbManager().session() as session:
            try:
                dbNodes = self.__expand_nodespec(session, nodespec)

                if not dbNodes:
                    raise NodeNotFound(
                        'No matching nodes for nodespec [%s]' % (nodespec))

                self._nodesDbHandler.startupNode(
                    session, dbNodes, remainingNodeList=remainingNodeList,
                    bootMethod=bootMethod)

                session.commit()
            except TortugaException:
                session.rollback()
                raise
            except Exception as ex:
                session.rollback()
                self.getLogger().exception('%s' % ex)
                raise

    def shutdownNode(self, nodespec: str,
                     bSoftShutdown: Optional[bool] = False) -> NoReturn:
        """
        Shutdown Node

        Raises:
            NodeNotFound
        """

        with DbManager().session() as session:
            try:
                dbNodes = self.__expand_nodespec(session, nodespec)

                if not dbNodes:
                    raise NodeNotFound(
                        'No matching nodes for nodespec [%s]' % (nodespec))

                self._nodesDbHandler.shutdownNode(
                    session, dbNodes, bSoftShutdown)

                session.commit()
            except TortugaException:
                session.rollback()
                raise
            except Exception as ex:
                session.rollback()
                self.getLogger().exception('%s' % ex)
                raise

    def __expand_nodespec(self, session: Session, nodespec: str) \
            -> List[NodeModel]:
        # Expand wildcards in nodespec. Each token in the nodespec can
        # be wildcard that expands into one or more nodes.

        filter_spec = []

        for nodespec_token in nodespec.split(','):
            # Convert shell-style wildcards into SQL wildcards
            if '*' in nodespec_token or '?' in nodespec_token:
                filter_spec.append(
                    nodespec_token.replace('*', '%').replace('?', '_'))

                continue

            # Add nodespec "AS IS"
            filter_spec.append(nodespec_token)

        return self._nodesDbHandler.getNodesByNameFilter(session, filter_spec)

    def evacuateChildren(self, nodeName: str) -> NoReturn:
        """
        Evacuate Children of node
        """

        with DbManager().session() as session:
            try:
                dbNode = self._nodesDbHandler.getNode(session, nodeName)

                self._nodesDbHandler.evacuateChildren(session, dbNode)

                session.commit()
            except TortugaException:
                session.rollback()
                raise
            except Exception as ex:
                session.rollback()
                self.getLogger().exception('%s' % ex)
                raise

    def getChildrenList(self, nodeName: str,
                        optionDict: OptionsDict = None) -> TortugaObjectList:
        """
        Get children of node

        Raises:
            NodeNotFound
        """

        with DbManager().session() as session:
            try:
                parent_node = self._nodesDbHandler.getNode(session, nodeName)

                return self.__convert_nodes_to_TortugaObjectList(
                    parent_node.children, optionDict=optionDict
                )
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise

    def checkpointNode(self, nodeName: str) -> NoReturn:
        """
        Checkpoint Node
        """

        with DbManager().session() as session:
            try:
                self._nodesDbHandler.checkpointNode(session, nodeName)

                session.commit()
            except TortugaException:
                session.rollback()
                raise
            except Exception as ex:
                session.rollback()
                self.getLogger().exception('%s' % ex)
                raise

    def revertNodeToCheckpoint(self, nodeName: str) -> NoReturn:
        """
        Revert Node to Checkpoint
        """

        with DbManager().session() as session:
            try:
                self._nodesDbHandler.revertNodeToCheckpoint(session, nodeName)

                session.commit()
            except TortugaException:
                session.rollback()
                raise
            except Exception as ex:
                session.rollback()
                self.getLogger().exception('%s' % ex)
                raise

    def migrateNode(self, nodeName: str, remainingNodeList: List[NodeModel],
                    liveMigrate: bool) -> NoReturn:
        """
        Migrate Node
        """

        with DbManager().session() as session:
            try:
                self._nodesDbHandler.migrateNode(
                    session, nodeName, remainingNodeList, liveMigrate)

                session.commit()
            except TortugaException:
                session.rollback()
                raise
            except Exception as ex:
                session.rollback()
                self.getLogger().exception('%s' % ex)
                raise

    def setParentNode(self, nodeName: str, parentNodeName: str) -> NoReturn:
        '''
        Raises:
            NodeNotFound
        '''

        with DbManager().session() as session:
            try:
                dbNode = self._nodesDbHandler.getNode(session, nodeName)

                # Setting the parent to 'None' is equivalent to unsetting it
                dbNode.parentnode = self._nodesDbHandler.getNode(
                    session, parentNodeName) if parentNodeName else None

                session.commit()
            except TortugaException:
                session.rollback()
                raise
            except Exception as ex:
                session.rollback()
                self.getLogger().exception('%s' % ex)
                raise

    def getNodesByNodeState(self, state: str,
                            optionDict: OptionsDict = None) \
            -> TortugaObjectList:
        """
        Get nodes by node state
        """

        with DbManager().session() as session:
            try:
                return self.__convert_nodes_to_TortugaObjectList(
                    self._nodesDbHandler.getNodesByNodeState(session, state),
                    optionDict=optionDict)
            except TortugaException:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % (ex))
                raise

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

from tortuga.db.dbManager import DbManager
from tortuga.typestore.base import TypeStore
from .store import SqlalchemySessionHardwareProfileStore


class HardwareProfileStoreManager:
    """
    HardwareProfile store manager

    """
    _db_manager: DbManager = None
    _hwp_store: TypeStore = None

    @classmethod
    def get(cls) -> TypeStore:
        """
        Get an instance of the hwp store.

        :return HardwareProfileStore: the hwp store instance

        """
        if not cls._db_manager:
            from tortuga.web_service.database import dbm
            cls._db_manager = dbm
        if not cls._hwp_store:
            cls._hwp_store = SqlalchemySessionHardwareProfileStore(
                cls._db_manager)
        return cls._hwp_store

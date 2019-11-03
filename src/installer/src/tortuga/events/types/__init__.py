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

from .base import BaseEvent, get_event_class
from .hardwareprofile import HardwareProfileTagsChanged
from .node import NodeStateChanged, NodeTagsChanged
from .noderequest import (AddNodeRequestComplete, AddNodeRequestQueued,
                          DeleteNodeRequestComplete, DeleteNodeRequestQueued)
from .resourcerequest import (ResourceRequestCreated, ResourceRequestUpdated,
                              ResourceRequestDeleted)
from .software_profile import SoftwareProfileTagsChanged
from .tag import TagCreated, TagUpdated, TagDeleted
from .task import TaskFailed

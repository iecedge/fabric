
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
import os
import sys
from xossynchronizer.event_steps.eventstep import EventStep
from xossynchronizer.modelaccessor import model_accessor
from xossynchronizer.modelaccessor import FabricService, Switch, Service
from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

class KubernetesPodDetailsEventStep(EventStep):
    topics = ["xos.kubernetes.pod-details"]
    technology = "kafka"

    def __init__(self, *args, **kwargs):
        super(KubernetesPodDetailsEventStep, self).__init__(*args, **kwargs)

    @staticmethod
    def get_fabric_onos(service):
        service = Service.objects.get(id=service.id)
        # get the onos_fabric service
        fabric_onos = [s.leaf_model for s in service.provider_services if "onos" in s.name.lower()]

        if len(fabric_onos) == 0:
            raise Exception('Cannot find ONOS service in provider_services of Fabric')

        return fabric_onos[0]

    def process_event(self, event):
        value = json.loads(event.value)

        if (value.get("status") != "created"):
            return

        if "labels" not in value:
            return

        xos_service = value["labels"].get("xos_service")
        if not xos_service:
            return

        for fabric_service in FabricService.objects.all():
            onos_service = KubernetesPodDetailsEventStep.get_fabric_onos(fabric_service)
            if (onos_service.name.lower() != xos_service.lower()):
                continue

            for switch in Switch.objects.all():
                log.info("Dirtying Switch", switch=switch)
                switch.backend_code=0
                switch.backend_status="resynchronize due to kubernetes event"
                switch.save(update_fields=["updated", "backend_code", "backend_status"], always_update_timestamp=True)

                for port in switch.ports.all():
                    log.info("Dirtying SwitchPort", port=port)
                    port.backend_code=0
                    port.backend_status="resynchronize due to kubernetes event"
                    port.save(update_fields=["updated", "backend_code", "backend_status"], always_update_timestamp=True)

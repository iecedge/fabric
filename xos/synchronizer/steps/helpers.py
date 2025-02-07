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

class Helpers():
    @staticmethod
    def format_url(url):
        if 'http' in url:
            return url
        else:
            return 'http://%s' % url
    @staticmethod
    def get_onos_fabric_service(model_accessor):
        # FIXME do not select by name but follow ServiceDependency
        fabric_service = model_accessor.Service.objects.get(name="fabric")
        onos_fabric_service = fabric_service.provider_services[0].leaf_model
        return onos_fabric_service

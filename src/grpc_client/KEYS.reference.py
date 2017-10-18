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

#########################################################################
#                                                                       #
# This file is here for reference, the used one is generate by xos-genx #
#                                                                       #
#########################################################################

TOSCA_KEYS = {
    'XOSBase': [],
    'User': ['email'],
    'Privilege': [],
    'AddressPool': ['name'],
    'Controller': ['name'],
    'ControllerImages': [],
    'ControllerNetwork': [],
    'ControllerRole': [],
    'ControllerSite': [],
    'ControllerPrivilege': [],
    'ControllerSitePrivilege': [],
    'ControllerSlice': [],
    'ControllerSlicePrivilege': [],
    'ControllerUser': [],
    'Deployment': ['name'],
    'DeploymentPrivilege': [],
    'DeploymentRole': [],
    'Diag': ['name'],
    'Flavor': ['name'],
    'Image': ['name'],
    'ImageDeployments': [],
    'Instance': ['name'],
    'Network': ['name'],
    'NetworkParameter': [],
    'NetworkParameterType': ['name'],
    'NetworkSlice': ['network', 'slice'],
    'NetworkTemplate': ['name'],
    'Node': ['name'],
    'NodeLabel': ['name'],
    'Port': [],
    'Role': [],
    'Service': ['name'],
    'ServiceAttribute': ['name'],
    'ServiceDependency': ['provider_service'],
    'ServiceMonitoringAgentInfo': ['name'],
    'ServicePrivilege': [],
    'ServiceRole': [],
    'Site': ['name'],
    'SiteDeployment': ['site', 'deployment'],
    'SitePrivilege': ['site', 'role'],
    'SiteRole': [],
    'Slice': ['name'],
    'SlicePrivilege': [],
    'SliceRole': [],
    'Tag': ['name'],
    'InterfaceType': ['name'],
    'ServiceInterface': ['service', 'interface_type'],
    'ServiceInstance': ['name'],
    'ServiceInstanceLink': ['provider_service_instance'],
    'ServiceInstanceAttribute': ['name'],
    'TenantWithContainer': ['name'],
    'XOS': ['name'],
    'XOSGuiExtension': ['name'],
}
# -*- coding: utf-8 -*-
# !/usr/bin/env ambari-python-wrap
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Python imports
import imp
import os
import traceback
import re
import socket
import fnmatch
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STACKS_DIR = os.path.join(SCRIPT_DIR, '../../../../../stacks/')
PARENT_FILE = os.path.join(STACKS_DIR, 'service_advisor.py')

try:
    if "BASE_SERVICE_ADVISOR" in os.environ:
        PARENT_FILE = os.environ["BASE_SERVICE_ADVISOR"]
    with open(PARENT_FILE, 'rb') as fp:
        service_advisor = imp.load_module('service_advisor', fp, PARENT_FILE, ('.py', 'rb', imp.PY_SOURCE))
except Exception as e:
    traceback.print_exc()
    print
    "Failed to load parent"


class DorisServiceAdvisor(service_advisor.ServiceAdvisor):
    def __init__(self, *args, **kwargs):
        self.as_super = super(DorisServiceAdvisor, self)
        self.as_super.__init__(*args, **kwargs)
        self.initialize_logger("DorisServiceAdvisor")
        # Always call these methods
        self.modifyMastersWithMultipleInstances()
        self.modifyCardinalitiesDict()
        self.modifyHeapSizeProperties()
        self.modifyNotValuableComponents()
        self.modifyComponentsNotPreferableOnServer()
        self.modifyComponentLayoutSchemes()

    def modifyMastersWithMultipleInstances(self):
        pass

    def modifyCardinalitiesDict(self):
        pass

    def modifyHeapSizeProperties(self):
        pass

    def modifyNotValuableComponents(self):
        pass

    def modifyComponentsNotPreferableOnServer(self):
        pass

    def modifyComponentLayoutSchemes(self):
        pass

    def getServiceComponentLayoutValidations(self, services, hosts):
        return self.getServiceComponentCardinalityValidations(services, hosts, "Doris")

    def getServiceConfigurationRecommendations(self, configurations, clusterData, services, hosts):
        self.logger.info("Class: %s, Method: %s. Recommending Service Configurations." %
                         (self.__class__.__name__, inspect.stack()[0][3]))
        recommender = DorisRecommender()
        recommender.recommendDorisConfigurationsFromHDP(configurations, clusterData, services, hosts)

    def getServiceConfigurationsValidationItems(self, configurations, recommendedDefaults, services, hosts):
        self.logger.info("Class: %s, Method: %s. Validating Configurations." %
                         (self.__class__.__name__, inspect.stack()[0][3]))
        validator = DorisValidator()
        return validator.validateListOfConfigUsingMethod(configurations, recommendedDefaults, services, hosts,
                                                         validator.validators)


class DorisRecommender(service_advisor.ServiceAdvisor):
    def __init__(self, *args, **kwargs):
        self.as_super = super(DorisRecommender, self)
        self.as_super.__init__(*args, **kwargs)

    def recommendDorisConfigurationsFromHDP(self, configurations, clusterData, services, hosts):
        putFollowerSiteProperty = self.putProperty(configurations, "doris-env", services)
        dorisFollowerHost = self.getHostsWithComponent("DORIS", "DORIS_FE", services, hosts)
        isFeHa = False
        if len(dorisFollowerHost) > 0:
            followerHosts = ''
            for host in dorisFollowerHost:
                followerHosts = followerHosts + ',' + host["Hosts"]["host_name"]
                isFeHa = followerHosts.replace(",", "", 1).count(',') >= 2
            putFollowerSiteProperty("doris_fe_follower_host_list", followerHosts.replace(",", "", 1))

        if isFeHa:
            putFollowerProperty2 = self.putProperty(configurations, "doris-fe.conf", services)
            putFollowerProperty2("replica_sync_policy", 'SIMPLE_MAJORITY')
            putFollowerProperty2("master_sync_policy", 'SIMPLE_MAJORITY')

        putObserverSiteProperty = self.putProperty(configurations, "doris-env", services)
        dorisObserverHost = self.getHostsWithComponent("DORIS", "DORIS_FE_OBSERVER", services, hosts)
        if len(dorisObserverHost) > 0:
            observerHosts = ''
            for host in dorisObserverHost:
                observerHosts = observerHosts + ',' + host["Hosts"]["host_name"]
            putObserverSiteProperty("doris_fe_observer_host_list", observerHosts.replace(",", "", 1))


class DorisValidator(service_advisor.ServiceAdvisor):
    def __init__(self, *args, **kwargs):
        self.as_super = super(DorisValidator, self)
        self.as_super.__init__(*args, **kwargs)
        self.validators = []

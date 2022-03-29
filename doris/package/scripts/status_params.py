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

import params
from resource_management.libraries.script import Script

config = Script.get_config()
# pid dir
doris_pid_dir = "/var/run/doris"

# pid files
doris_fe_pid_file = doris_pid_dir + "/fe.pid"
doris_be_pid_file = doris_pid_dir + "/be.pid"
doris_broker_pid_file = doris_pid_dir + "/broker.pid"
palo_studio_pid_file = doris_pid_dir + "/studio.pid"

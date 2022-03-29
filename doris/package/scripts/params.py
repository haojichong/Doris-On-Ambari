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
from resource_management.libraries.script import Script

config = Script.get_config()
# Env
java64_home = config["ambariLevelParams"]["java_home"]
hostname = config['agentLevelParams']['hostname']

########################################## Doris Install ##########################################
# Download Url
doris_download = config['configurations']['env-doris']['doris_download']
# Download Path
doris_downloaded_path = config['configurations']['env-doris']['doris_downloaded_dir'] + "/palo"
# Install Path
doris_install_path = config['configurations']['env-doris']['install_path']
# User & Group
doris_user = config['configurations']['env-doris']['doris_user']
doris_group = config['configurations']['env-doris']['doris_group']

# Bin Dir
# fe bin dir
doris_fe_bin_path = doris_install_path + "/fe/bin"
# be bin dir
doris_be_bin_path = doris_install_path + "/be/bin"
# broker bin dir
doris_broker_bin_path = doris_install_path + "/broker/bin"

# Conf file path
doris_fe_conf_dir = doris_install_path + '/fe/conf/fe.conf'
doris_be_conf_dir = doris_install_path + '/be/conf/be.conf'
doris_broker_conf_dir = doris_install_path + '/broker/conf/apache_hdfs_broker.conf'

# Upgrade[Experimental Feature]
# upgrade_option = config['configurations']['env-doris']['is_minor_version_upgrade']

########################################## Doris Config ##########################################
# FE configuration parameters
LOG_DIR = config['configurations']['fe.conf']['LOG_DIR']
java_opts_for_jdk_9 = config['configurations']['fe.conf']['java9_opts']
java8_option = config['configurations']['fe.conf']['java8_opts']
fe_sys_log_level = config['configurations']['fe.conf']['sys_log_level']
fe_meta_dir = config['configurations']['fe.conf']['fe_meta_dir']
http_port = config['configurations']['fe.conf']['http_port']
rpc_port = config['configurations']['fe.conf']['rpc_port']
query_port = config['configurations']['fe.conf']['query_port']
edit_log_port = config['configurations']['fe.conf']['edit_log_port']
qe_max_connection = config['configurations']['fe.conf']['qe_max_connection']
mysql_service_nio_enabled = config['configurations']['fe.conf']['mysql_service_nio_enabled']
enable_batch_delete_by_default = config['configurations']['fe.conf']['enable_batch_delete_by_default']
disable_storage_medium_check = config['configurations']['fe.conf']['disable_storage_medium_check']
default_storage_medium = config['configurations']['fe.conf']['default_storage_medium']
enable_materialized_view = config['configurations']['fe.conf']['enable_materialized_view']
dynamic_partition_enable = config['configurations']['fe.conf']['dynamic_partition_enable']
max_conn_per_user = config['configurations']['fe.conf']['max_conn_per_user']
qe_query_timeout_second = config['configurations']['fe.conf']['qe_query_timeout_second']

# BE configuration parameters
PPROF_TMPDIR = config['configurations']['be.conf']['PPROF_TMPDIR']
be_sys_log_level = config['configurations']['be.conf']['sys_log_level']
be_data_path = config['configurations']['be.conf']['be_data_path']
be_port = config['configurations']['be.conf']['be_port']
be_rpc_port = config['configurations']['be.conf']['be_rpc_port']
webserver_port = config['configurations']['be.conf']['webserver_port']
heartbeat_service_port = config['configurations']['be.conf']['heartbeat_service_port']
brpc_port = config['configurations']['be.conf']['brpc_port']
storage_root_path = config['configurations']['be.conf']['storage_root_path']


# Broker configuration parameters
broker_ipc_port = config['configurations']['broker.conf']['broker_ipc_port']
client_expire_seconds = config['configurations']['broker.conf']['client_expire_seconds']

########################################## Palo Studio 1.0.1 ##########################################
# Download Url
palo_download = config['configurations']['env-doris']['palo_download']
# Download Path
palo_downloaded_path = config['configurations']['env-doris']['doris_downloaded_dir'] + "/palo-studio"
# Install Path
palo_install_path = doris_install_path + "/palo-studio"
# Bin Dir
palo_bin_path = palo_install_path
# Conf Path
palo_conf_file_path = palo_install_path + "/conf/studio.conf"
# Log Dir
palo_log_dir = palo_install_path + "/logs"
# configuration parameters
STUDIO_PORT = config['configurations']['studio.conf']['STUDIO_PORT']
MB_DB_TYPE = config['configurations']['studio.conf']['MB_DB_TYPE']
MB_DB_HOST = config['configurations']['studio.conf']['MB_DB_HOST']
MB_DB_PORT = config['configurations']['studio.conf']['MB_DB_PORT']
MB_DB_USER = config['configurations']['studio.conf']['MB_DB_USER']
MB_DB_PASS = config['configurations']['studio.conf']['MB_DB_PASS']
MB_DB_DBNAME = config['configurations']['studio.conf']['MB_DB_DBNAME']
DEPLOY_NAME = config['configurations']['studio.conf']['DEPLOY_NAME']

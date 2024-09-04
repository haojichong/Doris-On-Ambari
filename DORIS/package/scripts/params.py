# -*- coding: utf-8 -*-
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

from resource_management import *
from resource_management.libraries.functions.version import get_major_version
from resource_management.libraries.functions.version import format_stack_version

import commands

config = Script.get_config()

# Env
java64_home = config["ambariLevelParams"]["java_home"]
hostname = config['agentLevelParams']['hostname']
hostIpAddress = commands.getoutput('hostname -i')
stack_version_unformatted = config['clusterLevelParams']['stack_version']
stack_version_formatted_major = format_stack_version(stack_version_unformatted)
major_stack_version = get_major_version(stack_version_formatted_major)

# Doris Home Dir
doris_home_dir = '/usr/hdp/{0}/doris'.format(major_stack_version)

# User & Group
operator = 'root'
operatorGroup = 'root'
doris_user = config['configurations']['doris-env']['doris_user']
doris_group = config['configurations']['doris-env']['doris_group']
fe_root_password = config['configurations']['doris-env']['fe_root_password']
doris_package_download_url = config['configurations']['doris-env']['doris_download']

# get system local priority_networks
priority_networks = commands.getoutput(
    'ip a | grep `hostname -i` | awk -F \' \' \'{print $2}\''
)

# Bin Dir
# fe bin dir
doris_fe_bin_path = doris_home_dir + "/fe/bin"
# be bin dir
doris_be_bin_path = doris_home_dir + "/be/bin"
# broker bin dir
doris_broker_bin_path = doris_home_dir + "/broker/bin"

# Conf file path
doris_fe_conf_dir = doris_home_dir + '/fe/conf'
doris_be_conf_dir = doris_home_dir + '/be/conf'
doris_broker_conf_dir = doris_home_dir + '/broker/conf'
DORIS_FE_CONFIG_FILE = doris_fe_conf_dir + '/fe.conf'
DORIS_FE_LDAP_CONFIG_FILE = doris_fe_conf_dir + '/ldap.conf'
DORIS_BE_CONFIG_FILE = doris_be_conf_dir + '/be.conf'
DORIS_BE_ASAN_SUPPR_CONFIG_FILE = doris_be_conf_dir + '/asan_suppr.conf'
DORIS_BE_LSAN_SUPPR_CONFIG_FILE = doris_be_conf_dir + '/lsan_suppr.conf'
DORIS_BE_ODBCINST_INI_CONFIG_FILE = doris_be_conf_dir + '/odbcinst.ini'
DORIS_BROKER_CONFIG_FILE = doris_broker_conf_dir + '/apache_hdfs_broker.conf'
DORIS_BROKER_LOG4J_CONFIG_FILE = doris_broker_conf_dir + '/log4j.properties'
DORIS_BROKER_HDFS_SITE_FILE = doris_broker_conf_dir + '/hdfs-site.xml'

fe_log_default_dir = "/var/log/doris/fe"
be_log_default_dir = "/var/log/doris/be"

# FE configuration parameters
FE_CUR_DATE = config['configurations']['doris-fe.conf']['CUR_DATE']
FE_LOG_DIR = config['configurations']['doris-fe.conf']['LOG_DIR']
FE_JAVA_OPTS = config['configurations']['doris-fe.conf']['JAVA_OPTS']
FE_JAVA_OPTS_FOR_JDK_9 = config['configurations']['doris-fe.conf']['JAVA_OPTS_FOR_JDK_9']
fe_sys_log_level = config['configurations']['doris-fe.conf']['sys_log_level']
fe_sys_log_mode = config['configurations']['doris-fe.conf']['sys_log_mode']
fe_meta_dir = config['configurations']['doris-fe.conf']['meta_dir']
fe_http_port = config['configurations']['doris-fe.conf']['http_port']
fe_rpc_port = config['configurations']['doris-fe.conf']['rpc_port']
fe_query_port = config['configurations']['doris-fe.conf']['query_port']
fe_edit_log_port = config['configurations']['doris-fe.conf']['edit_log_port']
fe_log_roll_size_mb = config['configurations']['doris-fe.conf']['log_roll_size_mb']
fe_sys_log_dir = config['configurations']['doris-fe.conf']['sys_log_dir']
fe_sys_log_roll_num = config['configurations']['doris-fe.conf']['sys_log_roll_num']
fe_sys_log_verbose_modules = config['configurations']['doris-fe.conf']['sys_log_verbose_modules']
fe_audit_log_dir = config['configurations']['doris-fe.conf']['audit_log_dir']
fe_audit_log_modules = config['configurations']['doris-fe.conf']['audit_log_modules']
fe_audit_log_roll_num = config['configurations']['doris-fe.conf']['audit_log_roll_num']
fe_meta_delay_toleration_second = config['configurations']['doris-fe.conf']['meta_delay_toleration_second']
fe_qe_max_connection = config['configurations']['doris-fe.conf']['qe_max_connection']
fe_qe_slow_log_ms = config['configurations']['doris-fe.conf']['qe_slow_log_ms']
fe_enable_batch_delete_by_default = str(
    config['configurations']['doris-fe.conf']['enable_batch_delete_by_default']).lower()
fe_disable_storage_medium_check = str(config['configurations']['doris-fe.conf']['disable_storage_medium_check']).lower()
fe_default_storage_medium = config['configurations']['doris-fe.conf']['default_storage_medium']
fe_dynamic_partition_enable = str(config['configurations']['doris-fe.conf']['dynamic_partition_enable']).lower()
fe_max_bdbje_clock_delta_ms = config['configurations']['doris-fe.conf']['max_bdbje_clock_delta_ms']
fe_temp_dir = '/tmp/doris/fe'  # config['configurations']['doris-fe.conf']['fe_temp_dir']

DORIS_FE_CONFIG_ROOT_PASSWD_FILE = doris_fe_conf_dir + '/root_password'

# BE configuration parameters
BE_CUR_DATE = config['configurations']['doris-be.conf']['CUR_DATE']
BE_PPROF_TMPDIR = config['configurations']['doris-be.conf']['PPROF_TMPDIR']
BE_JAVA_OPTS = config['configurations']['doris-be.conf']['JAVA_OPTS']
BE_JAVA_OPTS_FOR_JDK_9 = config['configurations']['doris-be.conf']['JAVA_OPTS_FOR_JDK_9']
# BE_JAVA_HOME = config['configurations']['doris-be.conf']['JAVA_HOME']
BE_JEMALLOC_CONF = config['configurations']['doris-be.conf']['JEMALLOC_CONF']
BE_JEMALLOC_PROF_PRFIX = config['configurations']['doris-be.conf']['JEMALLOC_PROF_PRFIX']
be_be_sys_log_level = config['configurations']['doris-be.conf']['sys_log_level']
be_be_port = config['configurations']['doris-be.conf']['be_port']
be_webserver_port = config['configurations']['doris-be.conf']['webserver_port']
be_heartbeat_service_port = config['configurations']['doris-be.conf']['heartbeat_service_port']
be_brpc_port = config['configurations']['doris-be.conf']['brpc_port']
be_enable_https = str(config['configurations']['doris-be.conf']['enable_https']).lower()
be_ssl_certificate_path = config['configurations']['doris-be.conf']['ssl_certificate_path']
be_ssl_private_key_path = config['configurations']['doris-be.conf']['ssl_private_key_path']
be_enable_auth = str(config['configurations']['doris-be.conf']['enable_auth']).lower()
be_storage_root_path = config['configurations']['doris-be.conf']['storage_root_path']
be_sys_log_dir = config['configurations']['doris-be.conf']['sys_log_dir']
be_sys_log_roll_mode = config['configurations']['doris-be.conf']['sys_log_roll_mode']
be_sys_log_roll_num = config['configurations']['doris-be.conf']['sys_log_roll_num']
be_sys_log_verbose_modules = config['configurations']['doris-be.conf']['sys_log_verbose_modules']
be_log_buffer_level = config['configurations']['doris-be.conf']['log_buffer_level']
be_rpc_port = config['configurations']['doris-be.conf']['be_rpc_port']
# 这是正确的,该配置fe和be必须保持一致
be_thrift_server_type_of_fe = config['configurations']['doris-fe.conf']['thrift_server_type']

# Broker configuration parameters
broker_sys_log_level = config['configurations']['doris-broker.conf']['sys_log_level']
broker_broker_ipc_port = config['configurations']['doris-broker.conf']['broker_ipc_port']
broker_client_expire_seconds = config['configurations']['doris-broker.conf']['client_expire_seconds']
broker_sys_log_dir = config['configurations']['doris-broker.conf']['sys_log_dir']
broker_sys_log_roll_num = config['configurations']['doris-broker.conf']['sys_log_roll_num']
broker_sys_log_roll_mode = config['configurations']['doris-broker.conf']['sys_log_roll_mode']
broker_sys_log_verbose_modules = config['configurations']['doris-broker.conf']['sys_log_verbose_modules']
broker_audit_log_dir = config['configurations']['doris-broker.conf']['audit_log_dir']
broker_audit_log_roll_num = config['configurations']['doris-broker.conf']['audit_log_roll_num']
broker_audit_log_roll_mode = config['configurations']['doris-broker.conf']['audit_log_roll_mode']
broker_hdfs_site_file_path = '/etc/hadoop/conf/hdfs-site.xml'

# Fe fe-ldap.conf configuration parameters
fe_ldap_conf_content = config['configurations']['doris-fe-ldap.conf']['content']

# Broker log4j.properties configuration parameters
broker_log4j_prop_content = config['configurations']['doris-broker-log4j.properties']['content']

# Be asan_suppr.conf configuration parameters
asan_suppr_conf_content = config['configurations']['doris-asan_suppr.conf']['content']

# Be lsan_suppr.conf configuration parameters
lsan_suppr_conf_content = config['configurations']['doris-lsan_suppr.conf']['content']

# Be odbcinst.ini configuration parameters
odbcinst_ini_content = config['configurations']['doris-odbcinst.ini']['content']

# DORIS_FE
doris_fe_hosts_list = config['configurations']['doris-env']['doris_fe_follower_host_list']
# DORIS_FE_OBSERVER
doris_fe_observer_hosts_list = config['configurations']['doris-env']['doris_fe_observer_host_list']

# doris_fe_hosts_list.sort()
if len(doris_fe_hosts_list) > 0:
    doris_fe_host = doris_fe_hosts_list[0]

fe_root_password_sql = ''
if fe_root_password != '':
    fe_root_password_sql = '-p{0}'.format(fe_root_password)

# kerberos
security_enabled = config['configurations']['cluster-env']['security_enabled']
if security_enabled:
    kinit_path_local = get_kinit_path(default('/configurations/kerberos-env/executable_search_paths', None))
    doris_user_keytab = config['configurations']['doris-env']['doris_user_keytab']
    doris_user_principal_name = config['configurations']['doris-env']['doris_user_principal']
    doris_user_kinit_cmd = format("{kinit_path_local} -kt {doris_user_keytab} {doris_user_principal_name};")

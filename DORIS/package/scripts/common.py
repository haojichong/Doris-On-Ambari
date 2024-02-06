# -*- coding: utf-8 -*-
# !/usr/bin/env python
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
import commands
import os
import time

from resource_management import *
from resource_management import Environment
from resource_management.core import sudo

env = Environment.get_instance()


def doris_service(action=''):
    import params, status_params

    if params.security_enabled:
        Execute(params.doris_user_kinit_cmd, user=params.operator)

    # start doris service
    if action == 'fe_follower_start':
        fe_follower_start()
    elif action == 'fe_observer_start':
        fe_observer_start()
    elif action == 'be_start':
        be_start()
    elif action == 'broker_start':
        broker_start()
    # stop doris service
    elif action == 'fe_follower_stop':
        stopService("Fe Follower", params.doris_fe_bin_path, "fe.pid", status_params.doris_fe_pid_file, "stop_fe.sh")
    elif action == 'fe_observer_stop':
        stopService("Fe Observer", params.doris_fe_bin_path, "fe.pid", status_params.doris_fe_pid_file, "stop_fe.sh")
    elif action == 'be_stop':
        stopService("Be", params.doris_be_bin_path, "be.pid", status_params.doris_be_pid_file, "stop_be.sh", 'doris_be')
    elif action == 'broker_stop':
        stopService("Broker", params.doris_broker_bin_path, "apache_hdfs_broker.pid",
                    status_params.doris_broker_pid_file,
                    "stop_broker.sh", 'org.apache.doris.broker.hdfs.BrokerBootstrap')
    # add service to doris cluster
    elif action == 'add_be_to_cluster':
        addBe()
    elif action == 'add_broker_to_cluster':
        addBroker()
    elif action == 'add_fe_follower_to_cluster':
        addFe()
    elif action == 'add_fe_observer_to_cluster':
        addFe("OBSERVER")
    # delete service from doris cluster
    elif action == 'decommission_be_from_cluster':
        removeBe()
    elif action == 'remove_broker_from_cluster':
        removeBroker()
    elif action == 'remove_fe_follower_from_cluster':
        removeFe()
    elif action == 'remove_fe_observer_from_cluster':
        removeFe("OBSERVER")
    else:
        raise Exception("unknown command type: :{action}")


# 启动或添加 Fe Follower,首次初始化集群默认第一台Follower为Master节点
def fe_follower_start():
    import utils, params, status_params
    if os.path.exists(status_params.doris_fe_pid_file):
        Execute('rm -rf {0}'.format(status_params.doris_fe_pid_file), user=params.operator)
    if os.path.exists('{0}/fe.pid'.format(params.doris_fe_bin_path)):
        Execute('rm -rf {0}/fe.pid'.format(params.doris_fe_bin_path), user=params.operator)
    killProcess("Fe", "org.apache.doris.DorisFE")

    # judy flag file
    doris_fe_flag = '{0}/fe.flag'.format(params.doris_fe_bin_path)
    if not os.path.exists(doris_fe_flag):
        host = utils.find_available_host()
        if host == '':
            if str(params.doris_fe_hosts_list).startswith(params.hostIpAddress) or str(
                    params.doris_fe_hosts_list).startswith(params.hostname):
                # leader_fe_host = utils.get_master_host(host)
                Logger.info('{0} is default master'.format(params.hostIpAddress))
                Execute('{0}/start_fe.sh --daemon'.format(params.doris_fe_bin_path),
                        user=params.operator)
                time.sleep(30)
                # create flag
                File(os.path.join(params.doris_fe_bin_path, 'fe.flag'),
                     owner=params.operator,
                     group=params.operatorGroup,
                     content=params.hostIpAddress
                     )
            else:
                Logger.info('Wait fe follower master start...')
                # 首次创建集群,其他的Follower节点等待Follower Master节点启动成功,随后加入该集群
                time.sleep(180)
                addFe()
        else:
            addFe()
    else:
        Execute('{0}/start_fe.sh --daemon'.format(params.doris_fe_bin_path),
                user=params.operator)
    time.sleep(30)
    checkDorisActualRunningStatus("fe follower",
                                  "org.apache.doris.DorisFE",
                                  status_params.doris_fe_pid_file,
                                  "fe.pid",
                                  params.doris_fe_bin_path)

    time.sleep(30)
    # 修改FE的Root用户密码(如果发生修改的话)
    Logger.info("Check whether the password needs to be changed...")
    new_password = str(params.fe_root_password).strip()
    host = utils.find_available_host()
    if host != '':
        leader_fe_host = utils.get_master_host(host)
        if not os.path.exists(params.DORIS_FE_CONFIG_ROOT_PASSWD_FILE):
            utils.change_root_password(leader_fe_host, '', new_password)
        else:
            old_password = commands.getoutput("cat {0}".format(params.DORIS_FE_CONFIG_ROOT_PASSWD_FILE)).strip()
            if old_password != new_password:
                utils.change_root_password(leader_fe_host, old_password, new_password)
    else:
        raise Exception("Error,No FE node is alive")


# 启动或添加 Fe Observer
def fe_observer_start():
    import utils, params, status_params
    if not os.path.exists(status_params.doris_fe_pid_file) or os.path.exists(status_params.doris_fe_pid_file):
        Execute('rm -rf {0}'.format(status_params.doris_fe_pid_file), user=params.operator)
    if os.path.exists('{0}/fe.pid'.format(params.doris_fe_bin_path)):
        Execute('rm -rf {0}/fe.pid'.format(params.doris_fe_bin_path), user=params.operator)
    killProcess("Fe", "org.apache.doris.DorisFE")

    # judy flag file
    doris_fe_flag = '{0}/fe.flag'.format(params.doris_fe_bin_path)
    host = utils.find_available_host()
    if host != '' and not os.path.exists(doris_fe_flag):
        addFe('OBSERVER')
    else:
        Execute('{0}/start_fe.sh --daemon'.format(params.doris_fe_bin_path), user=params.operator)
    time.sleep(30)
    checkDorisActualRunningStatus("fe observer",
                                  "org.apache.doris.DorisFE",
                                  status_params.doris_fe_pid_file,
                                  "fe.pid",
                                  params.doris_fe_bin_path)


# 启动或添加 Broker
def broker_start():
    import params, status_params
    Execute('rm -rf {0}'.format(status_params.doris_broker_pid_file), user=params.operator)
    Execute('rm -rf {0}/apache_hdfs_broker.pid'.format(params.doris_broker_bin_path),
            user=params.operator)
    killProcess("Broker", "org.apache.doris.broker.hdfs.BrokerBootstrap")

    Execute('{0}/start_broker.sh --daemon'.format(params.doris_broker_bin_path),
            user=params.operator)
    time.sleep(10)

    checkDorisActualRunningStatus("broker",
                                  "org.apache.doris.broker.hdfs.BrokerBootstrap",
                                  status_params.doris_broker_pid_file,
                                  "apache_hdfs_broker.pid",
                                  params.doris_broker_bin_path)

    # judy flag file
    doris_broker_flag = '{0}/broker.flag'.format(params.doris_broker_bin_path)
    if not os.path.exists(doris_broker_flag):
        addBroker()


# 启动或添加 Backend
def be_start():
    import params, status_params
    # start be
    Execute('rm -rf {0}'.format(status_params.doris_be_pid_file), user=params.operator)
    Execute('rm -rf {0}/be.pid'.format(params.doris_be_bin_path),
            user=params.operator)
    killProcess("Backend", "doris_be")
    # Start Doris BE Server
    max_map_count = commands.getoutput("sysctl vm.max_map_count | awk '{print $3}'").strip()
    if int(max_map_count) < 2000000:
        Execute('sysctl -w vm.max_map_count=2000000', user=params.operator)
    Execute('swapoff -a ', user=params.operator)
    Execute('{0}/start_be.sh --daemon'.format(params.doris_be_bin_path), user=params.operator)
    time.sleep(10)

    checkDorisActualRunningStatus("be",
                                  "doris_be",
                                  status_params.doris_be_pid_file,
                                  "be.pid",
                                  params.doris_be_bin_path)

    # judy flag file
    doris_be_flag = '{0}/be.flag'.format(params.doris_be_bin_path)
    if not os.path.exists(doris_be_flag):
        addBe()


# 添加 Fe(follower/observer),并指定--helper参数启动fe进程
def addFe(role='FOLLOWER'):
    import params
    addDorisService("FE {0}".format(role), role, params.fe_edit_log_port, params.doris_fe_bin_path, 'fe.flag')


# 添加 Backend
def addBe():
    import params
    addDorisService("BACKEND", "BACKEND", params.be_heartbeat_service_port, params.doris_be_bin_path, 'be.flag')


# 添加 Broker
def addBroker():
    import params
    addDorisService("BROKER", "BROKER hdfs_broker", params.broker_broker_ipc_port, params.doris_broker_bin_path,
                    'broker.flag')


# 删除 Broker
def removeBroker():
    import params
    removeDorisService("Broker", "BROKER hdfs_broker", params.broker_broker_ipc_port)


# 安全删除(DECOMMISSION) Backend,执行该动作后,该BE上节点数据会进行迁移,迁移完毕后自动删除
def removeBe():
    import params
    removeDorisService("Backend", "BACKEND", params.be_heartbeat_service_port)


# 删除 Fe(follower/observer)节点,目前暂不开放删除Fe Follower功能
def removeFe(role="FOLLOWER"):
    import params
    removeDorisService("FE {0}".format(role), role, params.fe_edit_log_port)


# 添加Doris服务(FE/BE/BROKER)
def addDorisService(name, role, port, binPath, flagFile):
    import utils, params
    host = utils.find_available_host()
    if host != '':
        if os.path.exists("{0}/{1}".format(binPath, flagFile)):
            Logger.warning("This service is already in the Doris cluster and does not need to be added again")
        else:
            leader_fe_host = utils.get_master_host(host)
            if role == 'FOLLOWER' or role == 'OBSERVER':
                Execute(
                    '{0}/start_fe.sh --helper {1}:{2} --daemon'.format(params.doris_fe_bin_path, leader_fe_host,
                                                                       params.fe_edit_log_port),
                    user=params.operator)
            try:
                utils.add_service(leader_fe_host, port, role)
            except Exception as exception:
                raise Exception("There was an exception when ALTER SYSTEM ADD {0}: ".format(name) + str(exception))
            # create flag
            File(os.path.join(binPath, flagFile),
                 owner=params.operator,
                 group=params.operatorGroup,
                 content=params.hostIpAddress
                 )
    else:
        raise Exception("Add {0} Fail,No FE node is alive".format(name))


# 删除Doris服务(FE/BE/BROKER)
def removeDorisService(name, role, port):
    import utils
    host = utils.find_available_host()
    if host != '':
        leader_fe_host = utils.get_master_host(host)
        try:
            utils.remove_service(leader_fe_host, port, role)
        except Exception as exception:
            raise Exception("There was an exception when ALTER SYSTEM REMOVE {0}: ".format(name) + str(exception))
    else:
        raise Exception("Remove {0} Fail,No FE node is alive".format(name))


# 停止服务公共方法
def stopService(serviceName, binPath, pidFileName, pidFilePath, scriptName, processFullName='org.apache.doris.DorisFE'):
    import utils, params
    if os.path.exists(pidFilePath) and sudo.read_file(pidFilePath) != '':
        Execute("cat {0} > {1}/{2}".format(pidFilePath, binPath, pidFileName), user=params.operator)
    pidfile = "{0}/{1}".format(binPath, pidFileName)
    if os.path.exists(pidfile) and utils.check_process_exists(pidfile):
        Execute('{0}/{1}'.format(binPath, scriptName), user=params.operator)
    Execute("rm -rf {0}".format(pidFilePath),
            user=params.operator)
    killProcess(serviceName, processFullName)
    Logger.info('Doris {0} Stop.'.format(serviceName))


# 检查服务是否真正运行,并生成对应pid文件
def checkDorisActualRunningStatus(serviceName, processFullName, pidFilePath, pidFileName, binPath):
    import params

    tryTimes = 5
    while (tryTimes > 0):
        Execute(
            "ps -ef | grep {0} | grep -v grep | awk '{{print $2}}' > {1}".format(processFullName, pidFilePath),
            user=params.operator)
        if (sudo.read_file(pidFilePath) != ''):
            break
        else:
            if os.path.exists("{0}/{1}".format(binPath, pidFileName)):
                Execute("cat {0}/{1} > {2} ".format(binPath, pidFileName, pidFilePath), user=params.operator)
            Logger.info('waiting from {0} start...'.format(serviceName))
            time.sleep(30)
            tryTimes = tryTimes - 1
    if (tryTimes == 0):
        Logger.error('start {0} error,pls check logs.'.format(serviceName))
        killProcess(serviceName, processFullName)
        raise Exception("{0} 服务启动失败或无法正常使用，请检查日志".format(serviceName))
    else:
        Logger.info('doris {0} start.'.format(serviceName))


# 根据服务名称杀掉进程
def killProcess(serviceName, processFullName):
    import params
    try:
        # kill process
        Execute("kill -9 $(ps -ef | grep {0} | grep -v grep | awk '{{print $2}}')".format(processFullName),
                user=params.operator)
    except Exception as exception:
        Logger.debug('kill [${0}] process fail,Msg:{1}'.format(serviceName, exception))

# -*- coding: utf-8 -*-
import commands, grp, pwd, os
from resource_management import *
from resource_management import User, Group, Logger
from resource_management.core.resources.system import Execute


# 检查端口是否可用
def is_port_alive(host, port):
    cmd = "echo -e 'quit' | telnet {0} {1}".format(host, port)
    # result = os.popen(cmd).read().strip()
    result = commands.getoutput(cmd)
    Logger.info("exec cmd:{0}".format(cmd))
    Logger.info("telnet result:{0}".format(result))
    return "Connected" in result


# 寻找正常可用的Doris Fe节点
def find_available_host():
    import params
    hosts = params.doris_fe_hosts_list.split(',')
    availableHost = ''
    for host in hosts:
        host = host.strip()
        flag = is_port_alive(host, params.fe_query_port)
        if flag:
            availableHost = host
            break
    return availableHost


# 获取Doris Fe Follower Master 主机IP地址
def get_master_host(host):
    import params
    # host = find_available_host
    port = params.fe_query_port
    user = 'root'
    password = params.fe_root_password

    leader_ip = commands.getoutput(
        "mysql -h {0} -P {1} -u {2} -p{3} -e \"SHOW FRONTENDS;\" | awk '$8==\"true\" {{print $2}}'".format(host,
                                                                                                           port,
                                                                                                           user,
                                                                                                           password))
    if len(leader_ip) >= 15:
        return commands.getoutput(
            "mysql -h {0} -P {1} -u {2} -e \"SHOW FRONTENDS;\" | awk '$8==\"true\" {{print $2}}'".format(host, port,
                                                                                                         user))
    else:
        return leader_ip


# 检查关键性目录是否存在，role=[fe,be,broker]
def checkDir(role=''):
    import params
    import status_params

    Execute('chown -R {0}:{1} {2}'.format(params.operator, params.operatorGroup, params.doris_home_dir),
            user='root')

    if role == 'fe':
        dirs = [
            params.fe_meta_dir,
            params.fe_log_default_dir,
            params.fe_sys_log_dir,
            params.fe_temp_dir
        ]
    elif role == 'be':
        dirs = [params.be_log_default_dir,
                params.be_sys_log_dir,
                params.BE_PPROF_TMPDIR]
        for i in params.be_storage_root_path.split(';'):
            dirs.append(i.split(',')[0].strip())
        dirs = [i for i in dirs if i != '']
    else:
        dirs = [params.broker_sys_log_dir]

    dirs.append(status_params.doris_pid_dir)

    Directory(dirs,
              owner=params.operator,
              create_parents=True,
              group=params.operatorGroup
              )


# 添加服务到Doris集群,role=[FOLLOWER,OBSERVER,BACKEND,BROKER]
def add_service(masterIp, port, role):
    add_or_remove_service(masterIp, port, role, "ADD")


# 从Doris集群删除服务,如果是BE,进行安全删除(数据迁移完毕后自动删除)
def remove_service(masterIp, port, role):
    action = 'DROP'
    if role == "BACKEND":
        action = 'DECOMMISSION'
    add_or_remove_service(masterIp, port, role, action)


# 添加或者删除服务(从Doris集群)
def add_or_remove_service(masterIp, port, role, action):
    import params
    password = params.fe_root_password  # commands.getoutput("cat {0}".format(params.DORIS_FE_CONFIG_ROOT_PASSWD_FILE)).strip()
    localIp = commands.getoutput("hostname -i").strip()
    cmd = "mysql -uroot -p{0} -h {1} -P {2} -e \"ALTER SYSTEM {3} {4} \'{5}:{6}\'\"".format(
        password, masterIp, params.fe_query_port, action, role, localIp, port)
    Logger.info("{0} Doris {1} Server, command is {2}.".format(action, role, cmd))
    Execute(cmd, user=params.doris_user, logoutput=True, tries=5, try_sleep=5)


# 修改Doris Root用户密码
def change_root_password(fe_leader_ip, old_password, new_password):
    import params
    cmd_no_password = format("mysql -uroot -h {fe_leader_ip} -P {fe_query_port} "
                             "-e \"SET PASSWORD FOR \'root\' = PASSWORD(\'{new_password}\') \" ")
    cmd_has_password = format("mysql -uroot -p{old_password} -h {fe_leader_ip} -P {fe_query_port} "
                              "-e \"SET PASSWORD FOR \'root\' = PASSWORD(\'{new_password}\') \" ")
    try:
        if old_password == '':
            Logger.info("Add Doris Server password, commonds is {0}.".format(cmd_no_password))
            Execute(cmd_no_password, user=params.operator, logoutput=True, tries=5, try_sleep=3)
        else:
            Logger.info("Changed Doris Server password, commonds is {0}.".format(cmd_has_password))
            Execute(cmd_has_password, user=params.operator, logoutput=True, ignore_failures=True, tries=5, try_sleep=3)
    except:
        Logger.warning("change password failed")
    Execute('echo {0} > {1}'.format(params.fe_root_password, params.DORIS_FE_CONFIG_ROOT_PASSWD_FILE),
            user=params.operator)


# 检查进程是否存在
def check_process_exists(pid_file):
    from resource_management.core import sudo
    if not pid_file or not os.path.isfile(pid_file):
        Logger.info("Pid file {0} is empty or does not exist".format(str(pid_file)))
        raise ComponentIsNotRunning()

    try:
        pid = int(sudo.read_file(pid_file))
    except:
        Logger.info("Pid file {0} does not exist or does not contain a process id number".format(pid_file))
        raise ComponentIsNotRunning()

    try:
        sudo.kill(pid, 0)
        return True
    except OSError:
        Logger.info("Process with pid {0} is not running. Stale pid file"
                    " at {1}".format(pid, pid_file))
        return False


# 自定义配置
def customConf(path, dic):
    dic_copy = dic.copy()
    with open(path, "r+") as fr:
        lines = fr.readlines()
        for line in lines:
            for key in dic:
                if line.startswith(key):
                    del dic_copy[key]

    with open(path, "a+") as fw:
        fw.write("\n#==================================== doris custom config ====================================\n")
        for key in dic_copy:
            line = (key + "=" + dic_copy[key] + "\n")
            fw.write(line)


# 创建Doris用户和用户组
def createUserIfNotExist():
    import params
    try:
        grp.getgrnam(params.doris_group)
    except KeyError:
        Group(params.doris_group, group_name=params.doris_group)

    try:
        pwd.getpwnam(params.doris_user)
    except Exception:
        Logger.info("User: %s not existed, create it" % params.doris_user)
        User(params.doris_user, username=params.doris_user,
             gid=params.doris_group,
             groups=[params.doris_group], ignore_failures=True)
        Logger.info("User: %s create successful" % params.doris_user)


# 安装前执行的动作
def installDependency():
    # install doris client，telnet tools
    Execute('yum install -y mariadb mysql telnet', user='root', ignore_failures=True)

    # create doris user and group
    createUserIfNotExist()

# -*- coding: utf-8 -*-
import os

from resource_management import *


class FE_OBSERVER(Script):
    def install(self, env):
        import params, utils
        env.set_params(params)
        fe_observer_ip = params.hostIpAddress
        # 检查该节点是否存在Fe Follower服务，Follower不能和Observer安装在一台机器上
        Logger.info(fe_observer_ip)
        print(params.doris_fe_hosts_list)
        if len(params.doris_fe_hosts_list) > 0 and (fe_observer_ip in params.doris_fe_hosts_list or params.hostname in params.doris_fe_hosts_list):
            Logger.info('FE OBSERVER can not install with FE in the same host !')
            raise Exception('FE OBSERVER can not install with FE in the same host !')
        else:
            utils.installDependency()
            self.install_packages(env)
            self.configure(env)
            Logger.info('install doris fe observer server successfully!')

    def configure(self, env, isInstall=False):
        import params, status_params, utils
        env.set_params(params)
        env.set_params(status_params)

        utils.checkDir("fe")

        if not os.path.exists(params.doris_fe_conf_dir):
            Execute('ln -s /etc/doris/fe/conf {0}'.format(params.doris_fe_conf_dir), user=params.operator)

        # fe.conf
        fe_conf_configurations = params.config['configurations']['doris-fe.conf']
        File(format(params.DORIS_FE_CONFIG_FILE),
             content=Template("fe.conf.j2",
                              configurations=fe_conf_configurations),
             owner=params.operator,
             group=params.operatorGroup
             )
        utils.customConf(format(params.DORIS_FE_CONFIG_FILE), fe_conf_configurations)

        # ldap.conf
        fe_ldap_conf_content = InlineTemplate(params.fe_ldap_conf_content)
        File(params.DORIS_FE_LDAP_CONFIG_FILE, content=fe_ldap_conf_content, owner=params.operator)

        Logger.info('configure doris fe server successfully!')

    def stop(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='fe_observer_stop')
        Logger.info('doris fe server stop successfully!')

    def start(self, env):
        import params, common
        fe_observer_ip = params.hostIpAddress
        Logger.info(fe_observer_ip)
        print(params.doris_fe_hosts_list)
        if len(params.doris_fe_hosts_list) > 0 and (fe_observer_ip in params.doris_fe_hosts_list or params.hostname in params.doris_fe_hosts_list):
            Logger.info('FE OBSERVER can not install with FE in the same host !')
            raise Exception('FE OBSERVER can not install with FE in the same host !')

        self.configure(env)
        env.set_params(params)
        common.doris_service(action='fe_observer_start')
        Logger.info('doris fe server observer start successfully!')

    def status(self, env):
        import status_params
        check_process_status(status_params.doris_fe_pid_file)

    def remove(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='add_fe_observer_to_cluster')
        Logger.info('doris fe observer remove finished!')

    def readd(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='remove_fe_observer_from_cluster')
        Logger.info('doris fe observer add operateion finished!')

if __name__ == "__main__":
    FE_OBSERVER().execute()

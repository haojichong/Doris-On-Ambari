# -*- coding: utf-8 -*-
import os

from resource_management import *


class Broker(Script):
    def install(self, env):
        import params, utils
        env.set_params(params)
        utils.installDependency()
        self.install_packages(env)
        # 首次安装，清除默认的配置模板
        Execute('rm -rf {0}/hdfs-site.xml'.format(params.doris_broker_conf_dir), user=params.operator)
        self.configure(env)
        Logger.info('install doris be server successfully!')

    def configure(self, env, isInstall=False):
        import params, status_params, utils
        env.set_params(params)
        env.set_params(status_params)
        utils.checkDir("broker")

        if not os.path.exists(params.doris_broker_conf_dir):
            Execute('ln -s /etc/doris/broker/conf {0}'.format(params.doris_broker_conf_dir), user=params.operator)

        # broker.conf
        broker_configurations = params.config['configurations']['doris-broker.conf']
        File(format(params.DORIS_BROKER_CONFIG_FILE),
             content=Template("broker.conf.j2",
                              configurations=broker_configurations),
             owner=params.operator,
             group=params.operatorGroup
             )
        utils.customConf(format(params.DORIS_BROKER_CONFIG_FILE), broker_configurations)

        # ln hdfs-site.xml to broker conf dir
        if os.path.exists(params.broker_hdfs_site_file_path) and not os.path.exists(
                '{0}/hdfs-site.xml'.format(params.doris_broker_conf_dir)):
            Execute('ln -s {0} {1}'.format(params.broker_hdfs_site_file_path, params.doris_broker_conf_dir),
                    user=params.operator)

        # log4j.properties
        log4j_properties_content = InlineTemplate(params.broker_log4j_prop_content)
        File(format(params.DORIS_BROKER_LOG4J_CONFIG_FILE), content=log4j_properties_content,
             owner=params.operator)

        Logger.info('configure doris broker server successfully!')

    def start(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='broker_start')
        Logger.info('start doris broker server start successfully!')

    def stop(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='broker_stop')
        Logger.info('start doris broker server stop successfully!')

    def status(self, env):
        import status_params
        check_process_status(status_params.doris_broker_pid_file)


    def remove(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='remove_broker_from_cluster')
        Logger.info('doris broker remove finished!')

    def readd(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='add_broker_to_cluster')
        Logger.info('doris broker add operateion finished!')

if __name__ == "__main__":
    Broker().execute()

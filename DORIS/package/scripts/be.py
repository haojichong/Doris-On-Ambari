# -*- coding: utf-8 -*-
import os
from resource_management import *


class BE(Script):
    def install(self, env):
        import params, utils
        env.set_params(params)
        utils.installDependency()
        self.install_packages(env)
        self.configure(env)
        Logger.info('install doris be server successfully!')

    def configure(self, env, isInstall=False):
        import params, status_params, utils
        env.set_params(params)
        env.set_params(status_params)

        utils.checkDir("be")
        if not os.path.exists(params.doris_be_conf_dir):
            Execute('ln -s /etc/doris/be/conf {0}'.format(params.doris_be_conf_dir), user=params.operator)

        # be.conf
        be_conf_configurations = params.config['configurations']['doris-be.conf']
        File(format(params.DORIS_BE_CONFIG_FILE),
             content=Template("be.conf.j2",
                              configurations=be_conf_configurations),
             owner=params.operator,
             group=params.operatorGroup
             )
        utils.customConf(format(params.DORIS_BE_CONFIG_FILE), be_conf_configurations)

        # asan_suppr.conf
        asan_suppr_conf_content = InlineTemplate(params.asan_suppr_conf_content)
        File(params.DORIS_BE_ASAN_SUPPR_CONFIG_FILE, content=asan_suppr_conf_content, owner=params.operator)

        # lsan_suppr.conf
        lsan_suppr_conf_content = InlineTemplate(params.lsan_suppr_conf_content)
        File(params.DORIS_BE_LSAN_SUPPR_CONFIG_FILE, content=lsan_suppr_conf_content, owner=params.operator)

        # odbcinst.ini
        odbcinst_ini_content = InlineTemplate(params.odbcinst_ini_content)
        File(params.DORIS_BE_ODBCINST_INI_CONFIG_FILE, content=odbcinst_ini_content, owner=params.operator)
        Logger.info('configure doris be server successfully!')

    def stop(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='be_stop')
        Logger.info('doris be server stop successfully!')

    def start(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='be_start')
        Logger.info('doris be server start successfully!')

    def status(self, env):
        import status_params
        check_process_status(status_params.doris_be_pid_file)

    def decommission(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='decommission_be_from_cluster')
        Logger.info('doris be decommission finished!')

    def readd(self, env):
        import params, common
        self.configure(env)
        env.set_params(params)
        common.doris_service(action='add_be_to_cluster')
        Logger.info('doris be add operateion finished!')


if __name__ == "__main__":
    BE().execute()

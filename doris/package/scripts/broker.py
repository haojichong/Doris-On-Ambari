import time

import grp
import pwd
import os

from resource_management import *


class Broker(Script):
    def install(self, env):
        import params, status_params

        try:
            grp.getgrnam(params.doris_group)
        except KeyError:
            Group("doris", group_name=params.doris_group)

        try:
            pwd.getpwnam(params.doris_user)
        except Exception:
            Logger.info("User: %s not existed, create it" % params.doris_user)
            User("doris", username=params.doris_user,
                 gid=params.doris_group,
                 groups=[params.doris_group], ignore_failures=True)
            Logger.info("User: %s create successful" % params.doris_user)
        Directory([params.doris_install_path,
                   status_params.doris_pid_dir,
                   params.doris_downloaded_path],
                  owner=params.doris_user,
                  group=params.doris_group,
                  create_parents=True
                  )
        if not os.path.exists('{0}/broker'.format(params.doris_install_path)):
            Execute('cd {0};wget {1} -O doris.tar.gz'.format(params.doris_downloaded_path, params.doris_download),
                    user=params.doris_user)
            Execute('cd {0};tar -xf doris.tar.gz --strip-components=1'.format(params.doris_downloaded_path),
                    user=params.doris_user)
            Execute('cp -r {0}/apache_hdfs_broker {1}'.format(params.doris_downloaded_path, params.doris_install_path),
                    user=params.doris_user)
            Execute('mv {0}/apache_hdfs_broker {1}/broker'.format(params.doris_install_path, params.doris_install_path),
                    user=params.doris_user)
            Execute('chmod +x {0}/*.sh'.format(params.doris_broker_bin_path),
                    user=params.doris_user)
            Execute('rm -rf {0}'.format(params.doris_downloaded_path),
                    user="root")
        self.configure(env, True)

    def configure(self, env, isInstall=False):
        import params
        import status_params
        import common
        env.set_params(params)
        env.set_params(status_params)
        configurations = params.config['configurations']['broker.conf']
        File(format(params.doris_broker_conf_dir),
             content=Template("broker.conf.j2",
                              configurations=configurations),
             owner=params.doris_user,
             group=params.doris_group
             )
        common.customConf(format(params.doris_broker_conf_dir), configurations)

    def start(self, env):
        import params, status_params
        self.configure(env)
        Execute('rm -rf {0}'.format(status_params.doris_broker_pid_file), user=params.doris_user)
        Execute('rm -rf {0}/apache_hdfs_broker.pid'.format(params.doris_broker_bin_path),
                user=params.doris_user)
        Execute('{0}/start_broker.sh --daemon'.format(params.doris_broker_bin_path),
                user=params.doris_user)
        time.sleep(4)
        Execute(
            "ps -ef | grep org.apache.doris.broker.hdfs.BrokerBootstrap | grep -v grep | cut -c 9-15 > {0}".format(
                status_params.doris_broker_pid_file),
            user=params.doris_user)
        time.sleep(1)
        Execute("cat {0} > {1}/apache_hdfs_broker.pid".format(
            status_params.doris_broker_pid_file, params.doris_broker_bin_path),
            user=params.doris_user)


    def stop(self, env):
        import params, status_params
        self.configure(env)
        Execute("cat {0} > {1}/apache_hdfs_broker.pid".format(
            status_params.doris_broker_pid_file, params.doris_broker_bin_path),
            user=params.doris_user)
        Execute('{0}/stop_broker.sh'.format(params.doris_broker_bin_path),
                user=params.doris_user)
        Execute('rm -rf {0}/apache_hdfs_broker.pid'.format(params.doris_broker_bin_path),
                user=params.doris_user)
        Execute('rm -rf {0}'.format(status_params.doris_broker_pid_file),
                user=params.doris_user)


    def status(self, env):
        import status_params
        check_process_status(status_params.doris_broker_pid_file)


if __name__ == "__main__":
    Broker().execute()

import time

import grp
import pwd
import os

from resource_management import *


class Palo_Studio(Script):
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
        Directory([status_params.doris_pid_dir,
                   params.palo_log_dir,
                   params.palo_install_path,
                   params.palo_downloaded_path
                   ],
                  owner=params.doris_user,
                  group=params.doris_group,
                  create_parents=True
                  )
        if not os.path.exists('{0}/conf'.format(params.palo_install_path)):
            Execute('cd {0};wget {1} -O palo_studio.tar.gz'.format(params.palo_downloaded_path, params.palo_download),
                    user=params.doris_user)
            Execute('cd {0};tar -xf palo_studio.tar.gz --strip-components=1'.format(params.palo_downloaded_path),
                    user=params.doris_user)
            Execute('cp -r {0}/* {1}'.format(params.palo_downloaded_path, params.palo_install_path),
                    user=params.doris_user)
            Execute('rm -rf {0}/palo_studio.tar.gz'.format(params.palo_install_path),
                    user="root")
            Execute('rm -rf {0}'.format(params.palo_downloaded_path),
                    user="root")
        self.configure(env, True)

    def configure(self, env, isInstall=False):
        import params
        import status_params
        import common
        env.set_params(params)
        env.set_params(status_params)
        configurations = params.config['configurations']['studio.conf']
        File(format(params.palo_conf_file_path),
             content=Template("palo-studio.conf.j2",
                              configurations=configurations),
             owner=params.doris_user,
             group=params.doris_user
             )
        common.customConf(format(params.palo_conf_file_path), configurations)

    def start(self, env):
        import params
        import status_params
        self.configure(env)
        Execute("rm -rf {0}".format(status_params.palo_studio_pid_file), user=params.doris_user)
        Execute('cd {0};nohup sh {0}/start.sh > {1}/start.log 2>&1 &'.format(params.palo_bin_path, params.palo_log_dir),
                user=params.doris_user)
        Execute('cd {0};sh {0}/prometheus/start_prometheus.sh'.format(params.palo_bin_path, params.palo_log_dir),
                user=params.doris_user)
        time.sleep(5)
        Execute(
            "ps -ef | grep studio-server | grep -v grep | cut -c 9-15 > {0}".format(status_params.palo_studio_pid_file),
            user=params.doris_user)

    def stop(self, env):
        import params
        import status_params
        self.configure(env)
        Execute('ps -ef | grep studio-server | grep -v grep | cut -c 9-15 | xargs kill -9', user=params.doris_user)
        Execute('ps -ef | grep {0}/prometheus | grep -v grep | cut -c 9-15 | xargs kill -9'.format(
            params.palo_install_path), user=params.doris_user)
        # Execute('sh {0}/prometheus/stop_prometheus.sh'.format(params.palo_bin_path), user=params.doris_user)
        Execute('rm -rf {0}'.format(status_params.palo_studio_pid_file), user=params.doris_user)

    def status(self, env):
        import status_params
        check_process_status(status_params.palo_studio_pid_file)


if __name__ == "__main__":
    Palo_Studio().execute()

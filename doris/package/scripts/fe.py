import time

import grp
import pwd
import os

from resource_management import *


class FE(Script):
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
                   params.fe_meta_dir,
                   params.doris_downloaded_path],
                  owner=params.doris_user,
                  group=params.doris_group,
                  create_parents=True
                  )

        if not os.path.exists('{0}/fe'.format(params.doris_install_path)):
            Execute('cd {0};wget {1} -O doris.tar.gz'.format(params.doris_downloaded_path, params.doris_download),
                    user=params.doris_user)
            Execute('cd {0};tar -xf doris.tar.gz --strip-components=1'.format(params.doris_downloaded_path),
                    user=params.doris_user)
            Execute('cp -r {0}/fe {1}'.format(params.doris_downloaded_path, params.doris_install_path),
                    user=params.doris_user)
            # if not os.path.exists('{0}/fe/doris-meta'.format(params.doris_install_path)):
            #     Execute('mkdir -p {0}/fe/doris-meta'.format(params.doris_install_path),
            #             user=params.doris_user)
            Execute('rm -rf {0}'.format(params.doris_downloaded_path),
                    user="root")
        self.configure(env, True)

    def configure(self, env, isInstall=False):
        import params
        import status_params
        import common
        env.set_params(params)
        env.set_params(status_params)
        configurations = params.config['configurations']['fe.conf']
        File(format(params.doris_fe_conf_dir),
             content=Template("fe.conf.j2",
                              configurations=configurations),
             owner=params.doris_user,
             group=params.doris_group
             )
        common.customConf(format(params.doris_fe_conf_dir), configurations)

    def stop(self, env):
        import params, status_params
        self.configure(env)
        Execute("cat {0} > {1}/fe.pid".format(
            status_params.doris_fe_pid_file,params.doris_fe_bin_path),
            user=params.doris_user)
        Execute('{0}/stop_fe.sh'.format(params.doris_fe_bin_path),
                user=params.doris_user)
        Execute('rm -rf {0}/fe.pid'.format(params.doris_fe_bin_path),
                user=params.doris_user)
        Execute("rm -rf {0}".format(status_params.doris_fe_pid_file),
                user=params.doris_user)

    def start(self, env):
        import params, status_params
        self.configure(env)
        if not os.path.exists(params.fe_meta_dir):
            Execute("mkdir -p {0}".format(params.fe_meta_dir), user=params.doris_user)
            Execute("chown -R {0}:{1} {2}".format(params.doris_user,params.doris_group,params.fe_meta_dir), user=params.doris_user)

        Execute('rm -rf {0}'.format(status_params.doris_fe_pid_file), user=params.doris_user)
        Execute('rm -rf {0}/fe.pid'.format(params.doris_fe_bin_path),
                user=params.doris_user)
        Execute('{0}/start_fe.sh --daemon'.format(params.doris_fe_bin_path),
                user=params.doris_user)
        time.sleep(4)
        Execute("ps -ef | grep org.apache.doris.PaloFe | grep -v grep | cut -c 9-15 > {0}".format(
            status_params.doris_fe_pid_file),
            user=params.doris_user)
        time.sleep(1)
        Execute("cat {0} > {1}/fe.pid".format(
            status_params.doris_fe_pid_file,params.doris_fe_bin_path),
            user=params.doris_user)

    def status(self, env):
        import status_params
        check_process_status(status_params.doris_fe_pid_file)

    # [Experimental Feature]
    def fe_upgrade(self, env):
        import params, status_params
        if os.path.exists(status_params.doris_fe_pid_file):
            raise Exception("Server is running, please stop it first.")
        else:
            # Minor version upgrade Only update for lib/palo-fe.jar package
            # Major version upgrades need to update multiple directories
            Execute('rm -rf {0}/tmp_doris_upgrade'.format(params.doris_install_path),
                    user=params.doris_user)
            Execute('mkdir -p {0}/tmp_doris_upgrade'.format(params.doris_install_path),
                    user=params.doris_user)
            Execute('cd {0}/tmp_doris_upgrade;wget {1} -O doris.tar.gz'.format(params.doris_install_path,
                                                                               params.doris_download),
                    user=params.doris_user)
            Execute(
                'cd {0}/tmp_doris_upgrade;tar -xf doris.tar.gz --strip-components=1'.format(params.doris_install_path),
                user=params.doris_user)
            # if int(params.upgrade_option()) == 0:
            #     Execute('mv -f {0}/tmp_doris_upgrade/fe/lib/palo-fe.jar {0}/fe/lib/'.format(params.doris_install_path),
            #             user=params.doris_user)
            # else:
            time.sleep(3)
            Execute('rm -rf {0}/fe/bin/*'.format(params.doris_install_path),
                    user=params.doris_user)
            Execute('mv -f {0}/tmp_doris_upgrade/fe/bin/* {0}/fe/bin'.format(params.doris_install_path),
                    user=params.doris_user)
            Execute('rm -rf {0}/fe/lib/*'.format(params.doris_install_path),
                    user=params.doris_user)
            Execute('mv -f {0}/tmp_doris_upgrade/fe/lib/* {0}/fe/lib'.format(params.doris_install_path),
                    user=params.doris_user)
            Execute('rm -rf {0}/fe/spark-dpp/*'.format(params.doris_install_path),
                    user=params.doris_user)
            Execute('mv -f {0}/tmp_doris_upgrade/fe/spark-dpp/* {0}/fe/spark-dpp'.format(params.doris_install_path),
                    user=params.doris_user)
            Execute('rm -rf {0}/fe/webroot/*'.format(params.doris_install_path),
                    user=params.doris_user)
            Execute('mv -f {0}/tmp_doris_upgrade/fe/webroot/* {0}/fe/webroot'.format(params.doris_install_path),
                    user=params.doris_user)
            Execute("chown -R {0}:{1} {2}".format(params.doris_user,params.doris_group,params.doris_install_path), user=params.doris_user)
            Execute('rm -rf {0}/tmp_doris_upgrade'.format(params.doris_install_path),
                    user=params.doris_user)


if __name__ == "__main__":
    FE().execute()

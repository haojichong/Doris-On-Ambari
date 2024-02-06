# -*- coding: utf-8 -*-
from resource_management import *
import commands, random

# 验证集群是否可用
# 1.连接Doris集群创建库和表
# 2.创建库和表
# 3.生成测试数据
# 4.Count查询输出结果
def testDorisClusterUsability():
    import utils, params
    Logger.info("ready to start creating temporary tables to check the doris service availability")
    host = utils.find_available_host()
    master_ip = utils.get_master_host(host)
    if master_ip == '':
        raise Exception("Service check failed,error msg：Description Failed to obtain the FE Master node")
    password = params.fe_root_password
    randomId = random.randint(1, 10000)
    connectDoris = "mysql -uroot -p{0} -h {1} -P {2} -e ".format(password, master_ip, params.fe_query_port)
    createDatabaseCmd = "{0} \"CREATE DATABASE IF NOT EXISTS test;\"".format(connectDoris)
    createTableCmd = "{0} \"CREATE TABLE IF NOT EXISTS test.test (\`id\` BIGINT, \`data\` VARCHAR(1024)) DUPLICATE KEY(\`id\`) DISTRIBUTED BY HASH(id) BUCKETS 10 PROPERTIES('replication_num' = '1');\"".format(
        connectDoris)
    insertDataCmd = "{0} \"insert into test.test values({1},'test_data_{1}');\"".format(connectDoris, randomId)
    enableProfileCmd = "{0} \"set global enable_profile=true;\"".format(connectDoris, randomId)
    countTableCmd = "{0} \"select count(1) from test.test;\"".format(connectDoris)
    Execute(enableProfileCmd, user=params.operator, logoutput=False, tries=5, try_sleep=5)
    Logger.info("Run the create database command: 'CREATE DATABASE IF NOT EXISTS test'")
    Execute(createDatabaseCmd, user=params.operator, logoutput=False, tries=5, try_sleep=5)
    Logger.info("Run the create table command: CREATE TABLE IF NOT EXISTS test.test (`id` BIGINT, `data` VARCHAR("
                "1024)) DUPLICATE KEY(`id`) DISTRIBUTED BY HASH(id) BUCKETS 10 PROPERTIES('replication_num' = '1');")
    Execute(createTableCmd, user=params.operator, logoutput=False, tries=5, try_sleep=5)
    Logger.info("Insert test data...")
    Execute(insertDataCmd, user=params.operator, logoutput=False, tries=5, try_sleep=5)
    Logger.info("Start the count test...")
    countResult = commands.getoutput(countTableCmd)
    Logger.info("count result: \r\n--result--\r\n{0}\r\n----------".format(countResult))


class ServiceCheck(Script):
    def service_check(self, env):
        import params
        env.set_params(params)
        testDorisClusterUsability()


if __name__ == "__main__":
    ServiceCheck().execute()

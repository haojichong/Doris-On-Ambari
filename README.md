# Doris-On-Ambari

## 说明

- Ambari 集成 Doris 服务
- Ambari版本: 2.7.5版本
- Doris版本: PALO-1.0.0 (2022-03-21)

## 使用方式

#### 1.部署

1. 在 **/var/lib/ambari-server/resources/stacks/HDP/3.1/services** 目录下创建目录 **DORIS**

   ```shell
   mkdir -p /var/lib/ambari-server/resources/stacks/HDP/3.1/services/DORIS
   ```

2. 将项目中doris中所有内容拷贝至 **DORIS** 目录下

3. 重启 ambari server服务

   ```shell
   ambari-server restart
   ```

#### 2.使用

1. 登录Ambari 管理界面,添加服务,选择 Doris

2. 分配角色:FE/BE/BROKER/PALO-STUDIO

3. 配置文件:

   1. env-doris 配置文件
      1. 需要配置doris和palo_studio的安装包下载地址
      2. 需要配置安装的目录
      3. 需要配置安装包下载到指定位置的目录
   2. 需要检查所有端口是否被占用[8030,8040,8080,9030,8000等]
   3. fe.conf 需要指定元数据存储目录,其他配置根据需求配置
   4. be.conf 需要指定数据存储目录,其他配置根据需求配置
   5. broker.conf 根据需求配置
   6. studio.conf 配置数据库连接信息[可选项,可以将数据库类型设置为H2]

4. 开始安装部署...

   

## 注意事项

1. FE/BE 的升级为实验功能,请勿在生产环境中使用
2. 暂未实现Broker的升级功能
3. 部署完成以后,需要使用MySQL客户端连接Doris手动来配置,添加FE/BE/BROKER等
4. Doris部署文档:http://note.youdao.com/noteshare?id=aca0d927508eaf365596756d9cda3be7&sub=82BD3C37BB0A4A2297064103C105AF3F
5. Palo_Studio部署文档:http://note.youdao.com/noteshare?id=4d43de88da3a3df7e09a98b17a03f1ca&sub=DDAF52BEE87742698063EE499412262A
6. 其他问题参考Doris官网:[Apache Doris](https://doris.apache.org/zh-CN/)
7. 预编译安装包下载地址
   1. doris:[Palo文档PALO - 预编译版本下载 | Doris (baidu.com)](http://palo.baidu.com/docs/下载专区/预编译版本下载)
   2. palo_studio:[Palo文档PALO - 工具下载 | Doris (baidu.com)](http://palo.baidu.com/docs/生态工具/工具下载)
8. 联系方式:QQ-821621741



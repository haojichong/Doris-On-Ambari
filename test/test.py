import mysql.connector

# 替换以下信息为你的数据库连接信息
db_config = {
    "host": "192.168.12.18",
    "port":"9031",
    "user": "admin",
    "password": "",
    "database": "information_schema"
}

def get_master_host():
    try:
        # 连接到MySQL数据库
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to Doris database")
            # 创建游标对象
            cursor = connection.cursor()
            # 执行 SHOW DATABASES 命令
            cursor.execute("SHOW FRONTENDS;")
            # 获取结果
            databases = cursor.fetchall()
            # 打印结果
            print("get doris fe follower master host")
            for database in databases:
                if database[7] == 'true':
                    print(database[1])

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    finally:
        # 关闭游标和连接
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Doris connection closed")



if __name__ == "__main__":
    get_master_host()
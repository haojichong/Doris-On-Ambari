from pymilvus import connections, db



if __name__ == '__main__':
    conn = connections.connect(host="192.168.12.132", port=19530)

    # database = db.create_database("my_database")

    print(db.list_database())
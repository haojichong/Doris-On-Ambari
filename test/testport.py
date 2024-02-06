import socket
import random



def generate_random_string(length,str):
    # 设置随机种子
    random.seed("kdp-trino-random-seed-{0}".format(str))
    letters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(letters) for i in range(length))


def is_port_alive(host, port):
    try:
        # 创建套接字对象
        with socket.create_connection((host, port), timeout=1000):
            return True
    except (socket.timeout, socket.error):
        return False

def find_available_host(host_str, port):
    hosts = host_str.split(',')
    for host in hosts:
        host = host.strip()
        try:
            if is_port_alive(host, port):
                return socket.gethostbyname(host)
        except Exception:
            pass
    # 如果所有主机都不可用，抛出异常
    return ""

if __name__ == "__main__":
    # e1f1e1b0-2bdc-4553-a8ab-61e4304f832a
    # # 请替换为你的主机字符串和端口
    # result = ''
    # hosts_str = "192.168.12.199"
    # target_port = 9031
    # result = find_available_host(hosts_str, target_port)
    # result = result + '2222'
    # print(result)
    # # 每次调用生成的随机字符串都会一样，因为种子是固定的
    # print(generate_random_string(8,'1-192.168.12.199'))
    # print(generate_random_string(4,'2-192.168.12.199'))
    # print(generate_random_string(4,'3-192.168.12.199'))
    # print(generate_random_string(4,'4-192.168.12.199'))
    # print(generate_random_string(12,'5-192.168.12.199'))

    str = ',192.168.12.199,192.168.12.123,192.168.12.111'
    isFeHa = str.replace(",", "", 1).count(',') >= 2
    print(isFeHa)


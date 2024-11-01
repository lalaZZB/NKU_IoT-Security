import binascii
import socket
import time

# 创建TCP套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 目标地址和端口
aimAddress = ('192.168.1.3', 102)

try:
    # 连接到目标
    client_socket.connect(aimAddress)
    client_socket.settimeout(1)  # 设置超时时间为1秒

    # 数据报文
    PIserve = '0300001611e00000000900c1020101c2020101c0010a'

    setup = '0300001902f08032010000ccc100080000f0000001000103c0'

    stop = '0300002102f0803201000000770010000029000000000009505f50524f4752414d'

    # 发送第一个数据包
    client_socket.send(binascii.unhexlify(PIserve))
    time.sleep(1)
    print("已发送piserve数据包")

    # 发送第二个数据包
    client_socket.send(binascii.unhexlify(setup))
    time.sleep(1)
    print("已发送setup数据包")

    # 发送第三个数据包
    client_socket.send(binascii.unhexlify(stop))
    time.sleep(1)
    print("已发送stop数据包")

except socket.error as e:
    print(f"套接字错误: {e}")

finally:
    client_socket.close()
    print("连接已关闭")

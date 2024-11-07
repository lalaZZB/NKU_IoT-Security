import paho.mqtt.client as mqtt
from cryptography.fernet import Fernet
import time
import json

# 配置
broker_address = "192.168.188.130"  # MQTT服务器地址
username = "Client2"  # MQTT用户名
password = "Client123456"  # MQTT密码
encryption_key = b"P0LFY4l8Z5t0UI5PQubGQ3o0u9c8PiZ7JRT6qYFLy38="  # 加密密钥

devices = {}
near_devices = []

# 创建加密器对象
cipher_suite = Fernet(encryption_key)


def main():
    while True:
        print("\n欢迎使用物联网设备控制端,请输入对应操作的序号进行操作：")
        print("1. 设备操控")
        print("2. 查看设备状态")
        print("3. 设备绑定")
        print("4. 设备解绑")

        # 获取用户输入
        choice = input()

        if choice == "1":
            broadcast()
            print("当前在线设备：(\033[94m", end="")
            for device in devices:
                print(" " + device, end="")
            print(" \033[0m)")

            # 获取用户输入
            device_choice = input()

            # 控制设备
            if device_choice in devices and devices[device_choice]:
                command = {}
                if device_choice == "fridge":
                    print(f"1. 开关{device_choice}\n2. 调节温度")
                    action = input()
                    if action == "2":
                        if not devices[device_choice]["status"]:
                            print("冰箱尚未开启，请先开启冰箱")
                            continue
                        print("请输入目标温度：")
                        temperature = int(input())
                        command = {
                            "device": device_choice,
                            "action": "set",
                            "temperature": temperature,
                            "client": username,
                        }
                        if temperature <= -25 or temperature >= 5:
                            print("温度超出范围，请重新设置！")
                        else:
                            print(f"冰箱温度已设置为{temperature}℃")
                    elif action == "1":
                        print(f"{device_choice}已", end="")
                        if devices[device_choice]["status"]:
                            print("关")
                        else:
                            print("开")
                        command = {
                            "device": device_choice,
                            "action": "switch",
                            "client": username,
                        }
                    else:
                        print("错误，请重新输入！")
                else:
                    print(f"{device_choice}已", end="")
                    if devices[device_choice]["status"]:
                        print("关")
                    else:
                        print("开")
                    command = {
                        "device": device_choice,
                        "action": "switch",
                        "client": username,
                    }
                encrypted_command = cipher_suite.encrypt(json.dumps(command).encode())
                client.publish("command", encrypted_command)
            else:
                print("错误，请重新输入！")
        elif choice == "2":
            broadcast()
            # print(devices)
            if not devices:
                print("\033[91m\n未绑定设备\033[0m")
                continue
            else:
                if "light" in devices:
                    print(
                        "\033[91m\n灯: {}\033[0m".format(
                            "开" if devices["light"]["status"] else "关"
                        )
                    )
                if "fridge" in devices:
                    temperature_str = (
                        str(devices["fridge"]["temperature"])
                        if devices["fridge"]["temperature"] is not None
                        else "未设置"
                    )
                    print(
                        "\033[91m\n冰箱: {}   温度: {}\033[0m".format(
                            "开" if devices["fridge"]["status"] else "关", temperature_str
                        ),
                        end="\n",
                    )
                if "camera" in devices:
                    print(
                        "\033[91m\n摄像头: {}\033[0m".format(
                            "开" if devices["camera"]["status"] else "关"
                        )
                    )

        elif choice == "3":
            print("请输入要绑定的设备名称(\033[94m", end="")
            for device in near_devices:
                if device not in devices:
                    print(" " + device, end="")
            print(" \033[0m)")
            device = input()
            bind(device)
            broadcast()

        elif choice == "4":
            print("请输入要解绑的设备名称(\033[91m", end="")
            for device in devices:
                print(" " + device, end="")
            print(" \033[0m)")
            device = input()
            unbind(device)
            broadcast()

        else:
            print("错误，请重新输入！")
            continue

        # 跳出循环，执行下一次操作
        time.sleep(0.2)
        continue


def broadcast():
    command = {"client": username}
    encrypted_command = cipher_suite.encrypt(json.dumps(command).encode())
    client.publish("broadcast", encrypted_command)


def receive(msg):
    global near_devices, devices

    decrypted_msg = cipher_suite.decrypt(msg.payload)
    parsed_msg = json.loads(decrypted_msg)

    device = parsed_msg["device"]
    status = parsed_msg["status"]
    belongsto = parsed_msg["belongsto"]

    if device not in near_devices:
        near_devices.append(device)

    if username not in belongsto:
        return

    devices[device] = {"status": status}
    if device == "fridge":
        temperature = parsed_msg["value"]
        devices[device]["temperature"] = temperature


def bind(device):
    command = {"device": device, "client": username}
    encrypted_command = cipher_suite.encrypt(json.dumps(command).encode())
    client.publish("bind", encrypted_command)


def unbind(device):
    command = {"device": device, "client": username}
    encrypted_command = cipher_suite.encrypt(json.dumps(command).encode())
    client.publish("unbind", encrypted_command)
    del devices[device]


# 处理连接事件
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("成功连接到MQTT服务器")
    else:
        print("连接到MQTT服务器失败， 错误代码 %d\n", rc)

    # 开始订阅消息和启动消息循环
    client.subscribe("receive")

    # 发送状态查询请求
    command = {"client": username}
    encrypted_command = cipher_suite.encrypt(json.dumps(command).encode())
    client.publish("broadcast", encrypted_command)


# 处理消息事件
def on_message(client, userdata, msg):
    if msg.topic == "receive":
        receive(msg)


# 创建 MQTT 客户端对象
client = mqtt.Client(username)
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message

# 连接 MQTT 服务器
client.connect(broker_address, 1883, 20)

# 启动消息循环
client.loop_start()

time.sleep(0.5)
main()

# 停止消息循环
client.loop_stop()

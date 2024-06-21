import socket
import string
import time
import random
from datetime import datetime

def generate_others(length):
    return ''.join(random.choices(string.ascii_letters,k=length)) #''.join()：实现将random.choices()随机生成的length个字符拼接在一起，最后生成一个长度为length的字符串

def main():
    # 初始化：
    total_packets = 12
    lost_packets = 0
    received_packets = 0
    ver = 2
    others = generate_others(200)
    RTT_list = []

    # 获取服务器IP和端口：
    server_ip = input("请输入server IP：")
    server_port = int(input("请输入server port："))

    # 创建UDP套接字：
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 模拟TCP-建立连接：
    packet_hello = 'client SYN'
    client_socket.sendto(packet_hello.encode(),(server_ip,server_port))
    response, server_address = client_socket.recvfrom(2048)
    if response.decode() == 'server ACK':
        packet_ACK = 'client ACK'
        client_socket.sendto(packet_ACK.encode(), server_address)
        print("成功与server端建立连接！")

        # 交互：
        for i in range(1, total_packets + 1):

            flag = False
            retry = 2

            # packet = (str(i)+str(ver)+others).encode()
            packet = i.to_bytes(2, byteorder='big') + ver.to_bytes(1, byteorder='big') + others.encode('utf-8')
            # 输出测试：
            # print(len(packet),packet)
            # print(int.from_bytes(packet[:2]))

            while flag == False and retry > 0:
                # 发送:
                start_time = time.time()
                client_socket.sendto(packet, (server_ip, server_port))
                client_socket.settimeout(0.1)
                retry -= 1

                # 超时处理：
                try:
                    # 接收服务器响应
                    response, server_address = client_socket.recvfrom(2048)
                    end_time = time.time()
                    flag = True
                    received_packets += 1
                    RTT = (end_time - start_time) * 1000  # 计算RTT（毫秒）
                    RTT_list.append(RTT)

                    # 输出测试：
                    # print(f"接收到来自 {server_address} 的请求: {response.decode()}")

                    print(f"sequence no: {i}, server address: {server_ip}:{server_port}, RTT: {RTT}ms")
                except socket.timeout:  # 用try-catch处理超时没接收到的情况
                    if retry == 0:
                        print(f"sequence no: {i}, request time out")
                        lost_packets += 1
                    # else: #输出测试：
                    #     print(f"sequence no: {i}, 发生丢包，进行第二次重传")

        # server time:
        server_time = None
        try:
            response, server_address = client_socket.recvfrom(2048)
            # 输出测试：
            # print(response.decode())
            server_time = response.decode()
        except socket.timeout:
            print("接收server time 响应超时")

        # 输出测试：
        # print(received_packets, lost_packets)


        # 模拟TCP-断开连接：
        packet_FIN = 'client FIN'
        client_socket.sendto(packet_FIN.encode(), server_address)
        response, server_address = client_socket.recvfrom(2048)
        if response.decode() == 'server ACK':
            response, server_address = client_socket.recvfrom(2048)
            if response.decode() == 'server FIN':
                packet_ACK = 'client ACK'
                client_socket.sendto(packet_ACK.encode(), server_address)
                client_socket.close()  # 成功关闭client端套接字
                print("成功断开连接！")
            else:
                print("断开连接失败：未接收到server FIN")
        else:
            print("断开连接失败：未接收到client FIN")

        # 计算汇总信息
        packet_loss_rate = (lost_packets / total_packets) * 100
        max_rtt = max(RTT_list)
        min_rtt = min(RTT_list)
        avg_rtt = sum(RTT_list) / received_packets
        rtt_std_dev = (sum([(x - avg_rtt) ** 2 for x in RTT_list]) / received_packets) ** 0.5

        print("\n【汇总信息】:")
        print(f"共接收到{received_packets}个udp包")
        print(f"丢包率为: {packet_loss_rate:.2f}%")
        print(f"最大RTT为: {max_rtt}ms")
        print(f"最小RTT为: {min_rtt}ms")
        print(f"平均RTT为: {avg_rtt}ms")
        print(f"RTT的标准差为: {rtt_std_dev}ms")
        if server_time:
            print(f"server整体响应时间为：{server_time}ms")

    else:
        print("连接建立失败：未接收到server SYN")

if __name__ == "__main__":
    main()

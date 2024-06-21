#server运行在guest os IP:
#server-client报文：2+1+8+其他
from socket import*
import random
from datetime import*
import string

def generate_others(length):
    return ''.join(random.choices(string.ascii_letters,k=length)) #''.join()：实现将random.choices()随机生成的length个字符拼接在一起，最后生成一个长度为length的字符串


def main():
    # 初始化：
    server_port = 12345  # 服务器端口
    client_no = 1
    others = generate_others(200-8)
    start_time = None
    end_time = None
    client_address = None

    # 启动server：
    server_socket = socket(AF_INET, SOCK_DGRAM) #创建UDP套接字
    server_socket.bind(('', server_port))
    print("UDP服务器已启动...")

    # 模拟TCP-建立连接：
    message, client_address = server_socket.recvfrom(2048)
    if message.decode()=='client SYN':
        print("接收到："+message.decode()+",并发送server ACK")  # 输出检测
        packet_ACK = 'server ACK'
        server_socket.sendto(packet_ACK.encode(),client_address)
        message, client_address = server_socket.recvfrom(2048)
        if message.decode() == 'client ACK':
            print("接收到："+message.decode()) # 输出检测
            print("成功与client端建立连接！")

            # 交互：
            while client_no <= 12:

                curr = 0

                message, client_address = server_socket.recvfrom(2048)

                client_no = int.from_bytes(message[:2])
                # print("输出测试：",int.from_bytes(message[:2]),message.decode()[:2],client_no==message.decode()[:2])

                # 输出测试：
                ver = int.from_bytes(message[2:3])
                data = message[3:].decode()
                print(f"接收到来自 {client_address} 的请求:", client_no, ver, data)

                # 响应：
                if random.random() < 0.3:  # 丢包率自定为30%
                    print(f"模拟丢包，不响应第{client_no}包")
                    curr += 1
                else:
                    print(f"响应第{client_no}包")
                    curr_time = datetime.now().strftime("%H-%M-%S")
                    packet = message[:2] + bytes([2]) + curr_time.encode('utf-8') + others.encode('utf-8')
                    server_socket.sendto(packet, client_address)
                    curr = 2

                if client_no == 1:
                    start_time = datetime.now()
                if client_no == 12 and curr == 2:
                    end_time = datetime.now()
                    client_no += 1

            # print(client_address)
            # server时间：
            server_time = int((end_time - start_time).total_seconds() * 1000)
            print("server_time:", server_time)
            server_socket.sendto(str(server_time).encode('utf-8'), client_address)

            # 模拟TCP-断开连接：
            message, client_address = server_socket.recvfrom(2048)
            if message.decode() == 'client FIN':
                print("接收到："+message.decode()+",并发送server ACK")  # 输出检测
                packet_ACK = 'server ACK'
                server_socket.sendto(packet_ACK.encode(), client_address)
                packet_FIN = 'server FIN'
                server_socket.sendto(packet_FIN.encode(), client_address)
                message ,client_address = server_socket.recvfrom(2048)
                if message.decode() == 'client ACK':
                    print("接收到："+message.decode())  # 输出检测
                    server_socket.close()
                    print("成功断开连接！")
                else:
                    print("断开连接失败：未接收到client ACK")
            else:
                print("断开连接失败：未接收到client FIN")

        else:
            print("连接建立失败：未接收到client ACK")
    else:
        print("连接建立失败：未接收到client SYN")


if __name__ == "__main__":
    main()

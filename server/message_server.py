import socket
import threading
import queue
import select
import struct
import sys
import os.path
import os
from db import Data_table
from  multiprocessing import Process, Manager
import time
maxlen_name =10

ip ="127.0.0.1"
port_msg = 9900
port_file_recv = 9903
port_file_send = 9904
class Msg_file_server():
    user_file_path = os.path.dirname(os.path.abspath(sys.argv[0]))+"\\user_file"  # 存放将于发送的文件信息
    user_profile_path = os.path.dirname(os.path.abspath(sys.argv[0]))+"\\Profile"
    def __init__(self):
        self.tcp_server = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        self.file_server = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        global ip, port_msg, port_file_recv
        self.tcp_server.bind((ip, port_msg))
        self.tcp_server.listen(10)
        self.file_server.bind((ip,port_file_recv))
        self.file_server.listen(10)
        self.socket_data_dict = {}
        self.online_table_1 = Manager().dict() # 键值对为:name:(addr, socket)
        self.online_table_2 = dict() # 键值对为：socket.getpeername():name
        self.for_send ={}        # 存储要发送给不在线的用户的普通消息,  键值对为: name:queue
        self.for_file_send = Manager().dict() # 键值对为: dst_name :(source_name,filename)
        self.lock_online = Manager().Lock()  # 为 普通消息的接受和发送所设置的lock，用于限制访问online表的进程
        self.lock_file = Manager().Lock() # 为收发文件所设置的lock，用于限制进入for_file_send字典的进程
        process_1 = Process(target = self.msg_tcp)  # 进程1负责普通消息的收发
        process_2 = Process(target = self.recv_file_pro)  # 进程2负责文件的接收
        process_3 = Process(target = self.send_file_pro) #进程3负责文件的发送

        process_1.start()
        process_2.start()
        process_3.start()
        process_1.join()
        process_2.join()
        process_3.join()
    def msg_tcp(self):
        """
        请注意登录失败的情况,read_socket并没有关闭,并没有从inputs中去掉
        """
        inputs = {self.tcp_server}
        outputs =set()
        while True:
            readable, writable, exception_socket = select.select(inputs , outputs, inputs,30) #阻塞30秒
            for read_socket in readable:
                if read_socket is self.tcp_server:
                    client_socket, addr = read_socket.accept()
                    print("yes")
                    inputs.add(client_socket)
                else:  #是client_socket
                    try:
                        flag = read_socket.recv(4)#0或1, 0表示要登录,1表示要发送信息
                        if flag ==b"": #
                            print("yes b''")
                            if read_socket.getpeername() in self.online_table_2.keys():  # 在线
                                name = self.online_table_2[read_socket.getpeername()]
                                self.lock_online.acquire()
                                del self.online_table_1[name]
                                self.lock_online.release()
                                del self.online_table_2[read_socket.getpeername()]
                                if read_socket in self.socket_data_dict.keys():
                                    self.for_send[name] = self.socket_data_dict[read_socket]
                                    outputs.remove(read_socket)
                            else:
                                pass
                            inputs.remove(read_socket)
                            read_socket.close()
                        else:
                            flag = struct.unpack("i",flag)[-1]
                            #print(flag)
                            if flag == 1:
                                source_name = self.online_table_2[read_socket.getpeername()]
                                destination_name = read_socket.recv(10).decode("utf-8").strip(" ")
                                msg = read_socket.recv(1024) # 假设普通的消息的对应的字节长度不超过1024
                                msg = "from ".encode() + self.online_table_2[read_socket.getpeername()].encode()+":\n".encode() + msg 
                                if destination_name in self.online_table_1.keys():  # 在线,则信息放入socket_data_dict,在遍历可写socket时,就发送信息
                                    dst_socket = self.online_table_1[destination_name][-1]
                                    outputs.add(dst_socket)                      # 添加进outputs集合,才能在返回到可写列表中,进而实现发送信息
                                    if dst_socket in self.socket_data_dict.keys():
                                        self.socket_data_dict[dst_socket].put_nowait(msg)  # 先进先出的队列,队列长度为无穷大
                                    else: #需要新建一个队列
                                        self.socket_data_dict[dst_socket] = queue.Queue(maxsize  = 0)
                                        self.socket_data_dict[dst_socket].put_nowait(msg)
                                elif destination_name == "#all": #给在线的所有人发消息
                                    print("to all")
                                    for value in self.online_table_1.values():

                                        dst_socket = value[-1]

                                        if dst_socket.getpeername() != read_socket.getpeername():
                                            print(read_socket.getpeername())
                                            outputs.add(dst_socket)
                                            if dst_socket in self.socket_data_dict.keys():
                                                self.socket_data_dict[dst_socket].put_nowait(msg)  # 先进先出的队列,队列长度为无穷大
                                            else: #需要新建一个队列
                                                self.socket_data_dict[dst_socket] = queue.Queue(maxsize  = 0)
                                                self.socket_data_dict[dst_socket].put_nowait(msg)
                                else:#不在线
                                    if destination_name in self.for_send.keys(): # 已经建立关于该用户的键值对
                                        self.for_send[destination_name].put_nowait(msg)
                                    else:                                        # 尚未建立关于该用户的键值对
                                        self.for_send[destination_name] = queue.Queue(maxsize  = 0)
                                        self.for_send[destination_name].put_nowait(msg)

                                

                            elif flag == 0:  # 登录
                                print("want to login")
                                user_name = read_socket.recv(10).decode("utf-8") # 获取名字,实际上名字不一定是10字符长,但为方便起见,在传输时会在后面补空格
                                user_name = user_name.strip(" ") # 去掉空格
        
                                password = read_socket.recv(20).decode("utf-8") # 取password
                                password = password.strip(" ")
                                print(user_name,len(user_name))
                                print(password)
                                if Data_table().query_login(user_name,password):
                                    print("success")
                                    read_socket.send("1".encode()) #发送登录成功的标志
                                    self.lock_online.acquire()
                                    self.online_table_1[user_name] = (read_socket.getpeername(),read_socket)
                                    
                                    #print(read_socket)
                                    #print(self.online_table_2.keys())
                                    #print(self.online_table_2[read_socket.getpeername])
                                    self.lock_online.release()

                                    self.online_table_2[read_socket.getpeername()] = user_name
                                    self.send_profile(user_name,read_socket)
                                    if user_name in self.for_send.keys():  # 有待发送到此用户的的信息
                                        outputs.add(read_socket)
                                        #self.socket_data_dict[read_socket] = queue.Queue(maxsize=0)
                                        self.socket_data_dict[read_socket] = self.for_send[user_name]
                                        del self.for_send[user_name]
                                else:
                                    read_socket.send("0".encode()) #发送登录失败的标志, 但并不把它从inputs中移除,因为很可能马上登录

                            elif flag == 2:   # 注册
                                print("want to sign_up")
                                user_name = read_socket.recv(10).decode("utf-8") # 获取名字,实际上名字不一定是10字符长,但为方便起见,在传输时会在后面补空格
                                user_name = user_name.strip(" ") # 去掉空格
        
                                password = read_socket.recv(20).decode("utf-8") # 取password
                                password = password.strip(" ")
                                print(user_name)
                                print(password)
                                if Data_table().query_sign_up(user_name,password):
                                    read_socket.send("1".encode()) #发送注册成功的标志
                                else:
                                    read_socket.send("0".encode()) #发送注册成功的标志
                    except ConnectionResetError:         # 客户端断开 
                        print("ConnectionResetError")
                        inputs.remove(read_socket)  
                        if read_socket.getpeername() in self.online_table_2.keys(): # 状态为在线
                            name = self.online_table_2[read_socket.getpeername()]
                            self.lock_online.acquire()
                            del self.online_table_1[name]
                            self.lock_online.release()
                            del self.online_table_2[read_socket.getpeername()]
                            if read_socket in self.socket_data_dict.keys():
                                self.for_send[name] = self.socket_data_dict[read_socket]

                                del self.socket_data_dict[read_socket]
                                outputs.remove(read_socket)
                        read_socket.close()

            for write_socket in writable:  # write_socket中可能含有已经关闭的read_sockdet,因为虽然outputs把该read_socket去掉,
                                           # 但在去掉前就已经把它放在返回的writable列表里
                if write_socket in self.socket_data_dict.keys():
                    # write_socket处于正常状态
                    write_queue = self.socket_data_dict[write_socket]
                    while not write_queue.empty():
                        message = write_queue.get_nowait()
                        write_socket.send(message)
            # for exception_socket in exceptional:
                # print('handling exceptional condition for', exception_socket.getpeername()[0])
                # if exception_socket in inputs:
                    # inputs.remove(exception_socket)
                    
                # if exception_socket in self.online_table_2.keys():
                    # name = self.online_table_2[exception_socket]
                    # del self.online_table_1[name]
                    # del self.online_table_2[exception_socket]
                # if exception_socket in self.socket_data_dict.keys():
                    # del socket_data_dict[exception_socket]
                # if name in self.for_send.keys():
                    # del self.for_send[name]
                # exception_socket.close()
            
            # 为什么要注释掉这一段代码,因为socket是阻塞socket,而且没有用带外数据.故 excptiional是空列表
    def recv_file_pro(self):
        self.file_server.setblocking(True)
        while True:
            temp_socket,addr = self.file_server.accept()
            print(temp_socket)
            print("start receiving")
            t = threading.Thread(target = self.recv_file,args=(temp_socket,))
            t.start()


    def recv_file(self,temp_socket):
        temp_socket.settimeout(20) # 
        source_name = temp_socket.recv(10).decode().strip(" ")
        print(source_name,len(source_name))
        try:
            assert(source_name in self.online_table_1.keys())
        except AssertionError  as e:
            print("error")

            raise(e)

        try:
            destination_name = temp_socket.recv(10).decode().strip(" ")
            if destination_name != source_name:
                len_filename = temp_socket.recv(4)
                len_filename = struct.unpack("i",len_filename)[-1]
                filename = temp_socket.recv(len_filename).decode()
                print(filename)
                dst_dir = self.user_file_path+"\\"+destination_name
                if os.path.exists(dst_dir):
                    pass
                else:
                    os.mkdir(dst_dir) # 没有则创建目录
                write_type = self.txt_binary_write(filename[-3:])
                with open(dst_dir+"\\"+filename,write_type) as f:
                    i = 0
                    if write_type == "wb":
                        while True:
                            try:
                                data_recv = temp_socket.recv(1028)
                                num = struct.unpack("i",data_recv[0:4])[-1]
                                #print(num)
                                if num==i:
                                    f.write(data_recv[4:])
                                    temp_socket.send(data_recv[0:4])
                        
                                    if len(data_recv) < 1028:
                                        break
                                    i+= 1
                            except (socket.timeout, ConnectionResetError) as e:
                                print(e)
                                pass
                    else:
                        while True:
                            try:
                                data_recv = temp_socket.recv(1028)
                                num = struct.unpack("i",data_recv[0:4])[-1]
                                #print(num)
                                if num==i:
                                    f.write(data_recv[4:].decode())
                                    temp_socket.send(data_recv[0:4])
                        
                                    if len(data_recv) < 1028:
                                        break
                                    i+= 1
                            except (socket.timeout, ConnectionResetError):
                                pass
                if os.listdir(dst_dir) == []:
                    print("remove")
                    os.rmdir(dst_dir)

                if os.path.exists(dst_dir):
                    # 为新表添加内容
                    self.lock_file.acquire()
                    if destination_name in self.for_file_send.keys():
                        pass
                    else:
                        self.for_file_send[destination_name] = []
                    temp = self.for_file_send[destination_name]
                    temp.append((source_name,dst_dir+"\\"+filename))
                    self.for_file_send[destination_name] = temp
                    print("已接收文件")
                    self.lock_file.release()
            else:
                self.recv_profile(source_name,temp_socket)
        except ConnectionResetError:
            print("ConnectionResetError")
            #inputs.remove(temp_socket)
        temp_socket.close()

    def send_file_pro(self):
        file_online_table ={}       # 以 destination_name 为键, 以(socket对象)为值
        lock_fileonline = threading.Lock()
        lock_socket = threading.Lock()
        threadqueue =  queue.Queue()
        send_file_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_file_sock.bind((ip,port_file_send))
        send_file_sock.listen(5)
        send_file_sock.setblocking(True)
        conn_thread = threading.Thread(target= self.build_conn, args =(send_file_sock,file_online_table,lock_fileonline))

        conn_thread.start()

        #conn_thread.join()

        while True:
            self.lock_file.acquire()

            for destination_name in self.for_file_send.keys():
                previous_len = len(self.for_file_send[destination_name])
                #print(destination_name)

                thread_send = threading.Thread(target = self.send_file_thre, args=(destination_name,self.for_file_send[destination_name],file_online_table,lock_fileonline,lock_socket)) 
                current_len = len(self.for_file_send[destination_name])
                if previous_len == current_len:
                    del self.for_file_send[destination_name]
                else:
                    self.for_file_send[destination_name] = self.for_file_send[destination_name][previous_len:]
                try:
                    threadqueue.put(thread_send,timeout = 5)
                except queue.Full:
                    print("full")
                    break
            self.lock_file.release()
            while True:
                try:
                    thread_send = threadqueue.get(timeout=1)
                    thread_send.start()

                except queue.Empty:
                    #print("can not get")
                    break

            #time.sleep(10)

    def build_conn(self,send_file_sock, file_online_table,lock_fileonline):
        while True:
            conn_sock, addr = send_file_sock.accept()  # 建立发送文件的连接
            user_name = conn_sock.recv(10).decode("utf-8").strip(" ")
            lock_fileonline.acquire()
            file_online_table[user_name] = conn_sock
            lock_fileonline.release()

    def send_file_thre(self,destination_name,source_filename,file_online_table,lock_fileonline,lock_socket):
        print("start send thread")
        
        try:
            self.lock_online.acquire()
            if destination_name not in self.online_table_1.keys():
                    self.lock_online.release()
                    if destination_name in file_online_table.keys():
                        lock_fileonline.acquire()
                        del file_online_table[destination_name]
                        lock_fileonline.release()
            else:
                self.lock_online.release()
            while destination_name not in self.online_table_1.keys():
                time.sleep(10)
                pass

            file_amount = len(source_filename)  # 获取file的数量
            lock_fileonline.acquire()
            socket_send = file_online_table[destination_name]
            lock_fileonline.release()
            lock_socket.acquire()
            socket_send.send(struct.pack("i",file_amount))


            
            for source_name, filename in source_filename:
                source_name = source_name + (maxlen_name - len(source_name.encode()))*' '  # 补充到长度为10
                socket_send.send(source_name.encode())  # 固定发送10长度的字节流
                filename_encode = os.path.basename(filename).encode()
                filename_len = len(filename_encode)
                socket_send.send(struct.pack("i",filename_len))
                socket_send.send(filename_encode)

            # 循环读取文件
            for i in range(file_amount):
                #print("waiting")
                len_encode = socket_send.recv(4)
                filename_len = struct.unpack("i",len_encode)[-1]
                temp_filename = socket_send.recv(filename_len)
                
                temp_filename =  os.path.dirname(filename) + "\\" +temp_filename.decode()
                print(temp_filename)
                read_type = self.txt_binary_read(temp_filename[-4:])
                with open(temp_filename,read_type) as f:
                    i = 0
                    if read_type == "r":
                        while True:
                            content = f.read(1024).encode()                
                            try:
                                if len(content)!=0:
                                    #print(len(content))
                                    data_send = struct.pack("i",i) + content
                                    socket_send.send(data_send)
                                    try:
                                        num = socket_send.recv(4)
                                        if struct.unpack("i",num)[-1] == i:
                                            pass
                                    except socket.timeout:
                                        while True:
                                            try:
                                                socket_send.send(data_send)
                                                num = socket_send.recv(4)
                                                if struct.unpack("i",num)[-1] == i:
                                                    break
                                            except socket.timeout:
                                                pass
                                    i+=1
                                else:
                                    break
                            except ConnectionResetError:
                                pass
                    else:
                        while True:
                            content = f.read(1024)                
                            try:
                                if len(content)!=0:
                                    #print(len(content))
                                    data_send = struct.pack("i",i) + content
                                    socket_send.send(data_send)
                                    try:
                                        num = socket_send.recv(4)
                                        if struct.unpack("i",num)[-1] == i:
                                            pass
                                    except socket.timeout:
                                        while True:
                                            try:
                                                socket_send.send(data_send)
                                                num = socket_send.recv(4)
                                                if struct.unpack("i",num)[-1] == i:
                                                    break
                                            except socket.timeout:
                                                pass
                                    i+=1
                                else:
                                    break
                            except ConnectionResetError:
                                pass
        except (ConnectionResetError, KeyError):
            print("error")
            pass
        finally:
            lock_socket.release()
    def txt_binary_write(self,file_type):
        if file_type!=".txt": # 非文本文件
            return "wb"
        else:
            return "w"       # 文本文件

    def txt_binary_read(self,file_type):
        if file_type!=".txt": # 非文本文件
            return "rb"
        else:
            return "r"       # 文本文件

    def send_profile(self,user_name,read_socket):
        read_socket.setblocking(True)
        read_socket.settimeout(3)
        if os.path.exists(self.user_profile_path + "\\" + user_name + ".jpg"):
            des_file = self.user_profile_path + "\\" + user_name + ".jpg"
        else:
            des_file = self.user_profile_path + "\\" + "default.jpg"
        with open(des_file,"rb") as f:
            i = 0
            while True:
                content = f.read(1024)                
                try:
                    if len(content)!=0:
                        #print(len(content))
                        data_send = struct.pack("i",i) + content
                        read_socket.send(data_send)
                        try:
                            num = read_socket.recv(4)
                            if struct.unpack("i",num)[-1] == i:
                                pass
                        except socket.timeout:
                            while True:
                                try:
                                    read_socket.send(data_send)
                                    num = read_socket.recv(4)
                                    if struct.unpack("i",num)[-1] == i:
                                        break
                                except socket.timeout:
                                    pass
                        i+=1
                    else:
                        break
                except ConnectionResetError:
                    print("头像发送失败")
            
    def recv_profile(self,source_name,temp_socket):
        with open(self.user_profile_path+"\\"+source_name+".jpg","wb") as f:
            i = 0
            while True:
                try:
                    data_recv = temp_socket.recv(1028)
                    num = struct.unpack("i",data_recv[0:4])[-1]
                    #print(num)
                    if num==i:
                        f.write(data_recv[4:])
                        temp_socket.send(data_recv[0:4])
                        if len(data_recv) < 1028:
                            break
                        i+= 1
                except socket.timeout:
                    pass
if __name__ == "__main__":
    one_server = Msg_file_server()
    
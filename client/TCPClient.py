# -*- coding: UTF-8 -*-
import socket
import os.path
import struct
import threading
from threading import Lock
import queue
import time
import sys
class Client():
    maxlen_name = 10
    maxlen_password = 20
    def __init__(self):
        self.build_connection()
        self.lock = Lock()




    def build_connection(self):
        self.server_ip = "127.0.0.1"
        self.port_msg = 9900
        self.port_recv_file = 9904
        self.msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_recv_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.msg_socket.connect((self.server_ip, self.port_msg))
        self.msg_socket.setblocking(True)
        self.msg_socket.settimeout(1)
        self.file_recv_sock.connect((self.server_ip, self.port_recv_file))
        self.file_recv_sock.setblocking(True)
    def send_login_information(self,account,password):
        account = account + (self.maxlen_name - len(account.encode()))*' '   # 在后面补空格
        password = password + (self.maxlen_password - len(password.encode()))*' ' # 在后面补空格
        self.msg_socket.send(struct.pack("i",0))
        self.msg_socket.send(account.encode())
        self.msg_socket.send(password.encode())
        self.file_recv_sock.send(account.encode())
        result = self.msg_socket.recv(1).decode()
        profile = None
        if result == "1":
            with open(os.path.dirname(os.path.abspath(sys.argv[0]))+"\\"+"profile.jpg","wb") as f:
                i = 0
                while True:
                    try:
                        data_recv = self.msg_socket.recv(1028)
                        num = struct.unpack("i",data_recv[0:4])[-1]
                        #print(num)
                        if num==i:
                            f.write(data_recv[4:])
                            self.msg_socket.send(data_recv[0:4])
                        
                            if len(data_recv) < 1028:
                                break
                            i+= 1
                    except socket.timeout:
                        pass
                
        return result
    def send_sign_up_information(self,account,password):
        account = account + (self.maxlen_name - len(account.encode()))*' '   # 在后面补空格
        password = password + (self.maxlen_password - len(password.encode()))*' ' # 在后面补空格
        sign_up_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sign_up_socket.connect((self.server_ip, self.port_msg))
        sign_up_socket.send(struct.pack("i",2))      # 注册信息
        sign_up_socket.send(account.encode())
        sign_up_socket.send(password.encode())

        result = sign_up_socket.recv(1).decode()
        print("result is",result)
        return result
    def send(self,msg,account):
        if len(msg)>18 and msg[10:18]=="file:///" and os.path.exists(msg[18:]):  #要传输文件  判断语句还有加上文件是否存在得到判断,估计要用到os
            self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.file_socket.connect((self.server_ip,9903))
            account = account + (self.maxlen_name - len(account.encode()))*' '
            self.file_socket.send(account.encode())
            self.file_socket.send(msg[0:10].encode())
            filename = os.path.basename(msg[18:])
            
            len_filename = len(filename.encode())
            self.file_socket.send(struct.pack('i',len_filename))
            self.file_socket.send(filename.encode())
            read_type = self.txt_binary_read(msg[-4:])
            with open(msg[18:],read_type) as f:
                i = 0
                if read_type == "r":
                    while True:
                        content = f.read(1024).encode()                
                        try:
                            if len(content)!=0:
                                #print(len(content))
                                data_send = struct.pack("i",i) + content
                                self.file_socket.send(data_send)
                                try:
                                    num = self.file_socket.recv(4)
                                    if struct.unpack("i",num)[-1] == i:
                                        pass
                                except socket.timeout:
                                    while True:
                                        try:
                                            self.file_socket.send(data_send)
                                            num = self.file_socket.recv(4)
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
                                self.file_socket.send(data_send)
                                try:
                                    num = self.file_socket.recv(4)
                                    if struct.unpack("i",num)[-1] == i:
                                        pass
                                except socket.timeout:
                                    while True:
                                        try:
                                            self.file_socket.send(data_send)
                                            num = self.file_socket.recv(4)
                                            if struct.unpack("i",num)[-1] == i:
                                                break
                                        except socket.timeout:
                                            pass
                                i+=1
                            else:
                                break
                        except ConnectionResetError:
                            pass
            self.file_socket.close()
        else:

            msg = msg.encode()
            flag = 1
            self.lock.acquire()
            self.msg_socket.send(struct.pack("i",flag))
            self.msg_socket.sendall(msg)
            self.lock.release()

    def change_profile(self,filename,account):  # 改变头像
        self.profile_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.profile_socket.connect((self.server_ip,9903))
        account = account + (self.maxlen_name - len(account.encode()))*' '
        self.profile_socket.send(account.encode())
        self.profile_socket.send(account.encode())
        with open(filename,"rb") as f:
            i = 0
            while True:
                content = f.read(1024)                
                try:
                    if len(content)!=0:
                        #print(len(content))
                        data_send = struct.pack("i",i) + content
                        self.profile_socket.send(data_send)
                        try:
                            num = self.profile_socket.recv(4)
                            if struct.unpack("i",num)[-1] == i:
                                pass
                        except socket.timeout:
                            while True:
                                try:
                                    self.profile_socket.send(data_send)
                                    num = self.profile_socket.recv(4)
                                    if struct.unpack("i",num)[-1] == i:
                                        break
                                except socket.timeout:
                                    pass
                        i+=1
                    else:
                        break
                except ConnectionResetError:
                    pass
        time.sleep(5)
        self.profile_socket.close()

    # def close_socket(self):
        # self.msg_socket.shutdown()
        # self.msg_socket.close()

    def recv_for_longtime(self,update_signal,recv_file_signal):
        t_recv_msg = threading.Thread(target =self.receive_msg, args = (update_signal,))
        t_recv_file = threading.Thread(target =self.receive_file, args = (recv_file_signal,))
        t_recv_msg.start()
        t_recv_file.start()

    def receive_msg(self, update_signal):
        self.msg_socket.setblocking(0)
        while True:
            self.lock.acquire()
            try:
                msg = self.msg_socket.recv(1024) 
                update_signal.emit(msg.decode()+"\n")
            except BlockingIOError:
                pass
            self.lock.release()

    def receive_file(self,recv_file_signal):
        #print(self.msg_socket.getsockname())
        """
        self.temp_filename 是存放在客户端硬盘的完整文件名
        self.target_file   是basename
        """
        self.temp_filename = queue.Queue()  
        self.target_file = queue.Queue()
        print("thread start")
        while True:

            file_amount = self.file_recv_sock.recv(4)
            print("received")
            file_amount = struct.unpack("i",file_amount)[-1]
            source_filename = [None for i in range(file_amount)]
            
            for i in range(file_amount): # 接收发文件者的名字和文件名
                source_name = self.file_recv_sock.recv(10).decode().strip(" ")
                filename_encode = self.file_recv_sock.recv(4)
                filename_len = struct.unpack("i",filename_encode)[-1]
                filename = self.file_recv_sock.recv(filename_len).decode()
                source_filename[i] = (source_name, filename)
            print("signal will be emited")
            recv_file_signal.emit(source_filename)

            for i in range(file_amount):
                while self.temp_filename.empty():
                    print("empty")
                    time.sleep(2)
                #print("break")
                target = self.target_file.get() 
                filename_encode = target.encode()
                print(target)
                #print(self.temp_filename)
                #print(self.target_file)
                self.file_recv_sock.send(struct.pack("i",len(filename_encode)))
                self.file_recv_sock.send(filename_encode)
                #print(os.path.basename(self.temp_filename))
                saved_filename = self.temp_filename.get()
                write_type = self.txt_binary_write(saved_filename[-4:])
                with open(saved_filename,write_type) as f:
                    #print(self.temp_filename.get())
                    if write_type == "wb":
                        i = 0
                        while True:
                            try:
                                data_recv = self.file_recv_sock.recv(1028)
                                num = struct.unpack("i",data_recv[0:4])[-1]
                                #print(num)
                                if num==i:
                                    f.write(data_recv[4:])
                                    self.file_recv_sock.send(data_recv[0:4])
                        
                                    if len(data_recv) < 1028:
                                        break
                                    i+= 1
                            except socket.timeout:
                                pass

                    else:
                        i = 0
                        while True:
                            try:
                                data_recv = self.file_recv_sock.recv(1028)
                                num = struct.unpack("i",data_recv[0:4])[-1]
                                #print(num)
                                if num==i:
                                    f.write(data_recv[4:].decode())
                                    self.file_recv_sock.send(data_recv[0:4])
                        
                                    if len(data_recv) < 1028:
                                        break
                                    i+= 1
                            except socket.timeout:
                                pass

    def txt_binary_read(self,file_type):
        if file_type!='.txt':
            return "rb"
        else:
            return "r"

    def txt_binary_write(self,file_type):
        if file_type!=".txt":
            return "wb"
        else:
            return "w"


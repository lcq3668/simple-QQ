from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QLabel
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QWidget, QHBoxLayout , QTextEdit, QColorDialog,QMessageBox,QFileDialog
from PyQt5.QtGui import QMovie, QIcon, QColor, QPixmap
from PyQt5.QtCore import pyqtSignal, QSize
import sys
import os
from TCPClient import Client
from testfile import Ui_SubWindow
class Talking_win(QMainWindow):
    update_signal = pyqtSignal(str)
    recv_file_signal = pyqtSignal(list)
    confirm_path_signal = pyqtSignal()   # 点击另存为按钮则确认文件的保存路径
    #askfor_signal = pyqtSignal()  # 工作线程用于请求文件路径
    def __init__(self,one_client,account):
        super().__init__()
        self.initUI(account)
        self.account = account
        self.update_signal.connect(self.update_text)
        self.recv_file_signal.connect(self.remind_recv_file)
        self.confirm_path_signal.connect(self.confirm_path)
        #self.askfor_signal.connect(self.askfor_filepath)
        self.one_client = one_client

        self.one_client.recv_for_longtime(self.update_signal,self.recv_file_signal)

    def initUI(self,account):
        self.now_color = QColor(0,0,0)
        self.setGeometry(300,300,450,300)
        self.setWindowTitle('Welcome!'+account)
        self.Create_centre_widget()
        self.Create_layout(account)
        self.show()

    def Create_centre_widget(self):
        self.cen_wid = QWidget() 
        self.setCentralWidget(self.cen_wid)

    def Create_layout(self,account):
        self.cen_wid.mainlayout = QVBoxLayout()
        qhboxlayout = QHBoxLayout()
        rich_text_layout = QHBoxLayout() # 用于创建富文本

        #创建一些控件,并将控件放到水平布局中
        self.profile_photo = Mylabel(self,account)
        temp_map = QPixmap(os.path.dirname(os.path.abspath(sys.argv[0]))+"\\"+"profile.jpg")
        self.profile_photo.setPixmap(temp_map.scaled(QSize(30,25)))
        self.profile_photo.setFixedSize(30,25)
        self.nameline = QLineEdit(self)
        self.nameline.setPlaceholderText("请输入对方用户名")

        self.color_btn = QPushButton("",self)
        self.color_btn.setIcon(QIcon(os.path.dirname(os.path.abspath(sys.argv[0]))+'\\'+"flower.jpg"))
        self.color_btn.clicked.connect(self.Change_color)
        qhboxlayout.addWidget(self.profile_photo)
        qhboxlayout.addWidget(self.nameline)


        rich_text_layout.addWidget(self.color_btn)
        #创建发送信息框和显示框
        self.send_meage_text = QTextEdit()
        self.send_meage_text.setAcceptRichText(True)
        self.send_display_text = QTextEdit()
        self.send_display_text.setAcceptRichText(True)

        #创建发送信息按钮
        self.send_btn = QPushButton("发送",self)
        self.send_btn.clicked.connect(self.Send_message)

        #将水平布局,显示框,发送框和发送按钮整合到垂直布局
        self.cen_wid.mainlayout.addLayout(qhboxlayout)
        self.cen_wid.mainlayout.addWidget(self.send_display_text)
        # 添加包含一个富文本的控件和字体粗细控件的部件
        self.cen_wid.mainlayout.addLayout(rich_text_layout)
        self.cen_wid.mainlayout.addWidget(self.send_meage_text)
        self.cen_wid.mainlayout.addWidget(self.send_btn)
        self.cen_wid.setLayout(self.cen_wid.mainlayout)

            

    def update_text(self,msg):
        self.send_display_text.append(msg)
        
    def remind_recv_file(self,source_filename):
        if "file_win" not in dir(self):
            self.file_win = Ui_SubWindow(source_filename,self.confirm_path_signal)
            self.file_win.show()
        else:
            self.file_win.addfile(source_filename,self.confirm_path_signal)

    def confirm_path(self):
        """
        将要接收(保存)的文件传递给client对象的temp_file
        """
        if self.one_client.temp_filename.empty():
            for btn in self.file_win.available.keys():
                if self.file_win.available[btn][1] and (not self.file_win.available[btn][2]):
                    self.one_client.temp_filename.put(self.file_win.available[btn][0])
                    self.one_client.target_file.put(self.file_win.btn_dict[btn][0])
                    self.file_win.available[btn][2] = True
                    break



    # def askfor_filepath(self):
        # if "available" in dir(self.file_win):
            # for btn in self.file_win.available.keys():
                # if self.file_win.available[btn][1] and (not self.file_win.available[btn][2]):
                    # self.one_client.temp_filename = self.file_win.available[btn][0]
                    # self.one_client.target_file = self.file_win.btn_dict[btn][0]
                    # self.file_win.available[2] = True
                    # break

    def Send_message(self):
        #发送信息,并在显示框显示
        target_name = self.nameline.text()  #获取想要进行聊天的用户名
        msg = target_name+(10 - len(target_name.encode()))*' '+self.send_meage_text.toPlainText()
        self.one_client.send(msg,self.account) #接受server返回的信息
        self.send_display_text.setTextColor(self.now_color)
        msg = "to " + msg[:10] +"\n" + msg[10:]
        self.send_display_text.append(msg)
        self.send_meage_text.clear()




    def Change_color(self):
        self.now_color = QColorDialog.getColor()
        self.send_meage_text.setTextColor(self.now_color)
        

class Mylabel(QLabel):
    def __init__(self,parent,account):
        super().__init__()
        self.parent = parent
        self.account = account
    def mousePressEvent(self,mouseevent):
        abspath = QFileDialog.getOpenFileName(self,'请选择jpg图片')[0]
        if abspath:
            temp_map = QPixmap(abspath)
            self.parent.profile_photo.setPixmap(temp_map.scaled(QSize(30,25)))
            self.parent.one_client.change_profile(abspath,self.account)
        else:
            print(not abspath)
if __name__ =="__main__":
    app = QApplication(sys.argv)
    talk_win = Talking_win()
    sys.exit(app.exec_())
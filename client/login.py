from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QLabel
from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import pyqtSignal
import sys
import os
from talking_win import Talking_win
from TCPClient import Client
class Login_win(QMainWindow):
    sign_up_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300,300,350,300)
        self.setWindowTitle('Welcome! My firend')
        self.Create_centre_widget()
        self.Create_grid_groupbox()

        self.cen_wid.mainlayout = QVBoxLayout()

        self.Create_git()
        self.cen_wid.setLayout(self.cen_wid.mainlayout)
        self.cen_wid.mainlayout.addWidget(self.gridbox)



        self.show()

    def Create_centre_widget(self):
        self.cen_wid = QWidget() 
        self.setCentralWidget(self.cen_wid)
    def Create_git(self):
        """
        创建label 和动态图
        """
        self.label = QLabel(self)
        self.cen_wid.mainlayout.addWidget(self.label)
        path = os.path.dirname(os.path.abspath(sys.argv[0])) + "\\" + "welcome.gif"
        self.movie = QMovie(path)
        self.label.setMovie(self.movie)
        self.movie.start()
    def Create_grid_groupbox(self):
        self.gridbox = QGroupBox()
        self.gridlayout = QGridLayout()
        self.account_line = QLineEdit(self)
        self.account_line.setPlaceholderText("请输入账号")
        self.password_line = QLineEdit(self)
        self.password_line.setDragEnabled(True)
        self.password_line.setEchoMode(2) #2意味着是password模式，不会显式地显示字符..
        self.password_line.setPlaceholderText("请输入密码")
        self.login_btn = QPushButton("登录",self)
        self.login_btn.clicked.connect(self.Login)
        self.sign_up_btn = QPushButton("注册",self)
        self.sign_up_btn.clicked.connect(self.Sign_up)
        #添加控件
        self.gridlayout.addWidget(self.account_line)
        self.gridlayout.addWidget(self.password_line)
        self.gridlayout.addWidget(self.login_btn)
        self.gridlayout.addWidget(self.sign_up_btn)
        self.gridbox.setLayout(self.gridlayout)

    def Login(self):
        account = self.account_line.text()
        password = self.password_line.text()
        if "one_client" not in dir(self):
            self.one_client = Client()
        result = self.one_client.send_login_information(account,password)

        if result=="1":
            print("yes")
            self.talk_win=Talking_win(self.one_client,account)
            self.destroy(destroyWindow = True, destroySubWindows = False)
        elif result=="0":
            retry = QMessageBox()
            retry.setText("Sorry! The password or the account is wrong")
            retry.setInformativeText("Do you want to try again?")
            yes = retry.addButton("try again",QMessageBox.ActionRole)
            no = retry.addButton("exit",QMessageBox.ActionRole)
            retry.exec() #使之变成模态对话框
            if retry.clickedButton()== yes:
                retry.destroy()
            else:
                retry.destroy()
                self.destroy()
                

    def Sign_up(self):
        self.sign_up_signal.connect(self.send_sign_up_information)
        from sign_up import Ui_Form
        self.sign_up_widget = QWidget()
        self.sign_up_win = Ui_Form(self.sign_up_widget,self.sign_up_signal)

    def send_sign_up_information(self):
        if "one_client" not in dir(self):
            self.one_client = Client()
        result = self.one_client.send_sign_up_information(self.sign_up_widget.account,self.sign_up_widget.password)
        if result=="1":
            retry = QMessageBox()
            retry.setText("Congratulation!!!!!!!!!!!\n")
            retry.setInformativeText("You signed up successfully.")
            retry.exec() #使之变成模态对话框
        else:
            retry = QMessageBox()
            retry.setText("Sorry!The account exists.That is not usable for you.")
            retry.setInformativeText("Do you want to create another account?")
            yes = retry.addButton("try again",QMessageBox.ActionRole)
            no = retry.addButton("exit",QMessageBox.ActionRole)
            retry.exec() #使之变成模态对话框
            if retry.clickedButton()== yes:
                retry.destroy()
            else:
                retry.destroy()
                self.sign_up_widget.destroy()
                self.sign_up_win.destroy()
if  __name__ == "__main__":
    app = QApplication(sys.argv)

    one = Login_win()
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\studyINF\高级编程\experiment\untitled.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!
from PyQt5 import QtCore
from PyQt5.QtCore import  QRect

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton 
from PyQt5.QtWidgets import QMdiSubWindow ,QStatusBar, QMainWindow, QGroupBox,QFileDialog
import sys
import os.path
class Ui_SubWindow(QMainWindow):
    def __init__(self,source_filename,confirm_path_signal):
        super().__init__()
        self.setupUi()
        self.btn_dict ={}  #以按钮为键，以(文件名字,进度条)为值的字典
        self.create_unit(source_filename,confirm_path_signal)
    def setupUi(self):
        self.resize(400, 400)
        self.cen_wid = QWidget() 
        self.setCentralWidget(self.cen_wid)
        self.verticalLayout_2 = QVBoxLayout(self.cen_wid)
        self.cen_wid.setLayout(self.verticalLayout_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        # self.statusbar = QStatusBar(self)
        # self.statusbar.setObjectName("statusbar")
        # self.setStatusBar(self.statusbar)
        self.setWindowTitle("SubWindow")

    def create_unit(self,source_filename,confirm_path_signal):

        for source,filename in source_filename:  
            self.horizontalLayout = QHBoxLayout()
            self.groupbox = QGroupBox()
            self.label = QLabel(self.cen_wid) # os.path.dirname(os.path.abspath(sys.argv[0]))
            self.label.setPixmap(QPixmap(os.path.dirname(os.path.abspath(sys.argv[0]))+"\\"+"file.jpg"))
            self.horizontalLayout.addWidget(self.label)
            self.verticalLayout = QVBoxLayout()

            self.label_2 = QLabel(self)
            self.label_2.setText("from "+source+":"+filename)
            self.verticalLayout.addWidget(self.label_2)
            self.progressBar = QProgressBar(self)
            self.progressBar.setProperty("value", 0)
            self.progressBar.setObjectName("progressBar")
            self.verticalLayout.addWidget(self.progressBar)
            self.pushButton = QPushButton(self)
            self.pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
            self.pushButton.setFlat(True)
            self.pushButton.setText("另存为")
            self.pushButton.clicked.connect(lambda:self.saveas(self.pushButton,confirm_path_signal))  # 这里或许会出bug，是否能如我所愿,传递时,将所按的按钮传递到参数去
            self.verticalLayout.addWidget(self.pushButton)
            self.groupbox.setLayout(self.verticalLayout)
            self.horizontalLayout.addWidget(self.groupbox)
            self.btn_dict[self.pushButton] = (filename,self.progressBar)
            self.verticalLayout_2.addLayout(self.horizontalLayout)

    def saveas(self,pushbtn,confirm_path_signal): #另存为
        if "available" in dir(self):
            pass
        else:
            self.available = {}
            for btn in self.btn_dict.keys():
                self.available[btn] = ["0",False,False] # tuple中第一个元素是confirm(该按钮对应的文件是否已经确认保存路径)
                                                    # 第二个元素是recv_or_not(该按钮对应的文件是否已经被接收)
        # 还要生成文件保存对话框
        abspath = QFileDialog.getSaveFileName(self,'save as...')[0]
        if pushbtn not in self.available.keys():
            self.available[pushbtn] = ["0",False,False]
        #print("file is:",self.btn_dict[pushbtn][0])
        self.available[pushbtn][0] = abspath
        self.available[pushbtn][1] = True
        confirm_path_signal.emit()

    def addfile(self,source_filename,confirm_path_signal):
        self.create_unit(source_filename,confirm_path_signal)
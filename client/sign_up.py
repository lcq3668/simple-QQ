# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\studyINF\高级编程\experiment\sign_up.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QWidget
import sys
class Ui_Form(object):
    def __init__(self, Form,sign_up_signal):
        self.setupUi(Form,sign_up_signal)
        Form.show()
    def setupUi(self, Form,sign_up_signal):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.account_lineEdit = QtWidgets.QLineEdit(Form)
        self.account_lineEdit.setGeometry(QtCore.QRect(130, 180, 113, 20))
        self.account_lineEdit.setText("")
        self.account_lineEdit.setObjectName("account_lineEdit")
        self.password_lineEdit = QtWidgets.QLineEdit(Form)
        self.password_lineEdit.setGeometry(QtCore.QRect(130, 220, 113, 20))
        self.password_lineEdit.setObjectName("password_lineEdit")
        self.confirm_btn = QtWidgets.QPushButton(Form)
        self.confirm_btn.setGeometry(QtCore.QRect(140, 250, 75, 23))
        self.confirm_btn.setObjectName("confirm_btn")

        self.retranslateUi(Form,sign_up_signal)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form,sign_up_signal):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.account_lineEdit.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-style:italic; color:#aaaaff;\">昵称只能包含数字或英文字符</span></p><p><span style=\" font-style:italic; color:#aaaaff;\">且长度不超过10,也不能为空</span></p></body></html>"))
        self.account_lineEdit.setPlaceholderText(_translate("Form", "昵称"))
        self.password_lineEdit.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-style:italic; color:#aaaaff;\">要求同昵称</span></p></body></html>"))
        self.password_lineEdit.setPlaceholderText(_translate("Form", "密码"))
        self.confirm_btn.setText(_translate("Form", "确定"))
        self.confirm_btn.clicked.connect(lambda:self.record_information(Form, sign_up_signal))
    def record_information(self, Form,sign_up_signal):
        Form.account = self.account_lineEdit.text()
        Form.password = self.password_lineEdit.text()
        sign_up_signal.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QWidget()
    one = Ui_Form(widget)

    sys.exit(app.exec_())

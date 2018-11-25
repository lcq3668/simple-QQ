from login import *
if __name__ =="__main__":
    app = QApplication(sys.argv)
    one = Login_win()
    flag = app.exec_()
    sys.exit(flag)
import MySQLdb


class Data_table():
    def __init__(self):
        self.con_2db = MySQLdb.Connect(host = "127.0.0.1", user = "root", passwd = "lcqlcq1994",
                                        db = "account",port = 3306,charset = "utf8")
    def query_login(self, account, password):
        self.cur = self.con_2db.cursor() # 游标
        self.cur.execute("select name from user")
        all_name = self.cur.fetchall()

        if (account,) in all_name:
            
            self.cur.execute("select password from user where name=" +"\""+account+"\"")
            password_info = self.cur.fetchall()
            self.cur.close()
            self.con_2db.close()
            if (password,) in password_info:
                return True
        self.cur.close()
        self.con_2db.close()
        return False
    def query_sign_up(self,account,password):
        self.cur = self.con_2db.cursor() # 游标
        self.cur.execute("select name from user")
        all_name = self.cur.fetchall()

        if (account,) not in all_name:  # 数据表里已经有该账号
            self.cur.execute("insert into user values" + "(\"" + account + "\""+","+"\""+password+"\")")
            self.con_2db.commit() # 若不提交,则不能真正插入
            self.cur.close()
            self.con_2db.close()
            return True                 
        self.cur.close()
        self.con_2db.close()
        return False
if __name__ =="__main__":
    one = Data_table()
    #result = one.query_login("lcq","123")
    result2 = one.query_sign_up("any","123")
    print(result2)
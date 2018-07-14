from tkinter import *
import tkinter.messagebox as tm
import sqlite3,requests,json
import os
import pyxhook
import shelve
from textblob import TextBlob,Word


#sqlite connection
conn=sqlite3.connect('/home/an/Desktop/testDB.db')
cursor=conn.cursor()
sql_create_login_table = """ CREATE TABLE IF NOT EXISTS login (
                                        id integer PRIMARY KEY,
                                        email text NOT NULL,
                                        password text,
                                        status integer
                                    ); """
cursor.execute(sql_create_login_table)

gb=''
#gui window
class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        
        self.label_username = Label(self, text="Username")
        self.label_password = Label(self, text="Password")

        self.entry_username = Entry(self)
        self.entry_password = Entry(self, show="*")

        self.label_username.grid(row=0, sticky=E)
        self.label_password.grid(row=1, sticky=E)
        self.entry_username.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)

        # self.checkbox = Checkbutton(self, text="Keep me logged in")
        # self.checkbox.grid(columnspan=2)


        self.logbtn = Button(self, text="Login", command=self._login_btn_clicked)
        self.logbtn.grid(columnspan=2)
        self.pack()

    def _login_btn_clicked(self):
        # print("Clicked")
        username = self.entry_username.get()
        password = self.entry_password.get()

        # print(username, password)
        cursor.execute("SELECT * from login where email='"+username+"'")
        maildata=cursor.fetchone()
        global gb
        try:
            if maildata is None:
                payload={"username":username,"password":password}
                r=requests.post('http://127.0.0.1:5000/getdetails',data=json.dumps(payload))
                checkdata=r.json()
                if checkdata['status']=='no' :
                    tm.showwarning("Login Error","Something went wrong!")
                else :
                    cursor1=conn.cursor()
                    cursor1.execute("INSERT INTO login VALUES(?,?,?,?)",(checkdata['userid'],checkdata['username'],checkdata['password'],1))
                    conn.commit()
                    gb=checkdata['username']
                    self.new_windows()
                    self.close_windows()
            else:
                gb=maildata[1]
                if username == maildata[1] and password == maildata[2] :
                    self.new_windows()
                    self.close_windows()
                else :
                    tm.showerror("Login error", "Incorrect username or password!")
        except Exception as e:
            print(e)
            tm.showerror("Connection Lost","First time login needs network connection")

    def close_windows(self):
        self.master.destroy()
    def new_windows(self):
        test=Tk()
        test.title("Ambitious")
        test.geometry("250x100")
        gf=LogoutFrame(test)


class LogoutFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        global gb
        self.user = Label(self, text=gb)
        self.user.grid(row=0, sticky=E)
        self.qbtn = Button(self, text="Log out", command=self.close_windows)
        self.noti = Label(self, text="*press Log out to untrack!")
        self.noti.grid(row=3)
        self.qbtn.grid(columnspan=2)
        self.pack()
        self.key_fetch()
    def close_windows(self):
        global new_hook
        new_hook.cancel()
        self.createdb()
        self.master.destroy()
    def createdb(self):
        filepath='/home/an/Desktop/file.log'
        with open(filepath) as fp:
            line=fp.readline().strip()
            strlist=[]
            str1=''
            while line:
                # print(len(line.strip()))
                
                line=fp.readline()
                count=len(line.strip())
                print(count)
                if count==1 :
                    str1 += line.strip()
                else :
                    if len(str1)>1 and str1.isalpha():
                        str2=TextBlob(str1)
                        str1=str2.correct()
                        str2=Word(str1)
                        str1=str2.lemmatize()
                        str1=str(str1.lower())
                        strlist.append(str1)         
                    str1=''
        fp.close()
        open('/home/an/Desktop/file.log','w').close()
        dbfile=shelve.open("dbfile")
        # dbfile.clear()
        global gb
        if gb in list(dbfile.keys()):
            dbfile[gb]+=strlist
        else :
            dbfile[gb]=strlist
        # print(list(dbfile.keys()))
        try:
            list1=dbfile[gb]
            payload={"username":gb,"tokens":list1}
            r1=requests.post('http://127.0.0.1:5000/tokenposter',data=json.dumps(payload))
            print(r1.text)
            if r1.text == 'received' :
                dbfile[gb]=[]
            
        except Exception as e:
            print(e)
        dbfile.close()

    def key_fetch(self):
        log_file = os.environ.get('pylogger_file',os.path.expanduser('~/Desktop/file.log'))
        cancel_key = ord(os.environ.get('pylogger_cancel','`')[0])
        if os.environ.get('pylogger_clean', None) is not None:
            try:
                os.remove(log_file)
            except EnvironmentError:
            # File does not exist, or no permissions.
                pass
        def OnKeyPress(event):
            with open(log_file, 'a') as f:
                f.write('{}\n'.format(event.Key))
        # create a hook manager object
        global new_hook
        new_hook = pyxhook.HookManager()
        new_hook.KeyDown = OnKeyPress
        # set the hook
        new_hook.HookKeyboard()
        try:
            new_hook.start()
                     # start the hook
        except KeyboardInterrupt:
            # User cancelled from command line.
            pass
        except Exception as ex:
            # Write exceptions to the log file, for analysis later.
            msg = 'Error while catching events:\n  {}'.format(ex)
            # pyxhook.print_err(msg)
            with open(log_file, 'a') as f:
                f.write('\n{}'.format(msg))




root = Tk()
root.title("Ambitious")
root.geometry("270x100")
lf = LoginFrame(root)
root.mainloop()
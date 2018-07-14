from flask import Flask,redirect,url_for,request,render_template,session,send_file
from flaskext.mysql import MySQL
import json
import shelve
import operator


from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer


mysql=MySQL()
app=Flask(__name__)
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='amb'
app.config['MYSQL_DATABASE_HOST']='localhost'
mysql.init_app(app)
app.secret_key = "super secret key"

#chat

english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")

english_bot.set_trainer(ChatterBotCorpusTrainer)
# english_bot.train("chatterbot.corpus.english")
# english_bot.train("./static/english/")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(english_bot.get_response(userText))

@app.route("/chat")
def chat():
    if session.get('username'):
        return render_template('chat.html')
    else:
        return render_template("ambhome.html")


#chat ends

@app.route("/tree")
def tree():
    if session.get('username'):
        return render_template("tree.html")
    else:
        return render_template("ambhome.html")

@app.route("/home")
def home():
    if session.get('username'):
        return render_template("dashboard.html")
    else:
        return render_template("ambhome.html")


@app.route("/login",methods=['POST'])
def login():
    username=request.form['username']
    password=request.form['password']
    cursor=mysql.connect().cursor()
    cursor.execute("SELECT * from login where username='"+username+"'and password='"+password+"'")
    data=cursor.fetchone()
    if data is None:
        print("not match")
        return redirect(url_for('index')) 
        # render_template('index.html')
        # return json.dumps({'status':'nop'})
    else:
        print("match")
        session['username']=data[1]
        return redirect(url_for('home'))
        # return json.dumps({'status':'ok'})

@app.route("/forgotpass")
def forgotpass():
    return render_template('forgotpassword.html')

@app.route('/resetpass')
def resetpass():
    #return redirect('mailto:'+email+'?pass='+password)
    return redirect(url_for('index')) 


@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/ambhome")
def ambhome():
    return render_template('ambhome.html')

@app.route("/download")
def download():
    return send_file('/home/an/Desktop/ambitious/static/ambitious.deb.txt', attachment_filename='ambitious.deb.txt')



@app.route("/registeration",methods=['POST'])
def registeration():
    fname=request.form['fname']
    sname=request.form['sname']
    email=request.form['email']
    password1=request.form['password1']
    scount=1
    con=mysql.connect()
    cursor=con.cursor()
    cursor.execute("INSERT INTO register VALUES(%s,%s,%s,%s,%s)",('',fname,sname,email,1))
    con.commit()
    userid=cursor.lastrowid
    cursor.close()
    cursor1=con.cursor()
    cursor1.execute("INSERT INTO login VALUES(%s,%s,%s,%s)",(userid,email,password1,1))
    con.commit()
    cursor1.close()
    session['username']=email
    return render_template('dashboard.html')

@app.route("/uniquecheck",methods=['POST'])
def uniquecheck():
    mailid=request.form['email']
    con1=mysql.connect()
    cursor2=con1.cursor()
    cursor2.execute("SELECT e_mail from register where e_mail='"+mailid+"'")
    maildata=cursor2.fetchone()
    if maildata is None:
        #send data
        return json.dumps({'status':'yes'})
    else:
        # msg change mail id
        return json.dumps({'status':'no'})

@app.route("/")
def index():
    session.pop('username', None)
    return render_template('ambhome.html')

@app.route("/lpage")
def lpage():
    return render_template("index.html")

@app.route("/getdetails",methods=['POST'])
def getdetails():
    pcdata=request.get_json('data')
    # print(pcdata['username'])
    usermail=pcdata['username']
    userpass=pcdata['password']
    con11=mysql.connect()
    cursor22=con11.cursor()
    cursor22.execute("SELECT * from login where username='"+usermail+"'and password='"+userpass+"'")
    userdata=cursor22.fetchone()
    # print(userdata[1])
    if userdata is None:
        return json.dumps({'status':'no'})
    else:
        return json.dumps({'userid':userdata[0],'username':userdata[1],'password':userdata[2],'status':'yes'})

@app.route("/tokenposter",methods=['POST'])
def tokenposter():
    tokendata=request.get_json('data')
    print(tokendata['tokens'])
    shelffile=shelve.open("mydata")
    iduser=tokendata['username']
    if iduser in list(shelffile.keys()):
        shelffile[iduser]+=tokendata['tokens']
    else :
        shelffile[iduser]=tokendata['tokens']
    print(list(shelffile.values()))
    shelffile.close()
    return 'received'

@app.route("/priority",methods=['POST'])
def priority():
    shelffile=shelve.open("mydata")
    print(list(shelffile.keys()))
    commerce=["account","advance","agenda","agreement","allotment","annuity","assessment","asset","audit","balance","sheet","bank","bargain","cash","cheque","credit","ceposit","dividend","exchange","income","tax","investments","lease","liabilities","pledge","profit","lossaccount","revenue"]
    humanities=["decree","command","order","discordant","lacking","harmony","evolve","develop","excerpt","passage","grope","search","blindly","hover","hang","around","jostle","shove","laggard","plaudits","appulause","precude","prevent","revert","return","adage","wise","saying","bonanza","rewarding","churlish","rude","citadel","fortress","collaborate","rubble","broken","stones","servile","lacking","spirit","vigil","wrangle","argue","durable","strong","enterprising","ready","frugal","gingerly","glut","incognito","invalidate","legendary","oblique","respect","wanton"]
    science=["absolute","absorptive","power","accelerated","accelerator","action","adhesion","beaker","buoyancy","calibration","concave","lens","demagnetization","density","depolarisation","developer","circuit","current","induction","electrification","electrode","electron","electronics","energy","force","friction","gravitation","power","impulse","inertia","inference","melting","point","newton","nucleons","volume","watt"]
    ccount=0
    hcount=0
    scount=0
    uname=session['username']
    for key in shelffile[uname]:
        print(key)
        if key in commerce:
            ccount+=1
        if key in humanities:
            hcount+=1
        if key in science:
            scount+=1
    shelffile.close()
    print(ccount,hcount,scount)
    pdict={'Science':scount,'Commerce':ccount,'Humanities':hcount}
    spdict=sorted(pdict.items(),key=operator.itemgetter(1),reverse=True)
    return json.dumps(spdict)



#only for data test
@app.route("/poster",methods=['POST'])
def poster():
    data1=request.get_json('data')
    print(data1)
    return 'received'


if __name__ == "__main__":
    app.run(debug = True)
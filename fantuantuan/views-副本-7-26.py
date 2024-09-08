"""
Routes and views for the flask application.
"""
import os
import openpyxl
import time
import hashlib
import flask
from datetime import datetime
from flask import render_template
import flask_wtf
import wtforms
from fantuantuan import app
import sqlite3
#import flask_security as fs
#import flask_login
#import flask_sqlalchemy
# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired

# 定义的表单都需要继承自FlaskForm
class LoginForm(FlaskForm):
    # 域初始化时，第一个参数是设置label属性的
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('remember me', default=False)
    submit = SubmitField("log in")
    errors = ""
class RegisterForm(FlaskForm):
    email = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("sign")
    errors = ""
class SaveForm(FlaskForm):
    email = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    amount = IntegerField("amount",validators=[DataRequired()])
    submit = SubmitField("sign")
    errors = ""

import socket
def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

import re

def getOutterIP():
    ip = ''    
    try:
        res = flask.requests.get('https://myip.ipip.net', timeout=5).text
        ip = re.findall(r'(\d+\.\d+\.\d+\.\d+)', res)
        ip = ip[0] if ip else ''
    except:
        pass
    return ip
sqlite3.threadsafety=2
root="H:\\ers\\Admin\\source\\repos\\fantuantuan\\fantuantuan\\"
#ner=flask.request.get('http://myip.ipip.net', timeout=5).text()
uikit="192.168.1.2/uikit/"
conn=sqlite3.connect(root+"data.db", check_same_thread=False)
cu_shared=conn.cursor()
current_user={}#current_user=[uid,"name",["role"]]

admin_account_life=-1#admin account 登录保持时长
update_check_in_time=0 #是否当访问时更新一般用户teminal数据
base_rate=0.07
extra_rate=0.05
goodsprice={}  #good[uid]=price
goods={}   #good[uid]=品名
ordered={}#ordered[name][goods_uid]=cnt -->ordered[name][goods_uid]=[cnt,{attribute:val}]
note={}#note[name][goods_uid]=note_for_good
bill={} #bill[name]=[uid]
initialized=False
ordered_final_admin={}
order_start="0650"
order_deadline="0850"
def initialize():
    global initialized
    global goods
    global goodsprice
    global admin_account_life
    global base_rate
    global extra_rate
    global order_start
    global order_deadline
    initialized=True
    cu=conn.cursor()
    cu.execute("CREATE TABLE IF NOT EXISTS account(uid TEXT PRIMARY KEY,name TEXT,balance REAL,cost REAL,password TEXT,role TEXT,admin INTEGER)")#uid name balance weekly_cost password(cipher(md5)) role admin(bool)
    cu.execute("CREATE TABLE IF NOT EXISTS terminals(mac TEXT,role TEXT,name TEXT PRIMARY KEY,time REAL)")#[mac,用户组，用户名，记录时间]
    cu.execute("CREATE TABLE IF NOT EXISTS bills(date TEXT,id INTEGER PRIMARY KEY,name TEXT,content TEXT)")#[日期，订单编号，用户名，内容（“id 个数，”）]
    cu.execute("CREATE TABLE IF NOT EXISTS bills_shop(date TEXT,id INTEGER PRIMARY KEY,content TEXT,change TEXT)")#[日期，订单编号，用户名，内容（“id 个数，”），替换（“被替换 替代，”）]
    cu.execute("CREATE TABLE IF NOT EXISTS requests(time REAL PRIMARY KEY,ip TEXT,name TEXT,role TEXT,method TEXT,read INTEGER)")#[时间，IP，用户名，用户组，请求方法(get,post,UNKNOW,TypeError),是否标为已读]
    cu.execute("CREATE TABLE IF NOT EXISTS save_his(name TEXT,time TEXT,amount REAL,operater TEXT,id INTEGER PRIMARY KEY autoincrement)")#[用户，时间，金额，操作员，编号]
    #cu.execute("ALTER TABLE requests ADD COLUMN read INTEGER")
    #cu.execute("CREATE TABLE IF NOT EXISTS student(uid INTEGER PRIMARY KEY,name TEXT,balance REAL,cost REAL)")
    #txmnq=open(root+root+"\\config\\goodstest.txt","+a")
    #txmnq.write("hi")
    #txmnq.close()
    otmp=open(root+"\\config\\goods.txt","+r",encoding='UTF-8')
    line=otmp.readline()
    while line!="EOF" and line:
        if line=="!\n":
            line=otmp.readline()[:-1]
            break
        line=otmp.readline()
    else:
        otmp.close()
        conn.commit()
        cu.close()
        return 1
    while line!="EOF" and line:
        tmp=line.split(" ")
        k=0
        for i in range(len(tmp)):
            if not tmp[i-k]:
                tmp.pop(i-k)
                k+=1
        goodsprice[tmp[0]]=float(tmp[2])
        goods[tmp[0]]=tmp[1]
        line=otmp.readline()
    otmp.close()
    otmp=open(root+"config\\settings.txt","+r")
    line=otmp.readline()
#    while line!="EOF"and line:
#        if line=="|\n":
#            break
#        line=otmp.readline()
#    else:
#        otmp.close()
#        conn.commit()
#        cu.close()
#        return 1
#    line=otmp.readline()
    

    while line!="EOF" and line:
        opt,val=line.split(" ")
        line=otmp.readline()
        if opt=="admin_account_life":
            admin_account_life=int(val)
        elif opt=="base_rate":
            base_rate=float(val)
        elif opt=="extra_rate":
            extra_rate=float(val)
        elif opt=="order_start":
            order_start=val
        elif opt=="order_deadline":
            order_deadline=val
        elif opt=="uikit_root":
            global uikit
            uikit=val
        elif 1:
            1
    otmp.close()
    conn.commit()
    cu.close()
    return
#initialize settings
initialize()

def hash_md5(plain):
    m = hashlib.md5()  # 构建MD5对象
    m.update(plain.encode(encoding='utf-8')) #设置编码格式 并将字符串添加到MD5对象中
    cipher_md5 = m.hexdigest()  # hexdigest()将加密字符串 生成十六进制数据字符串值
    return cipher_md5
def hex_ckeck(plain,cipher):
    return hash_md5(plain.encode()).hexdigest()==cipher
app.config['SECRET_KEY'] = 'super-secret-key'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myapp.db'
#app.config['SECURITY_PASSWORD_SALT'] = 'salt'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
#app.config['SECRET_KEY'] = 'super-secret-key'
#app.config['SECURITY_PASSWORD_SALT'] = 'salt'

#db =flask_sqlalchemy.SQLAlchemy(app)

# 定义用户和角色模型
#class Role(db.Model, fs.RoleMixin):
#    id = db.Column(db.Integer(), primary_key=True)
#    name = db.Column(db.String(80), unique=True)

def set_unique_acount():
    cu=conn.cursor()
    cu.execute("update account set admin=1 where name='zhangliyang'")
    conn.commit()
    cu.close()


#class User(db.Model, fs.UserMixin):
#    id = db.Column(db.Integer(), primary_key=True)
#    email = db.Column(db.String(255), unique=True)
#    password = db.Column(db.String(255))
 #   active = db.Column(db.Boolean())
#    roles = db.relationship('Role',secondary=Role())
#    fs_uniquifier="10086"
# 设置用户数据存储
#user_datastore = fs.SQLAlchemyUserDatastore(db, User, Role)
#security = fs.Security(app, user_datastore)
#user_datastore.create_user(email='admin', password='12345',roles="admin")
#user_datastore.add_role_to_user('admin', 'admin')


@app.route('/register', methods=['GET', 'POST'])
def register():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0]!="admin":
        return flask.redirect(flask.url_for("home"))
    global current_user
    #if current_user[]!=None:
    #    return flask.redirect(flask.url_for("home"))
    form = RegisterForm()
    if form.validate_on_submit() or ( form.password.data!=None):
        if  0 and form.password.data != form.password_again.data:
            errors = 'empty submint'
            return render_template('register.html', form=form, errors=errors,uikit=uikit)
        #new_user = user_datastore.create_user(email=form.email.data, password=form.password.data)
        cu=conn.cursor()
        #return form.email.data
        cu.execute("select name from account where name=?",[(str(form.email.data))])
        N=cu.fetchone()
        if N==None:
            name=form.email.data
            uid=hash_md5(name)
            cu.execute("insert into account (uid,name,balance,cost,password,role,admin) values (?,?,0,0,?,'student',false)",(uid,name,hash_md5(form.password.data)))
            conn.commit()                                                               #若为admin则 admin=true
            cu.close()
            current_user[flask.request.access_route[-1]]=[uid,name,["student"]]
            return flask.redirect("/register")
        else:
            errors="ERROR: used name"
            return render_template('register.html', form=form, errors=errors,uikit=uikit)    
        #normal_role = user_datastore.find_role('User')
        
        #db.session.add(new_user)
        
        #user_datastore.add_role_to_user(new_user, normal_role)
        
        #fs.urils.login_user(new_user)
    return render_template('register.html', form=form,uikit=uikit)


#from flask_security import  current_user
@app.route('/login', methods=['POST', 'GET'])
def login():
    form =LoginForm()
    if form.validate_on_submit():
        #user = User.query.filter_by(email=form.email.data).first()
        #if user is None:
        #    
        #    return render_template('login.html', form=form)
        #if not user.password == form.password.data:
        #    
        #    return render_template('login.html', form=form)
        #fs.login_user(user, remember=True)
        user_input=check_password(form.username.data,form.password.data)
        if user_input==-1:
            form.errors= 'user does not exit'
            return render_template('login.html', form=form,uikit=uikit)
        if user_input:
            global current_user
            cu=conn.cursor()
            ip=flask.request.access_route[-1]
            if not user_input[1]:
                current_user[ip]=[user_input[2],form.username.data,[user_input[0]]]
                cu.execute("select name from terminals where name=?",[(form.username.data)])
                
                if cu.fetchone():
                    cu.execute("update terminals set mac='' where mac=?",[(ip)])
                    cu.execute("update terminals set mac=?,time=? where name=?",(ip,time.time(),form.username.data))
                else:
                    cu.execute("insert into terminals (mac ,role ,name,time ) values (?,?,?,?)",(flask.request.access_route[-1],user_input[0],form.username.data,time.time()))
            else:
                current_user[ip]=[user_input[2],form.username.data,[user_input[0],"admin"]]
                cu.execute("select name from terminals where name=?",[(form.username.data)])
                if cu.fetchone():
                    cu.execute("update terminals set mac='' where mac=?",[(ip)])
                    cu.execute("update terminals set mac=?,time=?,role='admin' where name=?",(ip,time.time(),form.username.data))
                    
                else:
                    cu.execute("insert into terminals (mac ,role ,name,time ) values (?,'admin',?,?)",[(flask.request.access_route[-1],form.username.data,time.time())])
            conn.commit()
            cu.close()
            #return "?"
            return flask.redirect(flask.url_for('home'))
        form.errors= 'password is not right'
    return render_template('login.html', form=form,uikit=uikit)
    #return "?"    


@app.route("/logout")
def logout():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    cu=conn.cursor()
    if ip in current_user:
        current_user.pop(ip)
    cu.execute("update terminals set mac='' where name=?",[(req[1])])
    conn.commit()
    cu.close()
    return flask.redirect(flask.url_for("login"))
ordered={}
bill_final={}
ordered_final={}
alternative_admin={}
ordered_admin={}
bill_admin={}
bill_time=""
def conclude_bill(_ordered):
    outcome={}
    for i in _ordered:
        for j in _ordered[i]:
            if j in outcome:
                outcome[j]+=_ordered[i][j]
            else:
                outcome[j]=_ordered[i][j]
    return outcome
def goods_change(alter):       #use uid  alter[origin]=uid
    global ordered_final
    ordered_final={}
    for i in ordered:
        ordered_final[i]={}
        for j in ordered[i]:
            if j in alter:
                _alter=alter[j]
                if _alter in ordered_final[i]:
                    ordered_final[i][_alter]+=ordered[i][j]
                else:
                    ordered_final[i][_alter]=ordered[i][j]
                
            else:
                if j in ordered_final[i]:
                    ordered_final[i][j]+=ordered[i][j]
                else:
                    ordered_final[i][j]=ordered[i][j]
    return
class change_form(FlaskForm):
    #goods={}
    origin=wtforms.SelectField("changed",choices=goods.items())
    alter=wtforms.SelectField("alter",choices=goods.items())
    submit=SubmitField("add")
with app.app_context():
    def identify(_mac):# db connection,cursor
        cu=conn.cursor()
        cu.execute("select * from terminals where mac =?",[_mac]) #[mac,用户组，用户名，记录时间]/算了先用IP吧
        his=cu.fetchone()
        _time=time.time()
        try:
            _method=flask.request.method
            if not isinstance(_method,str):
                _method="TypeError"
                cu.execute("insert into requests values (?,?,error,method,?)",(_time,_mac,_method))
                conn.commit()
                cu.close()
                return 0
        except:
            _method="UNKNOW"
            cu.execute("insert into requests (time,ip,name,role,method) values (?,?,'error','method',?)",(_time,_mac,_method))
            conn.commit()
            cu.close()
            return 0
        if not his:
            cu.execute("insert into requests (time,ip,name,role,method) values (?,?,'info','not logged',?)",(_time,_mac,_method))
            conn.commit()
            cu.close()
            return 0
        if his[1]=='admin':
            if 0<admin_account_life and admin_account_life<_time-his[3]:
                cu.close()
                return 0
            if update_check_in_time:
                cu.execute("update terminals set time=? where mac=?",(_time,_mac))
            cu.execute("insert into requests (time,ip,name,role,method) values (?,?,?,'admin',?)",(_time,_mac,his[2],_method))
            conn.commit()
            current_user[_mac]=[his[2],[his[1],"admin"]]
            cu.close()
            return ["admin",his[2]]
        if his[1] in ["student","shop"]:
        
            cu.execute("update terminals set time=? where mac=?",(_time,_mac))
            cu.execute("insert into requests (time,ip,name,role,method) values (?,?,?,?,?)",(_time,_mac,his[2],his[1],_method))
            conn.commit()
                #current_user[_mac]=[his[2],his[1]]
            cu.close()
            current_user[flask.request.access_route[-1]]=[his[2],[his[1]]]
            return ["student",his[2]]    
        cu.close()
        return 0
pass
def check_password(name,password):
    cu=conn.cursor()
    cu.execute("select password,role,admin,uid from account where name=?",[(name)])
    bar=cu.fetchone()
    cu.close()
    if bar==None:
        return -1
    if hash_md5(password)==bar[0]:
        return bar[1:]
    return 0


def submit_bill(_bill):
    goodslist={}
    cost=0
    for i in _bill:
        for j in _bill[i]:
            if j in goodslist:
                goodslist[j]=1
            else:
                goodslist[j]+=1
            if j>0:
                cost+=goodsprice[j]
                
    #open(root+"\\his_lists\\"+time.strftime('%Y-%m-%d', time.localtime())+".txt","+a").wirte(goodslist)
    return goodslist
def daily_settle(_bill):     #日常结算
    try:
        otmp=open("history_serves\\%s.txt"% time.strftime('%Y-%m-%d', time.localtime()),"w")
    except FileNotFoundError:
        otmp=open("history_serves\\%s.txt"% time.strftime('%Y-%m-%d', time.localtime()),"a")

    
    cu=conn.cursor()
    for i in _bill:
        cu.execute("select cost from account where name=?",[(i)])
        cost=cu.fetchone()[0]
        otmp.write("\n"+i)
        for j in _bill[i]:
            cost+=goodsprice[j]*_bill[i][j]
            otmp.write("\t %s \t %f \t %d"%(goods[j],goodsprice[j],_bill[i][j]))
        cu.execute("update account set cost=? where name=?",(cost,i))
    conn.commit()
    cu.close()
    otmp.close()
    return
def cyc_settle():          #周期结算, accout:[uid,name,balance,cost,password,role,admin]
    cu=conn.cursor()
    cu.execute("select uid,name,balance,cost from account")
    tmp=cu.fetchall()
    balance=0
    #nug=time.strftime('%Y-%m-%d', time.localtime())
    date=time.strftime('%Y-%m-%d', time.localtime())
    otmp=open(root+"bills\\%s.txt"%date ,"a")
    
    if os.path.exists(root+date+".xlsx"):
        suffix=0
        date+='-'
        while os.path.exists(date+str(suffix)):
            suffix+=1
        date+=str(suffix)
    
    #otmp=open(root+"\\bills\\day","+a")
    otmp.write("username\t\tbalance\t\tfee\n")
    import openpyxl

    # 打开工作簿
    workbook = openpyxl.Workbook()

    # 获取工作表
    sheet = workbook.active

    # 读取单元格数据
    #cell_value = sheet['A1'].value
    #print(cell_value)
    sheet["A1"],sheet["B1"],sheet["C1"],sheet["D1"]="username","balance",'cost','fee'
    row=2
    
    for i in tmp:                                       #
        fee=i[3]*base_rate
        if i[2]<0:
            fee+=i[3]*extra_rate
        elif i[3]>i[2]:
            fee+=(i[3]-i[2])*extra_rate
        balance=i[2]-i[3]-fee
        otmp.write("%s\t%f\t%f\n"%(i[1],balance,fee))
        _row=sheet[str(row)]
        _row[0].value=i[1]
        _row[1].value=str(balance)
        _row[2].value=str(i[3])
        _row[3].value=str(fee)
        row+=1
        cu.execute("update account set balance=? where name=?",(balance,i[1]))
    cu.execute("update account set cost=0")
    file_name="cyc settle\%s.xlsx"%date
    workbook.save(root+file_name)
    conn.commit()
    cu.close()
    return file_name
    
@app.route('/')
#def log_in(method=["GET","POST"]):
#    """sigh_in page"""
#    if method=="POST":
def redirect():
    if not initialized:
        initialize()
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    return flask.redirect(flask.url_for("home"))
@app.route('/home')
def home():
    """Renders the home page."""
    #if fs.current_user.is_anonymous:
    if not identify(flask.request.access_route[-1]):
        return flask.redirect(flask.url_for('login'))
    return render_template('home.html',name=current_user[flask.request.access_route[-1]][0],uikit=uikit)
@app.route("/student/<name>/history")
def check_his_bill_stu(name):
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if name!=req[1]:
        return flask.redirect("/student/%s/history"%req[1])
    cu=conn.cursor()
    cu.execute("select date,content from bills where name=?",[(name)])
    orig=cu.fetchall()[::-1]
    his={}
    for i in orig:
        tmp=i[1].split(",")
        if i[0] in his:
            k=1
            while i[0]+"-%d"%k in his:
                k+=1
            date=i[0]+"-%d"%k
        else:
            date=i[0]
        his[date]={}
        if tmp!=None:
            for j in tmp:
                item,cnt=j.split(" ")[:2]
                his[date][item]=cnt
            cu.execute("select change from bills_shop where date=?",[(date)])
            alter_orig=cu.fetchone()
            if alter_orig:
                if alter_orig[0]:
                    alter=alter_orig[0].split(",")
                    _tmp={}
                    for j in alter:
                        lack,patch=j.split(" ")[:2]
                        if lack in his[date]:
                            _tmp[lack]=patch
                    his[date]["alter"]=_tmp
    cu.close()
    return render_template("check_bill.html",goods_list=goods,goods_price=goodsprice,his=his,uikit=uikit,admin=False)
            
@app.route("/admin/bill/history",methods=["GET","POST"])
def admin_check_bill():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    his={}
    form=search_user()
    error=""
    delivery=flask.request.args.get("name")
    if delivery:
        name=delivery
        form.username.data=delivery
    name=form.username.data
    
    if name:
        cu=conn.cursor()
        cu.execute("select date,content from bills where name=?",[(name)])
        orig=cu.fetchall()[::-1]
        for i in orig:
            tmp=i[1].split(",")
            if i[0] in his:
                k=1
                while i[0]+"-%d"%k in his:
                    k+=1
                date=i[0]+"-%d"%k
            else:
                date=i[0]
            his[date]={}
            if tmp!=None:
                for j in tmp:
                    item,cnt=j.split(" ")[:2]
                    his[date][item]=cnt
                cu.execute("select change from bills_shop where date=?",[(date)])
                alter_orig=cu.fetchone()
                if alter_orig:
                    if alter_orig[0]:
                        alter=alter_orig[0].split(",")
                        _tmp={}
                        for j in alter:
                            lack,patch=j.split(" ")[:2]
                            if lack in his[date]:
                                _tmp[lack]=patch
                        his[date]["alter"]=_tmp
        cu.close()
    return render_template("check_bill_admin.html",goods_list=goods,goods_price=goodsprice,his=his,name='',form=form,uikit=uikit,admin=True)
@app.route("/student/<name>")
def order_food(name):
    global ordered
    alert=""
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0] not in ["student","admin"]:
        return flask.redirect(flask.url_for("home"))
    if name!=req[1]:
        return flask.redirect("/student/%s"%req[1])
    if not name:
        flask.redirect(flask.url_for("login"))
    if name not in ordered:
        ordered[name]={}    
    
    if not order_start<time.strftime('%H%M', time.localtime())<order_deadline:
        alert="out of time"
        return flask.render_template("order.html",goods_list=goods,goods_price=goodsprice,ordered=ordered[name],uikit=uikit,name=name,alert=alert)
    addition=flask.request.args.get('addition')
    if addition!=None:
        if addition in ordered[name]:
            ordered[name][addition]+=1
        else:
            ordered[name][addition]=1
        return flask.redirect("/student/"+name)
    remove=flask.request.args.get('minus')
    if remove!=None:
        if remove in ordered[name]:
            if ordered[name][remove]==1:
                ordered[name].pop(remove)
            else:
                ordered[name][remove]-=1
        return flask.redirect("/student/"+name)
    return flask.render_template("order.html",goods_list=goods,goods_price=goodsprice,ordered=ordered[name],uikit=uikit,name=name,alert=alert)#ordered=[uid],

#@app.route("/shop")
#def shop_page():
    
#@app.route("/admin")
#def admin_page():
@app.route("/shop/conclude",methods=["POST"])
def conclude():
    if flask.request.method=="POST":
        global bill
        bill =conclude_bill(ordered)
    return flask.redirect("/shop")

alternative={}
def save_history_bill(inp,_root="hisorty\\"):
    if not os.path.exists(_root):
        os.makedirs(_root)
    otmp=open(_root+"%s.txt"%time.strftime('%Y-%m-%d', time.localtime()),"a")
    total=0
    for i in inp:
        otmp.write(goods[i]+" %f %d\n"%(goodsprice[i],inp[i]))
        total+=goodsprice[i]*inp[i]
    otmp.write("total: %f\n"%total)
    otmp.close()
    return
def save_bill():
     num=0
     date=time.strftime("%Y-%m-%d",time.localtime())
     cu_shared.execute("select date from bills where id='0'")
     num=cu_shared.fetchone()
     if num==None:
         cu_shared.execute("insert into bills values (?,?,?,?)",("0",0,'',''))
         conn.commit()
         num=0
     else:
         num=int(num[0])
     if cu_shared.fetchone()!=None:
         k=1
         while 1:
             cu_shared.execute("select date from bills_shop where date=?",[(date+"-%d"%k)])
             if cu_shared.fetchone():
                 k+=1
             else:
                 break
         date=date+"-%d"%k
     for i in ordered:
         glist=""
         for j in ordered[i]:
             glist+="%s %d,"%(j,ordered[i][j])
         num+=1
         cu_shared.execute("insert into bills values (?,?,?,?)",(date,num,i,glist[:-1]))
     cu_shared.execute("update bills set date=? where id='0'",[(str(num))])
     conn.commit()
     return
def save_bill_shop():
     num=0
     date=time.strftime("%Y-%m-%d",time.localtime())
     cu_shared.execute("select date from bills_shop where date=?",[(date)])
     if cu_shared.fetchone()!=None:
         k=1
         while 1:
             cu_shared.execute("select date from bills_shop where date=?",[(date+"-%d"%k)])
             if cu_shared.fetchone():
                 k+=1
             else:
                 break
         date=date+"-%d"%k
     cu_shared.execute("select date from bills_shop where id='0'")
     num=cu_shared.fetchone()
     if num==None:
         cu_shared.execute("insert into bills_shop values (?,?,?,?)",("0",0,'',""))
         conn.commit()
         num=0
     else:
         num=int(num[0])
     glist=""
     for j in bill:
        glist+="%s %d,"%(j,bill[j])
     change=""
     for j in alternative:
        change+="%s %s,"%(j,alternative[j])
     num+=1   
     cu_shared.execute("insert into bills_shop values (?,?,?,?)",(date,num,glist[:-1],change[:-1]))
     cu_shared.execute("update bills_shop set date=? where id='0'",[(str(num))])
     conn.commit()
     return
@app.route("/shop/confirm")
def confirm():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0] not in ["shop","admin"]:
        return flask.redirect(flask.url_for("home"))
    global bill_final
    global bill
    global ordered
    global ordered_final
    global alternative
    global ordered_admin
    global alternative_admin
    global bill_admin
    global bill_time
    global ordered_final_admin
    con=flask.request.args.get("confirm")
    warning=''
    total=0
    if con:
        if con=="TRUE":
            if order_start<time.strftime('%H%M', time.localtime())<=order_deadline and req[0]!="admin":
                warning="not in the time"
                return flask.render_template("shop_confirm.html",list=bill_final,change_list=alternative,goods_list=goods,goods_price=goodsprice,former_list=bill,total=total,warning=warning,uikit=uikit) 
            daily_settle(ordered_final)
            for i in ordered_final:
                save_history_bill(ordered_final[i],_root="history\\%s\\"%i)
            save_history_bill(bill_final,_root="history\\bills\\")
            for i in ordered:
                save_history_bill(ordered[i],_root="history\\%s\\"%i)
            save_history_bill(bill,_root="history\\bills\\")
            ordered_admin=ordered.copy()
            ordered_final_admin=ordered_final.copy()
            alternative_admin=alternative.copy()
            bill_admin=bill.copy()
            bill_time=time.strftime('%Y-%m-%d %H:%M', time.localtime())
            save_bill()
            save_bill_shop()
            alternative={}
            ordered_final={}
            ordered={}
            bill={}
            bill_final={}
            return flask.redirect("/shop/settled")
    else:
        bill =conclude_bill(ordered)
    goods_change(alternative)
    
    bill_final=conclude_bill(ordered_final)
    
    for i in bill_final:
        total+=goodsprice[i]*bill_final[i]
    
    if order_start<time.strftime('%H%M', time.localtime())<=order_deadline:
        warning="not in the time"
    if req[0]=="admin":
        warning="admin"
    return flask.render_template("shop_confirm.html",list=bill_final,change_list=alternative,goods_list=goods,goods_price=goodsprice,former_list=bill,total=total,warning=warning,uikit=uikit) 
@app.route("/shop/settled")
def settled_page():
    return render_template("shop_settled_page.html",uikit=uikit)
@app.route("/shop",methods=["GET","POST"])
def check_bill():
    global alternative
    error=''
    alert=""
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0] not in ["shop","admin"]:
        return flask.redirect(flask.url_for("home"))
    form=change_form()
    #form.goods=goods
    if order_start<=time.strftime('%H%M', time.localtime())<=order_deadline:
        alert="not in the time"
    remove=flask.request.args.get("remove")
    if remove:
        alternative.pop(remove)
    if form.validate_on_submit() or flask.request.method=="POST":
        if form.alter.data in alternative:
            error="nest"
        elif form.origin.data==form.alter.data:
            error="repeat"
        elif form.origin.data in alternative:
            error="conflict"
        else:
            alternative[form.origin.data]=form.alter.data
    return render_template("shop.html",change_list=alternative,goods=goods,list=bill,form=form,goods_list=goods,goods_price=goodsprice,error=error,alert=alert,uikit=uikit)

@app.route("/admin")
def admin():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0] != "admin":
        return flask.redirect(flask.url_for("home"))
    return render_template("admin.html",uikit=uikit)

@app.route("/admin/bill")
def bill_view():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0] != "admin":
        return flask.redirect(flask.url_for("home"))
    cu=conn.cursor()
    cu.execute("select * from bills_shop")
    lis=cu.fetchall()
    lis=sorted(lis, key = lambda l: l[0],reverse=True)
    his={}
    for i in lis:
        ordered,alter=i[2].split(","),i[3].split(",")
        date=i[0]
        
        if ordered[0]:
            his[date]={}
            for j in ordered:
                item,cnt=j.split(" ")[:2]
                his[date][item]=cnt
            if alter:
                if alter[0]:
                    _tmp={}
                    for j in alter:
                        lack,patch=j.split(" ")[:2]
                        _tmp[lack]=patch
                    his[date]["alter"]=_tmp
    cu.close()
    return render_template("check_stu_bill.html",goods_list=goods,goods_price=goodsprice,his=his,uikit=uikit,admin=True)
    return render_template("bill.html",change_list=alternative_admin,goods=goods,list=bill_admin,goods_list=goods,goods_price=goodsprice,time=bill_time,uikit=uikit)
class search_user(FlaskForm):
    username=StringField("username",validators=[DataRequired()])
    submit = SubmitField("search")
@app.route("/ordered",methods=["POST","GET"])
def bill_guide():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0] != "admin":
        return flask.redirect(flask.url_for("home"))
    form=search_user()
    error=""
    _alter={}
    if flask.request.method=="POST":
        name=form.username.data
        if name:
            if name in ordered_admin:
                for i in alternative_admin:
                    if i in ordered_admin[name]:
                        _alter[i]=alternative_admin[i]
                cu.close()
                return flask.render_template("look_bills.html",form=form,uikit=uikit,error=error,admin=True,list=ordered_final_admin[name],change_list=_alter,goods_list=goods,goods_price=goodsprice,former_list=ordered_admin[name])
            else:
                cu=conn.cursor()
                cu.execute("select name from account where name=?",[(name)])
                tmp=cu.fetchone()
                if tmp:
                    error="%s didn't order anything"%name
                else:
                    error="username: '%s'doesn't exist"%name
                cu.close()
            
        
    return flask.render_template("look_bills.html",form=form,error=error,admin=True,list={},change_list={},goods_list=goods,goods_price=goodsprice,former_list={},uikit=uikit)
@app.route("/ordered/<name>")
def bill_check(name):
    error=""
    if name not in ordered_admin:
        cu=conn.cursor()
        cu.execute("select name from account where name=?",[(name)])
        tmp=cu.fetchone()
        if tmp:
            error="%s didn't order anything"%name
        else:
            error="username: '%s'doesn't exist"%name
        cu.close()
    else:
        _alter={}
        for i in alternative_admin:
            if i in ordered_admin:
                _alter[i]=alternative_admin[i]
    cu.close()
    return flask.render_template("look_bills.html",uikit=uikit,form={},error=error,admin=False,list=ordered_final_admin[name],change_list=_alter,goods_list=goods,goods_price=goodsprice,former_list=ordered_admin[name])
@app.route("/admin/settle")
def cyc_settle_page():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0] != "admin":
        return flask.redirect(flask.url_for("home"))
    file_name=cyc_settle()
    return flask.send_file(root+file_name,as_attachment=True)
    return flask.send_file(root+"data.db")
@app.route("/admin/accounts",methods=["GET","POST"])
def check_accounts():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0]!="admin":
        return flask.redirect(flask.url_for("home"))
    form=search_user()
    if flask.request.method=="POST":
        key=form.username.data
        cu_shared.execute('select name,balance,cost from account where name glob \"*%s*\"'%key)
        fits=cu_shared.fetchall()
        return render_template("accounts.html",lis=fits,form=form)
    cu_shared.execute("select name,balance,cost from account")
    fits=cu_shared.fetchall()
    return render_template("accounts.html",lis=fits,form=form)
@app.route("/admin/save",methods=["POST","GET"])
def save_money():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0]!="admin":
        return flask.redirect(flask.url_for("home"))
    #if current_user[]!=None:
    #    return flask.redirect(flask.url_for("home"))
    form = SaveForm()
    errors=""
    if form.validate_on_submit() or ( form.password.data!=None):
        name=form.email.data
        cu=conn.cursor()
        cu.execute("select name,balance from account where name=?",[(name)])
        N=cu.fetchone()
        if N!=None:
            if check_password(req[1],form.password.data):
                
                cu.execute("update account set balance=? where name=?",(N[1]+form.amount.data,name))
                cu.execute("insert into save_his(name,time,amount,operater) values (?,?,?,?)",(name,time.strftime("%Y-%m-%d-%H-%M-%S"),form.amount.data,req[1]))
                conn.commit()                                                               
                cu.close()
                return flask.redirect("/admin")
            else:
                errors='Uncorrect Password'
                cu.close()
                return render_template('save.html', form=form, errors=errors,uikit=uikit)  
        else:
            errors="ERROR: account doesn't exist"
            cu.close()
            return render_template('save.html', form=form, errors=errors,uikit=uikit)    
    return render_template('save.html', form=form,errors=errors,uikit=uikit)
@app.route("/admin/save/history",methods=["POST","GET"])
def check_save_history():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0]!="admin":
        return flask.redirect(flask.url_for("home"))
    form=search_user()
    delivery=flask.request.args.get("name")
    if delivery:
        name=delivery
        form.username.data=delivery
    key=form.username.data
    if form.username.data:
        cu_shared.execute('select name,amount,time,operater from save_his where name glob \"*%s*\"'%key)
        fits=cu_shared.fetchall()
        return render_template("save_his.html",lis=fits,form=form)
    cu_shared.execute("select name,amount,time,operater from save_his")
    fits=cu_shared.fetchall()
    return render_template("save_his.html",lis=fits,form=form)



#@app.route('/contact')
#def contact():
#    """Renders the contact page."""
 #   return render_template(
  #      'contact.html',
   #     title='Contact',
    #    year=datetime.now().year,
    #    message='Your contact page.'
    #)

#@app.route('/about')
#def about():
#    """Renders the about page."""
#    return render_template(
#        'about.html',
#        title='About',
#        year=datetime.now().year,
#        message='Your application description page.'
#    )
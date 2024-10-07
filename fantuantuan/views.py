"""
Routes and views for the flask application.
"""
from itertools import count
import os
from tkinter import SEL
from tokenize import group
from turtle import left
import openpyxl#须安装
import time
import hashlib
import flask
from datetime import datetime
from flask import render_template
import flask_wtf
import wtforms
from fantuantuan import app
import sqlite3
import socket
#import flask_security as fs
#import flask_login
#import flask_sqlalchemy
# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from fantuantuan.functions import *
from fantuantuan.classes import *
from fantuantuan.vars import *
sqlite3.threadsafety=2

 

initialize()


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
    ip=flask.request.environ.get('HTTP_X_REAL_IP',flask.request.remote_addr)
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
    error=""
    name=flask.request.form.get("username")
    password=flask.request.form.get("password")
    if flask.request.method=="POST":
        #user = User.query.filter_by(email=form.email.data).first()
        #if user is None:
        #    
        #    return render_template('login.html', form=form)
        #if not user.password == form.password.data:
        #    
        #    return render_template('login.html', form=form)
        #fs.login_user(user, remember=True)
        user_input=check_password(name,password)
        if user_input==-1:
            error= 'user does not exit'
            return render_template('login.html', error=error,uikit=uikit)
        if user_input:
            global current_user
            cu=conn.cursor()
            ip=flask.request.access_route[-1]
            if not user_input[1]:
                current_user[ip]=[user_input[2],name,[user_input[0]]]
                cu.execute("select name from terminals where name=?",[(name)])
                
                if cu.fetchone():
                    cu.execute("update terminals set mac='' where mac=?",[(ip)])
                    cu.execute("update terminals set mac=?,time=? where name=?",(ip,time.time(),name))
                else:
                    cu.execute("insert into terminals (mac ,role ,name,time ) values (?,?,?,?)",(flask.request.access_route[-1],user_input[0],name,time.time()))
            else:
                current_user[ip]=[user_input[2],name,[user_input[0],"admin"]]
                cu.execute("select name from terminals where name=?",[(name)])
                if cu.fetchone():
                    cu.execute("update terminals set mac='' where mac=?",[(ip)])
                    cu.execute("update terminals set mac=?,time=?,role='admin' where name=?",(ip,time.time(),name))
                    
                else:
                    cu.execute("insert into terminals (mac ,role ,name,time ) values (?,'admin',?,?)",[(flask.request.access_route[-1],name,time.time())])
            conn.commit()
            cu.close()
            return flask.redirect(flask.url_for('home'))
        error= 'password is not right'
    return render_template('login.html', error=error,uikit=uikit)
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

def conclude_bill(_ordered):
    outcome=bill_class([],[],[])
    for i in _ordered:
        for j in _ordered[i].goods_list:
            if j.goods_id=='0':
                if j.note:
                    outcome.add(j)
                    #noted.add(j)
            else:
                #if j.note:
                    #noted.add(j)
                outcome.add(j)
    outcome.get_difference()
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
                    ordered_final[i][_alter]+=ordered[i][j].num
                else:
                    ordered_final[i][_alter]=ordered[i][j].num
                
            else:
                if j in ordered_final[i]:
                    ordered_final[i][j]+=ordered[i][j].num
                else:
                    ordered_final[i][j]=ordered[i][j].num
    return

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
    x=hash_md5(password)
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
def daily_settle(_bill=bill):     #日常结算
    cu=conn.cursor()
    noted=[]
    date=time.strftime('%Y-%m-%d', time.localtime())
    for i in _bill:
        cu.execute("select cost from account where name=?",[(i)])
        cost=cu.fetchone()[0]
        cost+=_bill[i].get_changed_bill().total()
        _bill[i].save_his("bills",i)
        cu.execute("update account set cost=? where name=?",(cost,i))
        for j in _bill[i].changed_bill:
            if j.note:
                noted.append((date,i,j.goods_id,j.note,j.num))
    if noted:
        cu.executemany("insert into noted_goods (date,name,goods_id,note,num,condition) values (?,?,?,?,?,0)",noted)
        global noted_goods_processed
        noted_goods_processed=False
    conn.commit()
    cu.close()
    return
#sheduler=BlockingScheduler()
#sheduler.add_job(daily_settle,"cron",hour='4')
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
    error=""
    name=flask.request.form.get("key")
    delivery=flask.request.args.get("name")
    if delivery and (not name):
        name=delivery
    
    
    
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
    else:
        name=''
    return render_template("check_bill_admin.html",goods_list=goods,goods_price=goodsprice,his=his,name=name,uikit=uikit,admin=True,alluser=alluser)
@app.route("/student/<name>",methods=["GET","POST"])
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
        ordered[name]=bill_class([],[],[])
    
    if not order_start<time.strftime('%H%M', time.localtime())<order_deadline:
        alert="out of time"
        if name not in last_ordered:
            last_ordered[name]=bill_class([],[],[])
        return flask.render_template("order.html",goods_list=goods,goods_price=goodsprice,ordered=last_ordered[name],uikit=uikit,name=name,alert=alert,goods_group=goods_group,goods_list_for_ordering=goods_list_for_ordering)
    addition=flask.request.form.get('addition')
    try:
        if isNum(addition):
            ordered[name].add(goods_class(addition))
            #if addition in ordered[name]:
            #    ordered[name][addition].num+=1
            #else:
            #    ordered[name][addition]=[1,{}]
            #return flask.render_template("order.html",goods_list=goods,goods_price=goodsprice,ordered=ordered[name],uikit=uikit,name=name,alert=alert)
            #return flask.redirect("/student/"+name)
        add=flask.request.form.get('add')
        if isNum(add):
            ordered[name].goods_list[int(add)].num+=1
        remove=flask.request.form.get('minus')
        if isNum(remove):
            ordered[name].decline(int(remove))
            #if remove in ordered[name]:
            #    if ordered[name][remove].num==1:
            #        ordered[name].pop(remove)
            #    else:
            #        ordered[name][remove].num-=1
            #return flask.render_template("order.html",goods_list=goods,goods_price=goodsprice,ordered=ordered[name],uikit=uikit,name=name,alert=alert)
            #return flask.redirect("/student/"+name)
        note=flask.request.form.get("note")
        noted=flask.request.form.get("noted")
        if isNum(noted):
                #把点餐里其他几个传参全部改成post
            if int(noted)<len(ordered[name].goods_list):
                ordered[name].goods_list[int(noted)].note=note
            #return flask.render_template("order.html",goods_list=goods,goods_price=goodsprice,ordered=ordered[name],uikit=uikit,name=name,alert=alert)
            #return flask.redirect("/student/"+name)
    except IndexError:
        print("suspected request at /student/%s",name)
    return flask.render_template("order.html",goods_list=goods,goods_price=goodsprice,ordered=ordered[name],uikit=uikit,name=name,alert=alert,goods_group=goods_group,goods_list_for_ordering=goods_list_for_ordering)

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
             glist+="%s %d,"%(j,ordered[i][j].num)
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
def shop_confirm():
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
    
    global last_bill
    global last_ordered
    con=flask.request.args.get("confirm")
    warning=''
    total=0
    if con:
        if con=="TRUE":
            if order_start<time.strftime('%H%M', time.localtime())<=order_deadline and req[0]!="admin":
                warning="not in the time"
                return flask.render_template("shop_confirm.html",list=bill_final,change_list=alternative,goods_list=goods,goods_price=goodsprice,former_list=bill,total=total,warning=warning,uikit=uikit) 
            daily_settle(ordered)
            bill.save_his("bills_shop",req[1])
            last_ordered=ordered.copy()
            last_bill=bill_class(bill.goods_list.copy(),bill.get_changed_bill().goods_list,bill.get_difference())
            bill_class.alternative={}
            ordered={}
            bill=bill_class([],[],[])

            #ordered_admin=ordered.copy()
            #ordered_final_admin=ordered_final.copy()
            #alternative_admin=alternative.copy()
            #bill_admin=bill.copy()
            #bill_time=time.strftime('%Y-%m-%d %H:%M', time.localtime())
            #save_bill()
            #save_bill_shop()
            #alternative={}
            #ordered_final={}
            #ordered={}
            #bill={}
            #bill_final={}
            return flask.redirect("/shop/settled")
    else:
        bill =conclude_bill(ordered)
        
    #bill_final=conclude_bill(ordered_final)
    changed_bill=bill.get_changed_bill()
    if order_start<time.strftime('%H%M', time.localtime())<=order_deadline:
        warning="not in the time"
    if req[0]=="admin":
        warning="admin"
    return flask.render_template("shop_confirm.html",list=bill.changed_bill,change_list=bill.difference,goods_list=goods,goods_price=goodsprice,former_list=bill.goods_list,total=bill.total(),warning=warning,uikit=uikit) 
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
    if isNum(remove):
        try:
            bill_class.alternative.pop(remove)
            bill.get_difference()
        except IndexError:
            error ="IndexError"
    if form.validate_on_submit() or flask.request.method=="POST":
        error=bill_class.add_alter(form.origin.data,form.alter.data)
    return render_template("shop.html",change_list=bill.difference,goods=goods,list=bill.goods_list,form=form,goods_list=goods,goods_price=goodsprice,error=error,alert=alert,uikit=uikit)

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
    lis=sorted(lis, key = lambda l: l[1],reverse=True)
    his=[]
    change=[]
    date=[]
    for i in lis:
        ordered,alter=unpack(i[3]),unpack(i[4])
        date.append(i[0])
        
        if ordered[0]:
            his.append([])
            change.append([])
            for j in ordered:
                his[-1].append(j[:3])
            if alter:
                if alter[0]:
                    change[-1]=alter
    cu.close()
    return render_template("check_stu_bill.html",goods_list=goods,goods_price=goodsprice,his=his,change_list=change,date=date,uikit=uikit,admin=True)
    return render_template("bill.html",change_list=alternative_admin,goods=goods,list=bill_admin,goods_list=goods,goods_price=goodsprice,time=bill_time,uikit=uikit,notes=his_note)
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

@app.route("/admin/process_notes",methods=["GET","POST"])
def process_notes():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0] != "admin":
        return flask.redirect(flask.url_for("home"))
    global unprocessed_notes
    global noted_goods_processed
    page=flask.request.args.get("page")
    if page not in ["unprocessed","his","illegal"]:
        if noted_goods_processed:
            cu_shared.execute("select id,date,name,goods_id,note,condition,amount from noted_goods where condition=0")
            unprocessed_notes=cu_shared.fetchall()
            if unprocessed_notes:
                noted_goods_processed=False
            else:
                noted_goods_processed=True
        if noted_goods_processed:
            return flask.redirect("/admin/process_notes?page=his")
        else:
            return flask.redirect("/admin/process_notes?page=unprocessed")
    index=flask.request.form.get("index")
    if isNum(index):
        condition=flask.request.form.get("condition")
        amount=isNum(flask.request.form.get("amount"),outcome=True)
        cu_shared.execute("select condition,amount from noted_goods where id=?",[(index)])
        row=cu_shared.fetchone()
        index=int(isNum(index,outcome=True))
        if row[0]==0 and condition!=0:
            _index=search(index,unprocessed_notes,func=lambda x:x[0],ascending=False)
            if _index!=None:
                unprocessed_notes.pop(_index)
                if len(unprocessed_notes):
                    noted_goods_processed=False
                else:
                    noted_goods_processed=True
        if condition==0 and row!=0:
            cu_shared.execute("select id,date,name,goods_id,note,condition,amount from noted_goods where id=?",[(index)])
            unprocessed_notes.append(cu_shared.fetchone())
            noted_goods_processed=False
        if not amount:
            if row[1]:
                amount=row[1]
            else:
                amount=0
        cu_shared.execute("update noted_goods set condition=?,amount=? where id=?",(condition,amount,index))
    f=lambda x:x if x else "*"
    
    if page=="unprocessed":
        cu_shared.execute("select id,date,name,goods_id,note,condition,amount from noted_goods where condition=0")
        unprocessed_notes=cu_shared.fetchall()
        if unprocessed_notes:
            noted_goods_processed=False
        else:
            noted_goods_processed=True
        lis=unprocessed_notes
    elif page=="his":                 #考虑his页处理未处理的条目
        key_name=f(flask.request.form.get("key_name"))
        key_date="%s-%s-%s"%(f(flask.request.form.get("key_date_a")),f(flask.request.form.get("key_date_m")),f(flask.request.form.get("key_date_d")))# 用下拉栏
        key_goods=f(flask.request.form.get("key_goods"))
        if key_goods:
            cu_shared.execute("select id,date,name,goods_id,note,condition,amount,num from noted_goods where condition=0 and name glob :name and date glob :date and goods_id glob :goods",{"name":"*"+key_name+"*","date":"*"+key_date+"*","goods":key_goods})
            lis=sorted(cu_shared.fetchall(),key=lambda x:x[0],reverse=True)
            cu_shared.execute("select id,date,name,goods_id,note,condition,amount,num from noted_goods where condition!=0 and name glob :name and date glob :date and goods_id glob :goods",{"name":"*"+key_name+"*","date":"*"+key_date+"*","goods":key_goods})
        else:
            cu_shared.execute("select id,date,name,goods_id,note,condition,amount,num from noted_goods where condition=0 and name glob :name and date glob :date",{"name":"*"+key_name+"*","date":"*"+key_date+"*"})
            lis=sorted(cu_shared.fetchall(),key=lambda x:x[0],reverse=True)
            cu_shared.execute("select id,date,name,goods_id,note,condition,amount,num from noted_goods where condition!=0 and  name glob :name and date glob :date",{"name":"*"+key_name+"*","date":"*"+key_date+"*"})
        lis+=sorted(cu_shared.fetchall(),key=lambda x:x[0],reverse=True)
    elif page=="illegal":
        key_name=f(flask.request.form.get("key_name"))
        key_date="%s-%s-%s"%(f(flask.request.form.get("key_date_a")),f(flask.request.form.get("key_date_m")),f(flask.request.form.get("key_date_d")))# 用下拉栏
        key_goods=f(flask.request.form.get("key_goods"))
        if key_goods:
            cu_shared.execute("select id,date,name,goods_id,note,condition,amount,num from noted_goods where condition=2 and name glob :name and date glob :date and goods_id glob :goods",{"name":"*"+key_name+"*","date":"*"+key_date+"*","goods":key_goods})
        else:
            cu_shared.execute("select id,date,name,goods_id,note,condition,amount,num from noted_goods where condition=0 and name glob :name and date glob :date",{"name":"*"+key_name+"*","date":"*"+key_date+"*"})
        lis=sorted(cu_shared.fetchall(),key=lambda x:x[0],reverse=True)
    return render_template("process_notes.html",lis=lis,uikit=uikit,page=page,goods_list=goods,divided_goods=divided_goods,alluser=alluser)

@app.route("/admin/download/database")
def get_data_base():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0] != "admin":
        return flask.redirect(flask.url_for("home"))
    form =LoginForm()
    if form.validate_on_submit():
        user_input=check_password(req[1],form.password.data)
        if user_input:
            return flask.send_file(root+"data.db")
    return render_template("second_verify.html",form=form,username=False)

@app.route("/admin/accounts",methods=["GET","POST"])
def check_accounts():
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0]!="admin":
        return flask.redirect(flask.url_for("home"))
    if flask.request.method=="POST":
        key=flask.request.form.get("key")
        if key:
            cu_shared.execute('select name,balance,cost from account where name glob :key',{"key":'*'+key+'*'})
            fits=cu_shared.fetchall()
            return render_template("accounts.html",lis=fits,key=key,alluser=alluser,uikit=uikit)
    cu_shared.execute("select name,balance,cost from account")
    fits=cu_shared.fetchall()
    return render_template("accounts.html",key='',lis=fits,alluser=alluser,uikit=uikit)
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
                return flask.redirect("/admin/save")
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
    name=''
    if not req:
        return flask.redirect(flask.url_for("login"))
    if req[0]!="admin":
        return flask.redirect(flask.url_for("home"))
    key=flask.request.form.get("key")
    delivery=flask.request.args.get("name")
    if delivery and (not key):
        key=delivery
    
    if key:
        cu_shared.execute('select name,amount,time,operater from save_his where name glob :key',{"key":"*"+key+"*"})
        fits=cu_shared.fetchall()
        return render_template("save_his.html",lis=fits,name=key,alluser=alluser)
    cu_shared.execute("select name,amount,time,operater from save_his")
    fits=sorted(cu_shared.fetchall(),key=lambda x:x[2],reverse=True)
    return render_template("save_his.html",lis=fits,name=key,alluser=alluser)
@app.route("/password/<name>",methods=["GET","POST"])            #改密码的路由还没加！！！！！！！！！！！
def modify_passsword(name):
    ip = flask.request.access_route[-1]
    req= identify(ip)
    if not req:
        return flask.redirect(flask.url_for("login"))
    if name!=req[1]:
        return flask.redirect("/password/%s",req[1])
    error=""
    if flask.request.method=="POST":
        old=flask.request.form.get("old")
        if check_password(name,old):
            new=flask.request.form.get("new")
            new_again=flask.request.form.get("new_again")
            if new==new_again:
                cu=conn.cursor()
                cu.execute("update account set password=? where name=? ",(hash_md5(new),name))
                conn.commit()
                cu.close()
                return flask.redirect("/logout")
            else:
                error="two input is different"
        else:
            error="wrong password"
    return render_template("modify_password.html",error=error,uikit=uikit,name=name)

'''
@app.route('/uikit/assets/bootstrap/css/bootstrap.min.css')
def download_file():

    path = "templates\\assets\\bootstrap\\css\\bootstrap.min.css"
    return flask.send_file(path)  
@app.route('/uikit/assets/css/Login-Form-Basic-icons.css')
def download_file():

    path = "templates\\assets\\css\\Login-Form-Basic-icons.css"
    return flask.send_file(path)  
@app.route('/uikit/assets/bootstrap/js/bootstrap.min.js')
def download_file():

    path = "templates\\assets\\bootstrap\\js\\bootstrap.min.js"
    return flask.send_file(path)  
'''
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
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
from fantuantuan.classes import *
from fantuantuan.vars import *
from fantuantuan.constants import *
sqlite3.threadsafety=2

def isNum(inp,outcome=False):
    if inp:
        if isinstance(inp,str):
            try: 
                out=int(inp)
            except ValueError:
                try:
                    out=float(inp)
                except ValueError:
                    out=None
            if outcome:
                return out
            elif out!=None:
                return True
            else:
                return False
        elif isinstance(inp,(int,float)):
            if outcome:
                return inp
            else:
                return True
    elif inp==0:
        if outcome:
            return 0
        else:
            return True
    return None
def search(objective,lis,ascending=True,func=lambda x:x,cmp=lambda x,y:x>y): #rule>0则x>y =则= <则<
    left=0
    right=len(lis)
    if ascending:
        while left<right:
            mid=(left+right)>>1
            if cmp(objective,func(lis[mid])):
                right=mid-1
                continue
            if cmp(func(lis[mid]),objective):
                left=mid+1
                continue
            return mid
    else:
        while left<right:
            mid=(left+right)>>1
            if cmp(objective,func(lis[mid])):
                left=mid+1
                continue
            if cmp(func(lis[mid]),objective):
                right=mid-1
                continue
            return mid            
def pack(inp):
    row=[]
    for i in inp:
        row.append(" ".join(map(lambda x:str(x),i)))
    return ",".join(row)
def unpack(package,*type_set):
    unpacked=[]
    rows=package.split(",")
    cnt=0
    for i in rows:
        unpacked.append(i.split(' '))
        for k in range(len(type_set)):
            if k>= unpacked[cnt]:
                break
            unpacked[cnt][k]=type_set[k](unpacked[cnt][k])
        cnt+=1
    return unpacked
def hash_md5(plain):
    m = hashlib.md5()  # 构建MD5对象
    m.update(plain.encode(encoding='utf-8')) #设置编码格式 并将字符串添加到MD5对象中
    cipher_md5 = m.hexdigest()  # hexdigest()将加密字符串 生成十六进制数据字符串值
    return cipher_md5
def hex_ckeck(plain,cipher):
    return hash_md5(plain.encode()).hexdigest()==cipher
def special_operations_on_database():
    import sqlite3
    conn=sqlite3.connect("data-old.db")
    cu=conn.cursor()
    cu.execute("elect password,name from account")
    lis=cu.fetchall()
    cu.close()
    conn.close()
    conn=sqlite3.connect("data.db")
    cu.executemany("update account set password=? where name=?",lis)
    conn.commit()
    cu.close()
    conn.close()
def handle_on_db():
    cu=conn.cursor()
    cu.execute()
    conn.commit()
    cu.close()
def initialize():
    global initialized
    global goods
    global goodsprice
    global goods_group
    global admin_account_life
    global base_rate
    global extra_rate
    global order_start
    global order_deadline
    global goods_list_for_ordering
    global alluser
    global noted_goods_proccessed
    initialized=True
    cu=conn.cursor()
    cu.execute("CREATE TABLE IF NOT EXISTS account(uid TEXT PRIMARY KEY,name TEXT,balance REAL,cost REAL,password TEXT,role TEXT,admin INTEGER)")#uid name balance weekly_cost password(cipher(md5)) role admin(bool)
    cu.execute("CREATE TABLE IF NOT EXISTS terminals(mac TEXT,role TEXT,name TEXT PRIMARY KEY,time REAL)")#[mac,用户组，用户名，记录时间]
    cu.execute("CREATE TABLE IF NOT EXISTS bills(date TEXT,id INTEGER PRIMARY KEY Autoincrement,name TEXT,content TEXT,change TEXT)")#[日期，订单编号，用户名，内容（“id 个数，”）,替换（“被替换 替代，”）]
    cu.execute("CREATE TABLE IF NOT EXISTS bills_shop(date TEXT,id INTEGER PRIMARY KEY Autoincrement,name TEXT,content TEXT,change TEXT)")#[日期，订单编号，完成用户名,内容（“id 个数，”），替换（“被替换 替代，”）]
    cu.execute("CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY autoincrement,time TEXT,ip TEXT,name TEXT,role TEXT,method TEXT,read INTEGER)")#[id,时间，IP，用户名，用户组，请求方法(get,post,UNKNOW,TypeError),是否标为已读]
    cu.execute("CREATE TABLE IF NOT EXISTS save_his(name TEXT,time TEXT,amount REAL,operater TEXT,id INTEGER PRIMARY KEY autoincrement)")#[用户，时间，金额，操作员，编号]
    cu.execute("CREATE TABLE IF NOT EXISTS noted_goods(id INTEGER PRIMARY KEY autoincrement,date TEXT,name TEXT,goods_id TEXT,note TEXT,condition INTEGER,amount REAL,num INTEGER)")#[id,日期，用户，商品，备注内容，状态 (0:未读，1:合格，2:无效或违规),造成的金额]
    #cu.execute("ALTER TABLE terminals DROP COLUMN num")
    if 0:
        import sqlite3
        _root="D:\\Users\\38761\\Documents\\Visual Studio 2022\\fantuantuan\\fantuantuan\\"
        _conn=sqlite3.connect(_root+"data.db")
        _cu=conn.cursor()
        _cu.execute("drop table bills")
        _cu.execute("drop table bills_shop")
        _conn.commit()
        _cu.close()
        _conn.close()
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
        if line[-1]=="\n":
            line=line[:-1]
        tmp=line.split(" ")
        k=0
        for i in range(len(tmp)):
            if not tmp[i-k]:
                tmp.pop(i-k)
                k+=1
        goodsprice[tmp[0]]=float(tmp[2])
        goods[tmp[0]]=tmp[1]
        goods_group[tmp[0]]=tmp[3]
        if tmp[3]not in goods_group[0]:
            goods_group[0].append(tmp[3])
        if tmp[3]not in divided_goods:
            divided_goods[tmp[3]]=[tmp[0]]
        else:
            divided_goods[tmp[3]].append(tmp[0])
        line=otmp.readline()
    goods_list_for_ordering=[]
    for i in range(max(map(lambda x:list(goods_group.values()).count(x),goods_group[0]))):
        goods_list_for_ordering.append([""]*len(goods_group[0]))
    col=0
    for i in goods_group[0]:
        tmp=[]*len(goods_group[0])
        row=0
        for j in goods:
            if goods_group[j]==i:
                goods_list_for_ordering[row][col]=j
                row+=1
        col+=1
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
    cu.execute("select name from account")
    alluser=cu.fetchall()
    cu.execute("select id,date,name,goods_id,note,condition from noted_goods where condition=0")
    unprocessed_notes=cu.fetchall()
    if unprocessed_notes!=None:
        unprocessed_notes=sorted(unprocessed_notes, key = lambda l: l[0],reverse=True)
        noted_goods_processed=False
    conn.commit()
    cu.close()
    return
#initialize settings
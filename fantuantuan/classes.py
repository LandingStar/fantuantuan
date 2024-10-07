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
import sqlite3
import socket
#import flask_security as fs
#import flask_login
#import flask_sqlalchemy
# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from fantuantuan.constants import *
sqlite3.threadsafety=2

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

class LoginForm(FlaskForm):
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
class change_form(FlaskForm):
    #goods={}
    origin=wtforms.SelectField("changed",choices=goods.items())
    alter=wtforms.SelectField("alter",choices=goods.items())
    submit=SubmitField("add")
class goods_class():
    goods_id='0'
    num=0
    attributes={}
    note=''
    def __init__(self,goods_id,num=1,attributes=[].copy(),note=''):
        self.goods_id=goods_id
        self.num=num
        self.attributes=attributes
        self.note=note
    def __eq__(self,other):
        return self.goods_id==other.goods_id and self.attributes==other.attributes and self.note==other.note
    def __add__(self,other):
        if self!=other:
            return False
        return goods_class(self.goods_id,self.num+other.num,self.attributes,self.note)
    def __sub__(self,other):
        if self!=other:
            return False
        return goods_class(self.goods_id,self.num-other.num,self.attributes,self.note)
    def expense(self):
        if self.goods_id!='0' and self.goods_id in goodsprice:
            return self.num*goodsprice[self.goods_id]
        else:
            return -1


class bill_class():
    goods_list=[]
    alternative={}#沿用原结构
    changed_bill=[]
    difference=[]
    def __init__(self,goods_list=[].copy(),changed_bill=[].copy(),difference=[].copy()):
        self.goods_list=goods_list
        self.changed_bill=changed_bill
        self.difference=difference
        #self.changed_bill=self.get_changed_bill()
    def __eq__(self,other):
        return self.goods_list==other.goods_list
    def __len__(self):
        return len(self.goods_list)
    def __add__(self,other):
        outcome=bill_class([],[],[])
        for i in self.goods_list+other.goods_list:
            outcome.add(i)
        outcome.get_changed_bill()
        outcome.get_difference()
        return outcome
    def total(self):
        tol=0
        self.get_changed_bill()
        for i in self.changed_bill:
            tol+=i.expense()
        return tol
    def add(self,addition=goods_class(0,0,{},"")):
        lenth=len(self.goods_list)
        for i in range(lenth):
            if self.goods_list[i]==addition:
                self.goods_list[i]+=addition
                return 1
        self.goods_list.append(addition)
        return 0
    def drop(self,_id):
        self.goods_list.pop(_id)
    def decline(self,_id,num=1):
        if self.goods_list[_id].num<=num:
            self.drop(_id)
            return 1
        self.goods_list[_id].num-=num
        return 0
    def get_changed_bill(self): #返回替换后的订单
        _ordered_final=bill_class([],[],[])
        _alter=goods_class('',0,{},0)
        for j in self.goods_list:
            if j.goods_id in bill_class.alternative:
                _alter=goods_class(bill_class.alternative[j.goods_id],j.num,[],'')
                _ordered_final.add(_alter)
            else:
                _ordered_final.add(j)
        self.changed_bill=_ordered_final.goods_list.copy()
        return _ordered_final
    def get_list(self):
        outcome=[]
        for i in self.goods_list:
            outcome.append((i.goods_id,i.num,i.note))
        return outcome
    def get_final_list(self):
        outcome=[]
        for i in self.changed_bill:
            outcome.append((i.goods_id,i.num,i.note))
        return outcome
    def get_difference(self): #返回产生的替换[[被替代，替代品，数目]]
        _alter=[]
        
        for i in bill_class.alternative:
            flg=False
            for j in self.goods_list:
                if j.goods_id==i:
                    flg=True
                    _alter.append((i,bill_class.alternative[i],j.num)) #goods_class(bill_class.alternative[i],j.num,[],'')
            if not flg:
                _alter.append((i,bill_class.alternative[i],0))
        self.difference=_alter.copy()
        return _alter
    def add_alter(self,lack,patch):
        if lack in bill_class.alternative:
            return "conflict"
        elif lack==patch:
            return "repeat"
        elif patch in bill_class.alternative:
            return "nest"
        bill_class.alternative[lack]=patch
        self.get_difference()
        return 0
    def save_his(self,table,name):
        date=time.strftime("%Y-%m-%d",time.localtime())
       # try:
        if 1: 
            if table=="bills":
                cu_shared.execute("insert into bills (date,name,content,change) values (?,?,?,?)",(date,name,pack(self.get_list()),pack(self.difference)))
            elif table=="bills_shop":
                cu_shared.execute("insert into bills_shop (date,name,content,change) values (?,?,?,?)",(date,name,pack(self.get_list()),pack(self.difference)))
            #student [日期，订单编号，用户名，内容（“id 个数 备注，”）,替换（“被替换 替代，”）]
            #shop [日期，订单编号，完成用户名，内容（“id 个数 备注，”）,替换（“被替换 替代，”）]
            conn.commit()
            return 0
       # except sqlite3.OperationalError:
       #     return "table doesn't exist"
bill=bill_class([],[],[])
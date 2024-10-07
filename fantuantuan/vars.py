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
from fantuantuan.classes import bill_class
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



current_user={}#current_user=[uid,"name",["role"]]

#app.context_processor(goods_group)
#app.context_processor(goods)
#app.context_processor(goodsprice)
ordered={}#ordered[name][goods_uid]=cnt -->ordered[name][row]=goods_class
note={}#note[name][goods_uid]=note_for_good
initialized=False
ordered_final_admin={}
last_ordered={}
last_bill=[]
alluser=[]



noted=[]
unprocessed_notes=[]
noted_goods_processed=True

ordered={}
bill_final={}
ordered_final={}
alternative_admin={}
ordered_admin={}
bill_admin={}
bill_time=""

import sqlite3
root="D:\\Users\\38761\\Documents\\Visual Studio 2022\\fantuantuan\\fantuantuan\\"
#ner=flask.request.get('http://myip.ipip.net', timeout=5).text()
uikit="D:\\Users\\38761\\Documents\\Visual Studio 2022\\fantuantuan\\fantuantuan\\uikit\\"
uikit="127.0.0.1/uikit/"
conn=sqlite3.connect(root+"data.db", check_same_thread=False)
cu_shared=conn.cursor()
admin_account_life=-1#admin account 登录保持时长
update_check_in_time=0 #是否当访问时更新一般用户teminal数据
base_rate=0.07
extra_rate=0.05
goodsprice={}  #good[uid]=price
goods={}   #good[uid]=品名
divided_goods={} #divided_goods[组名]=id
goods_group={}#goods_group[uid]=组名 goods_group[0]=[所有组名] 
goods_group[0]=[]
goods_list_for_ordering=[]#[[组一元素，组二元素...]]
order_start="0650"
order_deadline="0850"
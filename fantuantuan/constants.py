import sqlite3
root="D:\\Users\\38761\\Documents\\Visual Studio 2022\\fantuantuan\\fantuantuan\\"
#ner=flask.request.get('http://myip.ipip.net', timeout=5).text()
uikit="D:\\Users\\38761\\Documents\\Visual Studio 2022\\fantuantuan\\fantuantuan\\uikit\\"
uikit="127.0.0.1/uikit/"
conn=sqlite3.connect(root+"data.db", check_same_thread=False)
cu_shared=conn.cursor()
admin_account_life=-1#admin account ��¼����ʱ��
update_check_in_time=0 #�Ƿ񵱷���ʱ����һ���û�teminal����
base_rate=0.07
extra_rate=0.05
goodsprice={}  #good[uid]=price
goods={}   #good[uid]=Ʒ��
divided_goods={} #divided_goods[����]=id
goods_group={}#goods_group[uid]=���� goods_group[0]=[��������] 
goods_group[0]=[]
goods_list_for_ordering=[]#[[��һԪ�أ����Ԫ��...]]
order_start="0650"
order_deadline="0850"
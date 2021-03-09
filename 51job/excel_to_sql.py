# --*-- coding: utf-8 --*--
import pandas as pd
import pymysql

# 数据从xlsx文件读取
data = pd.read_excel('data.xlsx',engine = 'openpyxl')
#连接数据库
db = pymysql.connect(host='localhost',port=3306,user='root',password='root',db='test')
cursor = db.cursor()

# 不存在表则新建表
try:
    cursor.execute('create table 51job( 职位 text,工资 varchar(100),地区 varchar(100)，经验 varchar(100),学历 varchar(100),招聘人数 varchar(100),发布时间 varchar(100),英语要求 varchar(100),福利标签  varchar(100),职位信息  text,上班地址  text, 公司名称 varchar(100),公司性质 varchar(100),公司规模 varchar(100),公司行业 varchar(100), 公司信息 text')
except:
        print('已存在的表')
# 信息存入mysql(mariadb)，若是用之前的excel需要从第二行开始（第一行为标题）
query = 'insert into 51job(职位,工资,地区 ,经验 ,学历 ,招聘人数 ,发布时间 ,英语要求 ,福利标签  ,职位信息  ,上班地址  , 公司名称,公司性质,公司规模 ,公司行业 , 公司信息 ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
for i in range(0,len(data)):
    职位=data.iloc[i,0]
    工资=data.iloc[i,1]
    地区=data.iloc[i,2]
    经验=data.iloc[i,3]
    学历=data.iloc[i,4]
    招聘人数=data.iloc[i,5]
    发布时间=data.iloc[i,6]
    英语要求=data.iloc[i,7]
    福利标签=data.iloc[i,8]
    职位信息=data.iloc[i,9]
    上班地址=data.iloc[i,10]
    公司名称=data.iloc[i,11]
    公司性质=data.iloc[i,12]
    公司规模=data.iloc[i,13]
    公司行业=data.iloc[i,14]
    公司信息=data.iloc[i,15]
    values = (str(职位),str(工资),str(地区),str(经验),str(学历) ,str(招聘人数) ,str(发布时间) ,str(英语要求) ,str(福利标签) ,str(职位信息) ,str(上班地址) ,str(公司名称),str(公司性质),str(公司规模) ,str(公司行业) ,str(公司信息) )
    cursor.execute(query,values)
cursor.close()
db.commit()
print("数据导入成功")
db.close()
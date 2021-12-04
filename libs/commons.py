import mysql.connector
from configparser import ConfigParser
import datetime

#根据配置文件中的db配置，连接数据库
def db_connect():
    #读取配置文件中的数据配置
    cfg = ConfigParser()
    cfg.read('./config.ini')
    db_host = cfg.get('database','host')
    db_user = cfg.get('database','user')
    db_passwords = cfg.get('database','passwords')
    
    #连接数据库
    mydb = mysql.connector.connect(
            host = db_host,
            user = db_user,
            passwd = db_passwords
            )
    return mydb

#根据各symbol method拉取数据的格式，入库到对应的表中
def insert_historical_original_data_to_db(symbol_name,data_list,interval,db):
    source_data_db = db
    source_data_cursor = source_data_db.cursor()
    #根据symbol_name及interval生成table name,按月分表
    today = datetime.datetime.today()
    year = today.year
    month=today.month
    table_name = 'original_data_source.'+symbol_name+'_'+interval+'_original_data_'+str(year)+str(month)
    #建立对应数据表
    create_table_sql = 'create table IF NOT EXISTS '+table_name+'  like original_data_source.single_symbol_original_data_template'
    source_data_cursor.execute(create_table_sql)

    #生成模版sql
    insert_source_data_template_sql = 'insert into '+table_name+'(symbol_name,ts,price_open,price_hgih,price_low,price_closed) values(%s,%s,%s,%s,%s,%s)'

    print(insert_source_data_template_sql)
    print(data_list)

    #通过executemany来批量执行语句
    n=source_data_cursor.executemany(insert_source_data_template_sql,data_list)
    db.commit()
    db.close()

    

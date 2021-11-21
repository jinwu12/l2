import mysql.connector
from configparser import ConfigParser

def db_connect():
    #读取配置文件中的数据配置
    cfg = ConfigParser()
    cfg.read('config.ini')
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


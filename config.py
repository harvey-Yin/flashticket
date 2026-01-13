# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # 数据库配置：mysql+pymysql://用户名:密码@地址:端口/数据库名
    # 请修改为你自己的 MySQL 信息
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:737602/WXx@localhost:3306/flashticket_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True # 开发阶段开启，会在控制台打印 SQL 语句，方便学习
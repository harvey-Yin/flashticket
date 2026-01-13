# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# 初始化插件（尚未绑定到具体 App）
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 绑定插件
    db.init_app(app)

    # 注册上下文，确保模型被加载
    with app.app_context():
        from . import models
        # 开发阶段直接创建表，生产环境通常使用 Flask-Migrate
        db.create_all() 
        
        # 为了方便调试，如果没有票，我们自动加一张测试票
        if not models.Ticket.query.first():
            print("初始化测试数据...")
            demo_ticket = models.Ticket(name="Python高并发讲座", price=100, total_count=50, remaining_count=50)
            db.session.add(demo_ticket)
            db.session.commit()

    return app
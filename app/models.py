# app/models.py
from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    # 实际生产中不存明文密码，这里简化，后续我们加 Hash
    password = db.Column(db.String(128)) 
    orders = db.relationship('Order', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # 比如 "周杰伦2026演唱会"
    price = db.Column(db.Float, nullable=False)
    total_count = db.Column(db.Integer, nullable=False) # 总票数
    remaining_count = db.Column(db.Integer, nullable=False) # 剩余票数 (高并发核心字段)

    def __repr__(self):
        return f'<Ticket {self.name} 剩余:{self.remaining_count}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    status = db.Column(db.Integer, default=0) # 0: 待支付, 1: 已支付, 2: 已取消
    create_time = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Order {self.id} Status:{self.status}>'
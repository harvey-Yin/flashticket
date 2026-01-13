# app/routes.py
from flask import Blueprint, jsonify, request
from . import db
from .models import User, Ticket, Order
import time

# 1. 创建蓝图 (名为 'main')
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """查看所有演出票"""
    tickets = Ticket.query.all()
    # 简单的列表推导式，把对象转成字典
    return jsonify([{
        'id': t.id, 
        'name': t.name, 
        'remaining_count': t.remaining_count
    } for t in tickets])

@bp.route('/init_user', methods=['POST'])
def init_user():
    """初始化一个用户（为了方便测试）"""
    username = request.json.get('username', 'test_user')
    if not User.query.filter_by(username=username).first():
        user = User(username=username, password='123')
        db.session.add(user)
        db.session.commit()
        return jsonify({'msg': f'用户 {username} 创建成功'})
    return jsonify({'msg': f'用户 {username} 已存在'})

@bp.route('/buy', methods=['POST'])
def buy_ticket():
    """
    【核心接口】有并发问题的抢票逻辑
    """
    user_id = request.json.get('user_id', 1) # 默认使用 ID 为 1 的用户
    ticket_id = request.json.get('ticket_id', 1)
    
    # 1. 查询库存
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({'msg': '票不存在'}), 404
        
    # 2. 检查是否有票
    if ticket.remaining_count > 0:
        # === 模拟网络延迟或业务处理时间 ===
        # 在高并发下，这 0.1 秒极其致命
        # 这意味着：线程 A 查到有票，歇了 0.1 秒；
        # 在这 0.1 秒内，线程 B 也查了，发现也有票（因为 A 还没减呢）
        time.sleep(0.1) 
        # ================================

        # 3. 扣减库存
        ticket.remaining_count -= 1
        
        # 4. 生成订单
        order = Order(user_id=user_id, ticket_id=ticket_id)
        db.session.add(order)
        
        # 5. 提交事务
        db.session.commit()
        return jsonify({'msg': '抢票成功!', 'remaining': ticket.remaining_count})
    else:
        return jsonify({'msg': '手慢无，票卖完了'}), 400
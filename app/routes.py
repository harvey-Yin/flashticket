# app/routes.py
from flask import Blueprint, jsonify, request
from . import db
from .models import User, Ticket, Order
import redis
import time

# 1. 创建蓝图 (名为 'main')
bp = Blueprint('main', __name__)

# 连接 Redis 连接池 (生产环境通常放在 config 里)
pool = redis.ConnectionPool(host='redis', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)

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
    【Redis 优化版】高并发抢票接口
    """
    user_id = request.json.get('user_id')
    ticket_id = request.json.get('ticket_id', 1)
    
    redis_key = f'ticket_stock:{ticket_id}'

    # === 核心优化：Redis 原子扣减 ===
    # dect() 操作是原子的，它会把 key 的值减 1，并返回减完后的结果
    # 比如原来是 5，decr 后变成 4，stock_now 就是 4
    stock_now = r.decr(redis_key)
    
    if stock_now >= 0:
        # 抢到了！(Redis 层面认可了)
        
        # 模拟业务耗时 (现在就算 sleep 10秒也不会超卖，因为 Redis 已经扣完了)
        time.sleep(0.1) 
        
        try:
            # 异步写入 MySQL (实际生产中通常是用消息队列，这里简化为同步写入)
            # 注意：这里如果 MySQL 挂了，就会出现数据不一致（缓存扣了，库里没单）
            # 这就是后续我们要解决的“最终一致性”问题
            order = Order(user_id=user_id, ticket_id=ticket_id)
            db.session.add(order)
            
            # 同时更新 MySQL 的库存用于展示 (可选，或者定时同步)
            # 这里我们为了演示，还是用 Update 语句，但逻辑已经变了
            # 我们不需要判断 remaining_count > 0，因为 Redis 已经保镖了
            ticket = db.session.get(Ticket, ticket_id)
            ticket.remaining_count -= 1 
            
            db.session.commit()
            return jsonify({'msg': '抢票成功!', 'remaining': stock_now})
            
        except Exception as e:
            # 如果 MySQL 写入失败（比如刚才的死锁），我们需要把 Redis 的库存加回去（回滚）
            r.incr(redis_key)
            db.session.rollback()
            return jsonify({'msg': f'系统繁忙: {str(e)}'}), 500
            
    else:
        # 没抢到 (stock_now 变成了 -1, -2...)
        # 因为 decr 已经减成负数了，不需要再减，但为了库存显示好看，通常也不加回去，
        # 或者仅仅是告诉用户卖完了。
        return jsonify({'msg': '手慢无，票卖完了'}), 400
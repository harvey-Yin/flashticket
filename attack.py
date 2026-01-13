# attack.py
import requests
import threading
import time

# 目标地址
BASE_URL = "http://127.0.0.1:5000"

def init_data():
    """初始化数据：重置库存为 5 张"""
    # 这里我们为了方便，稍微手动去数据库改一下，或者写个临时逻辑
    # 既然我们没有写重置接口，请手动去 MySQL 执行：
    # UPDATE tickets SET remaining_count = 5 WHERE id = 1;
    # DELETE FROM orders;
    print(">>> 请确保数据库里 Ticket(id=1) 的 remaining_count 是 5")
    print(">>> 请确保 flashticket 系统已经启动")
    time.sleep(1)

def buy_task(user_id):
    """模拟一个用户抢票"""
    url = f"{BASE_URL}/buy"
    # 模拟不同用户 ID
    data = {"user_id": user_id, "ticket_id": 1}
    
    try:
        res = requests.post(url, json=data)
        print(f"用户 {user_id} 请求结果: {res.text} [状态码: {res.status_code}]")
    except Exception as e:
        print(f"用户 {user_id} 请求失败: {e}")

def run_attack():
    threads = []
    print("--- 开始高并发抢票 ---")
    for i in range(10):
        # === 修改点开始 ===
        # 原来是: args=(f"user_{i}",)  <-- 这是一个字符串，导致了报错
        # 改为: args=(1,)             <-- 使用整数 1 (假设数据库里已有 ID=1 的用户)
        # 即使是同一个人发起 10 次并发请求，也能触发超卖 bug
        t = threading.Thread(target=buy_task, args=(1,)) 
        # === 修改点结束 ===
        
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    
    print("--- 抢票结束 ---")


if __name__ == '__main__':
    # 注意：运行脚本前，请先手动去数据库把 remaining_count 改成 5
    run_attack()
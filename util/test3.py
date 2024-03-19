import redis

# 连接到 Redis 服务器
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# 在收到网络请求时，重置会话的过期时间并存储会话ID到 Redis 中
def handle_request(session_id):
    # 处理网络请求
    # ...

    # 收到请求后，重置会话的过期时间
    reset_session_expiry(session_id)

    # 将会话ID 存储到 Redis 中
    redis_client.set(session_id, 'active', ex=3600)  # 设置过期时间为3600秒，根据需要调整

# 在收到网络请求时，重置会话的过期时间
def reset_session_expiry(session_id):
    redis_client.expire(session_id, 3600)  # 重置过期时间为3600秒，根据需要调整

# 判断会话是否存在
def is_session_exist(session_id):
    return redis_client.exists(session_id)

# 示例请求处理
session_id = 'your_session_id_from_request'
handle_request(session_id)
print(is_session_exist(session_id))

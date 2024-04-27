import uuid
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


class Session:
    sessions = {}  # 存储会话对象的字典

    def __init__(self, session_id):
        self.session_id = session_id
        self.data = {}  # 存储会话数据的字典

    def set(self, key, value):
        self.is_session_active()
        self.data[key] = value

    def get(self, key):
        self.is_session_active()
        return self.data.get(key)

    def delete(self, key):
        self.is_session_active()
        if key in self.data:
            del self.data[key]

    @classmethod
    def create_session(cls):
        session_id = str(uuid.uuid4())
        cls.sessions[session_id] = cls(session_id)
        # 将会话 ID 存储到 Redis
        redis_client.set(session_id, 'active', ex=3600)
        return cls.sessions[session_id]

    @classmethod
    def is_session_exist(cls, session_id):
        redis_client.expire(session_id, 3600)
        return redis_client.exists(session_id)

    def is_session_active(self):
        redis_client.expire(self.session_id, 3600)
        return redis_client.exists(self.session_id)

    @classmethod
    def get_session_by_id(cls, session_id):
        if cls.is_session_exist(session_id):
            return cls.sessions.get(session_id)
        else:
            return None


if __name__ == '__main__':
    session = Session.create_session()
    session = Session.get_session_by_id(session.session_id)
    session.set('username', 'example_user')
    session.set('user_id', 12345)
    print(session.session_id)  # Output: True
    print(session.get('username'))  # Output: example_user
    print(session.get('user_id'))  # Output: 12345

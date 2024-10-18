import uuid
import time
from surf.appsGlobal import get_logger

logger = get_logger('session')


class Session:
    sessions = {}  # 存储会话对象的字典
    expiration_times = {}  # 存储每个会话的过期时间

    def __init__(self, session_id):
        self.session_id = session_id
        self.data = {}  # 存储会话数据的字典

    def set(self, key, value):
        self.is_session_active()
        self.data[key] = value
        for session_id, session in self.sessions.items():
            logger.info(f"session:{session_id}'s info: {session.data}")
            logger.info(f"")

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
        cls.expiration_times[session_id] = time.time() + 3600  # 设置过期时间为1小时
        return cls.sessions[session_id]

    @classmethod
    def is_session_exist(cls, session_id):
        # 检查会话是否存在以及是否过期
        if session_id in cls.expiration_times:
            if time.time() < cls.expiration_times[session_id]:
                # 更新过期时间
                cls.expiration_times[session_id] = time.time() + 3600
                return True
            else:
                # 会话已过期，删除
                cls.delete_session(session_id)
                return False
        return False

    def is_session_active(self):
        flag = self.is_session_exist(self.session_id)
        if not flag:
            del self.sessions[self.session_id]
        return flag

    @classmethod
    def get_session_by_id(cls, session_id):
        if cls.is_session_exist(session_id):
            return cls.sessions.get(session_id)
        else:
            return None

    @classmethod
    def delete_session(cls, session_id):
        if session_id in cls.sessions:
            del cls.sessions[session_id]
        if session_id in cls.expiration_times:
            del cls.expiration_times[session_id]


if __name__ == '__main__':
    session = Session.create_session()
    session = Session.get_session_by_id(session.session_id)
    session.set('username', 'example_user')
    session.set('user_id', 12345)
    print(session.session_id)  # 输出会话ID
    print(session.get('username'))  # 输出: example_user
    print(session.get('user_id'))  # 输出: 12345

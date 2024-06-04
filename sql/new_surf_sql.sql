CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- 确保扩展已安装

CREATE OR REPLACE FUNCTION generate_random_nickname() RETURNS VARCHAR(20) AS $$
BEGIN
    RETURN md5(random()::text);
END;
$$ LANGUAGE plpgsql;

DROP TABLE IF EXISTS t_channel_chats;
DROP TABLE IF EXISTS t_channel_members;
DROP TABLE IF EXISTS t_channels;
DROP TABLE IF EXISTS t_channel_groups;
DROP TABLE IF EXISTS t_audit_logs;
DROP TABLE IF EXISTS t_permissions;
DROP TABLE IF EXISTS t_server_members;
DROP TABLE IF EXISTS t_roles;
DROP TABLE IF EXISTS t_servers;
DROP TABLE IF EXISTS t_user_friends;
DROP TABLE IF EXISTS t_users;
DROP TABLE IF EXISTS t_user_roles;

CREATE TABLE t_users
(
    c_user_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_nickname VARCHAR NOT NULL DEFAULT generate_random_nickname(),
    c_public_key VARCHAR,
    c_user_info jsonb DEFAULT '{}'
);

CREATE TABLE t_user_friends (
    c_user_id VARCHAR(36) NOT NULL,
    c_friend_id VARCHAR(36) NOT NULL,
    c_status VARCHAR(10) CHECK (c_status IN ('pending', 'accepted', 'blocked')),
    c_create_time BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
    PRIMARY KEY (c_user_id, c_friend_id),
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id) ON DELETE CASCADE,
    FOREIGN KEY (c_friend_id) REFERENCES t_users(c_user_id) ON DELETE CASCADE
);

CREATE TABLE t_servers(
    c_server_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_description TEXT,
    c_name VARCHAR NOT NULL DEFAULT generate_random_nickname(),
    c_owner_id VARCHAR(36) NOT NULL,
    c_create_time BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
    c_icon_url VARCHAR,
    c_is_active BOOLEAN NOT NULL DEFAULT TRUE,
    c_is_private BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE t_channel_groups(
    c_group_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_server_id VARCHAR(36) NOT NULL,
    c_group_name VARCHAR NOT NULL,
    FOREIGN KEY (c_server_id) REFERENCES t_servers(c_server_id) ON DELETE CASCADE
);

CREATE TABLE t_channels (
    c_channel_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_group_id VARCHAR(36) NOT NULL,
    c_name VARCHAR NOT NULL,
    c_type VARCHAR(10) CHECK (c_type IN ('text', 'voice')) NOT NULL,
    c_description TEXT,
    c_create_by VARCHAR(36) NOT NULL,
    c_create_time BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
    c_max_members INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (c_group_id) REFERENCES t_channel_groups(c_group_id) ON DELETE CASCADE
);

CREATE TABLE t_roles (
    c_role_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_server_id VARCHAR(36) NOT NULL,
    c_name VARCHAR NOT NULL,
    c_permissions jsonb NOT NULL default '[1,2,3]',
    FOREIGN KEY (c_server_id) REFERENCES t_servers(c_server_id) ON DELETE CASCADE
);

CREATE TABLE t_server_members (
    c_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_server_id VARCHAR(36) NOT NULL,
    c_user_id VARCHAR(36) NOT NULL,
    FOREIGN KEY (c_server_id) REFERENCES t_servers(c_server_id) ON DELETE CASCADE,
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id) ON DELETE CASCADE
);

CREATE TABLE t_permissions (
    c_permission_id INTEGER PRIMARY KEY,
    c_description TEXT NOT NULL
);

CREATE TABLE t_audit_logs (
    c_log_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_user_id VARCHAR(36) NOT NULL,
    c_action TEXT NOT NULL,
    c_description TEXT,
    c_timestamp BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id) ON DELETE CASCADE
);

CREATE TABLE t_channel_members (
    c_channel_id VARCHAR(36) NOT NULL,
    c_user_id VARCHAR(36) NOT NULL,
    c_permissions INTEGER NOT NULL,
    PRIMARY KEY (c_channel_id, c_user_id),
    FOREIGN KEY (c_channel_id) REFERENCES t_channels(c_channel_id) ON DELETE CASCADE,
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id) ON DELETE CASCADE
);

CREATE TABLE t_channel_chats (
    c_chat_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_channel_id VARCHAR(36) NOT NULL,
    c_status INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (c_channel_id) REFERENCES t_channels(c_channel_id) ON DELETE CASCADE
);
COMMENT ON column t_channel_chats.c_status is '-1->撤回 0->未撤回';

CREATE TABLE t_user_roles (
    c_user_id VARCHAR(36),
    c_role_id VARCHAR(36),
    c_server_id VARCHAR(36),
    PRIMARY KEY (c_user_id, c_role_id, c_server_id),
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id) ON DELETE CASCADE,
    FOREIGN KEY (c_role_id) REFERENCES t_roles(c_role_id) ON DELETE CASCADE,
    FOREIGN KEY (c_server_id) REFERENCES t_servers(c_server_id) ON DELETE CASCADE
);

-- 为用户ID和好友ID创建索引以优化查找性能
CREATE INDEX idx_user_friends_user_id ON t_user_friends (c_user_id);
CREATE INDEX idx_user_friends_friend_id ON t_user_friends (c_friend_id);

-- 创建复合索引以优化特定查询，如检索用户所有待处理的好友请求
CREATE INDEX idx_user_friends_status ON t_user_friends (c_user_id, c_status);

-- 为用户ID创建索引
CREATE INDEX idx_user_id ON t_users (c_user_id);
-- 为服务器ID创建索引
CREATE INDEX idx_server_id ON t_servers (c_server_id);
CREATE INDEX idx_server_id_on_members ON t_server_members (c_server_id);
CREATE INDEX idx_server_id_on_channel_groups ON t_channel_groups (c_server_id);
CREATE INDEX idx_server_id_on_roles ON t_roles (c_server_id);
-- 为频道分组ID创建索引
CREATE INDEX idx_channel_group_id ON t_channel_groups (c_group_id);
CREATE INDEX idx_channel_group_id_on_channels ON t_channels (c_group_id);
-- 为频道ID创建索引
CREATE INDEX idx_channel_id ON t_channels (c_channel_id);

CREATE INDEX idx_audit_logs_timestamp ON t_audit_logs (c_timestamp);

CREATE INDEX idx_message_type ON t_channel_chats (c_chat_id);
CREATE INDEX idx_channel_id_on_messages ON t_channel_chats (c_channel_id);

CREATE OR REPLACE FUNCTION check_permissions_exist()
RETURNS TRIGGER AS $$
DECLARE
    permission_id INT;
BEGIN
    -- 遍历 JSONB 数组中的每个元素
    FOR permission_id IN SELECT jsonb_array_elements_text(NEW.c_permissions)::int
    LOOP
        -- 检查元素是否存在于 t_permissions 表中
        IF NOT EXISTS (SELECT 1 FROM t_permissions WHERE c_permission_id = permission_id) THEN
            RAISE EXCEPTION 'Permission ID % does not exist in t_permissions.', permission_id;
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_permissions
BEFORE INSERT OR UPDATE ON t_roles
FOR EACH ROW EXECUTE FUNCTION check_permissions_exist();

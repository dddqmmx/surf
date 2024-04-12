-- create database surf;
-- \c surf;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- 确保扩展已安装



CREATE OR REPLACE FUNCTION generate_random_nickname() RETURNS VARCHAR(20) AS $$
BEGIN
    RETURN md5(random()::text);
END;
$$ LANGUAGE plpgsql;

DROP TABLE IF EXISTS t_users;
CREATE TABLE t_users
(
    c_user_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_nickname VARCHAR NOT NULL DEFAULT generate_random_nickname(),
    c_public_key VARCHAR,
    c_user_info jsonb
);

DROP TABLE IF EXISTS t_user_friends;
CREATE TABLE t_user_friends (
    c_user_id VARCHAR(36) NOT NULL,
    c_friend_id VARCHAR(36) NOT NULL,
    c_status VARCHAR(10) CHECK (c_status IN ('pending', 'accepted', 'blocked')),
    c_create_time BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
    PRIMARY KEY (c_user_id, c_friend_id),
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id) ON DELETE CASCADE,
    FOREIGN KEY (c_friend_id) REFERENCES t_users(c_user_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS t_servers;
CREATE TABLE t_servers(
    c_server_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_description TEXT,
    c_name VARCHAR NOT NULL DEFAULT generate_random_nickname(),
    c_owner_id VARCHAR(32) NOT NULL,
    c_create_time BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
    c_icon_url VARCHAR,
    c_is_active BOOLEAN NOT NULL DEFAULT TRUE,
    c_is_private BOOLEAN NOT NULL DEFAULT TRUE
);


DROP TABLE IF EXISTS t_channels;
CREATE TABLE t_channels (
    c_channel_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_server_id VARCHAR(36) NOT NULL,
    c_name VARCHAR NOT NULL,
    c_type VARCHAR(10) CHECK (c_type IN ('text', 'voice')) NOT NULL,
    c_description TEXT,
    c_create_by VARCHAR(32) NOT NULL,
    c_create_time BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
    FOREIGN KEY (c_server_id) REFERENCES t_servers(c_server_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS t_server_members;
CREATE TABLE t_server_members (
    c_member_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_server_id VARCHAR(36) NOT NULL,
    c_user_id VARCHAR(32) NOT NULL,
    c_role_id VARCHAR(36),
    FOREIGN KEY (c_server_id) REFERENCES t_servers(c_server_id),
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id),
    FOREIGN KEY (c_role_id) REFERENCES t_roles(c_role_id)
);

DROP TABLE IF EXISTS t_roles;
CREATE TABLE t_roles (
    c_role_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_server_id VARCHAR(36) NOT NULL,
    c_name VARCHAR NOT NULL,
    c_permissions INTEGER NOT NULL,
    FOREIGN KEY (c_server_id) REFERENCES t_servers(c_server_id)
);

DROP TABLE IF EXISTS t_permissions;
CREATE TABLE t_permissions (
    c_permission_id INTEGER PRIMARY KEY,
    c_description TEXT NOT NULL
);

DROP TABLE IF EXISTS t_user_roles;
CREATE TABLE t_user_roles (
    c_user_id VARCHAR(32) NOT NULL,
    c_role_id VARCHAR(36) NOT NULL,
    c_server_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (c_user_id, c_role_id, c_server_id),
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id),
    FOREIGN KEY (c_role_id) REFERENCES t_roles(c_role_id),
    FOREIGN KEY (c_server_id) REFERENCES t_servers(c_server_id)
);

DROP TABLE IF EXISTS t_audit_logs;
CREATE TABLE t_audit_logs (
    c_log_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_user_id VARCHAR(32) NOT NULL,
    c_action TEXT NOT NULL,
    c_description TEXT,
    c_timestamp BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())::BIGINT,
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id)
);

DROP TABLE IF EXISTS t_channel_members;
CREATE TABLE t_channel_members (
    c_channel_id VARCHAR(36) NOT NULL,
    c_user_id VARCHAR(32) NOT NULL,
    c_permissions INTEGER NOT NULL,
    PRIMARY KEY (c_channel_id, c_user_id),
    FOREIGN KEY (c_channel_id) REFERENCES t_channels(c_channel_id) ON DELETE CASCADE,
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id)
);

DROP TABLE IF EXISTS t_message_metadata;
CREATE TABLE t_message_metadata (
    c_message_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    c_channel_id VARCHAR(36) NOT NULL,
    c_user_id VARCHAR(32) NOT NULL,
    c_message_type VARCHAR(20) NOT NULL,
    c_timestamp BIGINT NOT NULL,
    FOREIGN KEY (c_channel_id) REFERENCES t_channels(c_channel_id) ON DELETE CASCADE,
    FOREIGN KEY (c_user_id) REFERENCES t_users(c_user_id)
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
CREATE INDEX idx_server_id_on_channels ON t_channels (c_server_id);
CREATE INDEX idx_server_id_on_roles ON t_roles (c_server_id);
-- 为频道ID创建索引
CREATE INDEX idx_channel_id ON t_channels (c_channel_id);
CREATE INDEX idx_channel_id_on_messages ON t_message_metadata (c_channel_id);


CREATE INDEX idx_user_roles_user_server ON t_user_roles (c_user_id, c_server_id);
CREATE INDEX idx_audit_logs_timestamp ON t_audit_logs (c_timestamp);

CREATE INDEX idx_message_type ON t_message_metadata (c_message_type);
CREATE INDEX idx_message_user_id ON t_message_metadata (c_user_id);


INSERT INTO t_users(c_user_id, c_public_key, c_user_info) VALUES ('e2cfa16b-c7a3-46f0-9995-22e2ae333e3e','80e6701cacfccc7e5c0b1767a466b993',"LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQ0lqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUF1YXNhRHcxVnpmeTJKU3BnVTMrRApEeTB0QzVadXFNSjhOanpnQk85UEtBcVU4QXdiem1WdEY5M0tieU8xd0xSTGJySXkxR0tJVlBkd0ZwOVVuNlZ2ClJNeHIxQ0hmRHY2WFFpYUpmbjJLZ1FaQ1lDcmo4REorcG84N2FneVF3R2s2ZEpDc2ZNOHoxenNqZ3dQQkxyTHMKcHo4aWZGcGNJUkkvWDF1a3RUS1JzaHhWVkh0OGtYYjVrRDl6SUM1ekRRcVBMeVc1TnFoUFZEbU1UdnFvdG05SwpicllqSnltbi9xaTJuVGplcDNaKzFxbHp5NmdPRXF4S3pralZwd1lyMlNsbWFEQU5iT2RKanJuQVdsNHFVNXN3CnorMzRWTklkaHJTSnhXRjBRR2MzaU82UENZS29mYWVsUWJYZjI3UTF5Uk1TdTYxL0hqdmhWUWNvTnYxeTFQT2cKSllkb2xiREwwYW9pWFNXOWZOK2hHd3RmZjczdjIwemV1N3RGWWowbTViczFFd3JvK2RjUjZsQmFUUHBRZnZDLwpydWVKaHpNZzAvZ3hvTFFBakI3eTlNVnVQYTNEUFVpSVFpdktHeGtUN3ZKdlN5WGdCb29KOHZiNE16dElIb1BGCngxb3RmQ05PajhVdGlwdG4rOFFTUXZ0UXJFdklZdVpaOERnSUd1NmtRVzFEMzZhRG1iVFdra00vTUw3UmRGN20KMVpOb3JBMzFnT3JQWnByTlRQUzlxRWtTY2x4dWxoZ3VHd2ZYUEcwTlk0NVZxNlhoUW1MR0NGMFVaWHhrRXllagpXdStKVjE0ZTJRNUlzTTdtaFpOQlp5SjRxSjZ1MFQxZ0RUMnZWWDN1a1o2dmtnNlZrWDdxTFFNRDk1Z0cwZjdpCnBKMXRQWTVzMG1oTmRUSUpvODBzTk5zQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo=")

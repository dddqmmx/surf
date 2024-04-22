-- create database surf;
-- \c surf;
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
    c_roles jsonb,
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

CREATE OR REPLACE FUNCTION check_roles_exist()
RETURNS TRIGGER AS $$
DECLARE
    role_id INT;
BEGIN
    -- 遍历 JSONB 数组中的每个元素
    FOR role_id IN SELECT jsonb_array_elements_text(NEW.c_roles)::int
    LOOP
        -- 检查元素是否存在于 t_permissions 表中
        IF NOT EXISTS (SELECT 1 FROM t_roles WHERE c_role_id = role_id) THEN
            RAISE EXCEPTION 'Permission ID % does not exist in t_permissions.', role_id;
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_permissions
BEFORE INSERT OR UPDATE ON t_roles
FOR EACH ROW EXECUTE FUNCTION check_permissions_exist();


INSERT INTO public.t_users (c_user_id, c_nickname, c_public_key, c_user_info) VALUES ('e2cfa16b-c7a3-46f0-9995-22e2ae333e3e', '80e6701cacfccc7e5c0b1767a466b993', 'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQ0lqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUF1YXNhRHcxVnpmeTJKU3BnVTMrRApEeTB0QzVadXFNSjhOanpnQk85UEtBcVU4QXdiem1WdEY5M0tieU8xd0xSTGJySXkxR0tJVlBkd0ZwOVVuNlZ2ClJNeHIxQ0hmRHY2WFFpYUpmbjJLZ1FaQ1lDcmo4REorcG84N2FneVF3R2s2ZEpDc2ZNOHoxenNqZ3dQQkxyTHMKcHo4aWZGcGNJUkkvWDF1a3RUS1JzaHhWVkh0OGtYYjVrRDl6SUM1ekRRcVBMeVc1TnFoUFZEbU1UdnFvdG05SwpicllqSnltbi9xaTJuVGplcDNaKzFxbHp5NmdPRXF4S3pralZwd1lyMlNsbWFEQU5iT2RKanJuQVdsNHFVNXN3CnorMzRWTklkaHJTSnhXRjBRR2MzaU82UENZS29mYWVsUWJYZjI3UTF5Uk1TdTYxL0hqdmhWUWNvTnYxeTFQT2cKSllkb2xiREwwYW9pWFNXOWZOK2hHd3RmZjczdjIwemV1N3RGWWowbTViczFFd3JvK2RjUjZsQmFUUHBRZnZDLwpydWVKaHpNZzAvZ3hvTFFBakI3eTlNVnVQYTNEUFVpSVFpdktHeGtUN3ZKdlN5WGdCb29KOHZiNE16dElIb1BGCngxb3RmQ05PajhVdGlwdG4rOFFTUXZ0UXJFdklZdVpaOERnSUd1NmtRVzFEMzZhRG1iVFdra00vTUw3UmRGN20KMVpOb3JBMzFnT3JQWnByTlRQUzlxRWtTY2x4dWxoZ3VHd2ZYUEcwTlk0NVZxNlhoUW1MR0NGMFVaWHhrRXllagpXdStKVjE0ZTJRNUlzTTdtaFpOQlp5SjRxSjZ1MFQxZ0RUMnZWWDN1a1o2dmtnNlZrWDdxTFFNRDk1Z0cwZjdpCnBKMXRQWTVzMG1oTmRUSUpvODBzTk5zQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo=', '{"email": "woshishabi@gmail.com", "phone": "1145141919810"}');
INSERT INTO public.t_users (c_user_id, c_nickname, c_public_key, c_user_info) VALUES ('02c9aba4-44a0-4ddf-8cf2-70c6e5e554d7', 'd0980d66c36175e8ce960e5fe403c691', 'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQ0lqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUFoemdQbGY3T0tmajVLMTRpVFVWTQpqUlhldGpiVUFhWW1vUjlaU2EzOUhWVXVybUxPY0d0SXVHNzB2SUNIMTg0anVsMVovRy96L2wvOFp4RkQxb1M4CnBSRGl3SEtKUXA0MmttdmFMMW1pVGY2M1gxWWxiV2ptbm5zaktWNW9LMzZVQnRvVytsQlhIWmxyLzFLOEo2MjEKRnlmKzR6amhlbmJ1Mmp5a0ZzNy9seVhNWW9xVmpHMnpJNHhpYk5Zd0t0MDJOT21KMW1jWHhIOWdUdEpMWEFuRQpCZldYQjlTMmtZZDVCcXhTc3FxWmZ6NUsvakFzNWx2Skp6dXAyanRFZ3RJSG9tdTY5R21mbjFJTXhtZmdoN1NkCnhPWFVGY3VFV291QjdadWozWVVnQXovUTdRYlVqdERicXhsaEFOaHJ2bGNCbUpxMnhuT2liUXFISlRQUkxmeFcKRkNDdGpZQmV0a3N3em9MbUgrb2dYTjJtRnBwa05TdWYzQzdPaGtXZFdMbHZLTXU0dENkZG0yV1dyZXgxa0lXNgpIOHo4cVV3aGFZZk9LMEtYaitCcmkyTnREV3hhR1VsdHI1YTR5NnpIMnJKUDlMUmhLMlhRUGhSbGRiajNKNW5TCnVYWllTWUo2NTVGdkZKZElqc3huNktiSkdKM2xFRnJxU2hhVDdzR09ReWZMcU5WWW8ycndNRm5WMnhYVGY1MXMKNUE2L2FDNUNNckN3dnE3Qytac0Y3YU45Tis0Qy9pSnF1VG1OTmFmaGw3bmpvRlNndXJyWCsveXNJd3UxR0dnTQpXS05qUXNRSytOOVgxcE1MOWFvR2F6dXRET3ZlTXNtMnl2dU81alNZRzRiWFM0VFA1c3dmbHYyY3NpeUR4aXNpCmt6V2RFUHM3bUhQditsbzNRdU9jTEFNQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo=', '{"email": "wocaonima@gmail.com", "phone": "24242424"}');


INSERT INTO public.t_permissions (c_permission_id, c_description) VALUES (1, 'Permission 1');
INSERT INTO public.t_permissions (c_permission_id, c_description) VALUES (2, 'Permission 2');
INSERT INTO public.t_permissions (c_permission_id, c_description) VALUES (3, 'Permission 3');

INSERT INTO public.t_servers (c_server_id, c_description, c_name, c_owner_id, c_create_time, c_icon_url, c_is_active, c_is_private) VALUES ('fdad3e5e-818d-4201-8b07-4734da71d9b7','傻逼','hololive','e2cfa16b-c7a3-46f0-9995-22e2ae333e3e','1713630327',NULL,true,true);

INSERT INTO public.t_roles (c_role_id, c_server_id, c_name, c_permissions) VALUES ('bdabb221-ebe9-478d-bb42-86578cb2e4c0', 'fdad3e5e-818d-4201-8b07-4734da71d9b7', '服务器拥有者', '[1, 2, 3]');
INSERT INTO public.t_roles (c_role_id, c_server_id, c_name, c_permissions) VALUES ('720712a3-8eb0-421e-a269-776bac5c5dd2', 'fdad3e5e-818d-4201-8b07-4734da71d9b7', '普通成员', '[1]');


INSERT INTO public.t_server_members (c_id, c_server_id, c_user_id, c_roles) VALUES ('b8dc425a-f238-4bf6-85cc-e17c27833a63', 'fdad3e5e-818d-4201-8b07-4734da71d9b7', 'e2cfa16b-c7a3-46f0-9995-22e2ae333e3e', '["bdabb221-ebe9-478d-bb42-86578cb2e4c0"]');
INSERT INTO public.t_server_members (c_id, c_server_id, c_user_id, c_roles) VALUES ('070e0b27-de71-4dd2-af69-a562d2b1825b', 'fdad3e5e-818d-4201-8b07-4734da71d9b7', '02c9aba4-44a0-4ddf-8cf2-70c6e5e554d7', '["720712a3-8eb0-421e-a269-776bac5c5dd2"]');


INSERT INTO public.t_channel_groups (c_group_id, c_server_id, c_group_name) VALUES ('97096b43-2de4-43ac-9024-ebb63ed3ec1e', 'fdad3e5e-818d-4201-8b07-4734da71d9b7', '文字频道分组');
INSERT INTO public.t_channel_groups (c_group_id, c_server_id, c_group_name) VALUES ('680c0836-58c4-43fb-8fb8-23a2103ffcdd', 'fdad3e5e-818d-4201-8b07-4734da71d9b7', '语音频道分组');


INSERT INTO public.t_channels (c_channel_id, c_group_id, c_name, c_type, c_description, c_create_by, c_create_time) VALUES ('aa6cd21b-7080-4e65-9059-8a6a8c303cbb', '97096b43-2de4-43ac-9024-ebb63ed3ec1e', '默认文字频道', 'text', '这是一个文字频道', 'e2cfa16b-c7a3-46f0-9995-22e2ae333e3e', 1713630328);
INSERT INTO public.t_channels (c_channel_id, c_group_id, c_name, c_type, c_description, c_create_by, c_create_time) VALUES ('0362e80c-839b-4ee6-9e77-c2cb6668c961', '680c0836-58c4-43fb-8fb8-23a2103ffcdd', '默认语音频道', 'voice', '这是一个语音频道', 'e2cfa16b-c7a3-46f0-9995-22e2ae333e3e', 1713630328);

create database surf;
\c surf;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- 确保扩展已安装



CREATE OR REPLACE FUNCTION generate_random_nickname() RETURNS VARCHAR(20) AS $$
BEGIN
    RETURN md5(random()::text);
END;
$$ LANGUAGE plpgsql;

DROP TABLE IF EXISTS "user";
CREATE TABLE "user"(
    user_uuid VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    public_key VARCHAR,
    user_info jsonb
);

DROP TABLE IF EXISTS "user_relationship";
CREATE TABLE "user_relationship"(
    user1_uuid VARCHAR(36) PRIMARY KEY,
    user2_uuid VARCHAR(36),
    user_relationship_type INT4,
    chat_uuid VARCHAR
);

DROP TABLE IF EXISTS "chatroom_info";
CREATE TABLE "chatroom_info"(
    chatroom_uuid VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    chatroom_name VARCHAR DEFAULT generate_random_nickname()
);

DROP TABLE IF EXISTS "chatroom_chats";
CREATE TABLE "chatroom_chats"(
    chatroom_uuid VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_type INT4,
    chat_uuid VARCHAR(36)
);

DROP TABLE IF EXISTS "chatroom_member";
CREATE TABLE "chatroom_member"(
    chatroom_uuid VARCHAR(36),
    user_uuid VARCHAR(36) NOT NULL,
    member_right INT4
);

DROP TABLE IF EXISTS "chat";
CREATE TABLE "chat"(
    chat_uuid VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()
);
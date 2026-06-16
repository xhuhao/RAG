-- =============================================
-- RAG校园知识库问答系统 - 数据库初始化脚本
-- =============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS db_enterprise_ga DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE db_enterprise_ga;

-- -------------------------------------------
-- 用户表
-- -------------------------------------------
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password VARCHAR(32) NOT NULL COMMENT '密码（MD5加密）',
    role ENUM('user', 'admin') DEFAULT 'user' COMMENT '角色',
    status TINYINT DEFAULT 1 COMMENT '状态：1正常 0禁用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- -------------------------------------------
-- 文档表
-- -------------------------------------------
DROP TABLE IF EXISTS documents;
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '文档ID',
    title VARCHAR(200) NOT NULL COMMENT '文档标题',
    category VARCHAR(50) COMMENT '分类（院系）',
    doc_type VARCHAR(50) COMMENT '文档类型',
    url VARCHAR(500) COMMENT '文档URL',
    version INT DEFAULT 1 COMMENT '版本号',
    is_active TINYINT DEFAULT 1 COMMENT '是否生效',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档表';

-- -------------------------------------------
-- 同步日志表
-- -------------------------------------------
DROP TABLE IF EXISTS sync_logs;
CREATE TABLE sync_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    status ENUM('success', 'failed') COMMENT '同步状态',
    added INT DEFAULT 0 COMMENT '新增数量',
    updated INT DEFAULT 0 COMMENT '更新数量',
    removed INT DEFAULT 0 COMMENT '删除数量',
    failed INT DEFAULT 0 COMMENT '失败数量',
    message TEXT COMMENT '备注信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '同步时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='同步日志表';

-- -------------------------------------------
-- 初始化数据
-- -------------------------------------------

-- 管理员账号（密码：123456）
INSERT INTO users (username, password, role, status) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin', 1);

-- 测试用户（密码：123456）
INSERT INTO users (username, password, role, status) VALUES
('student1', 'e10adc3949ba59abbe56e057f20f883e', 'user', 1),
('student2', 'e10adc3949ba59abbe56e057f20f883e', 'user', 1);

-- 测试文档数据
INSERT INTO documents (title, category, doc_type, url, version, is_active) VALUES
('2025年硕士研究生招生简章', '研究生院', '通知公告', 'https://www.gxnu.edu.cn/yz/2025/zs.pdf', 1, 1),
('图书馆借阅管理规定', '图书馆', '规章制度', 'https://www.gxnu.edu.cn/lib/rules.pdf', 1, 1),
('本科生学籍管理办法', '教务处', '规章制度', 'https://www.gxnu.edu.cn/jwc/xjgl.pdf', 1, 1),
('计算机学院课程大纲', '计算机学院', '课程信息', 'https://www.gxnu.edu.cn/cs/kcdg.pdf', 1, 1);

-- 输出初始化完成信息
SELECT '数据库初始化完成！' AS message;
SELECT '管理员账号：admin / 123456' AS admin_info;
SELECT '测试账号：student1 / 123456' AS test_user_info;

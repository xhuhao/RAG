"""
文件：md5.py
功能：MD5加密工具
说明：提供密码加密功能
"""

import hashlib

# 加盐值
SALT = 'guangxi_rag_2025'

def md5_encrypt(password):
    """
    MD5加密（不加盐）

    参数：
        password: 原始密码

    返回：
        加密后的密码字符串
    """
    return hashlib.md5(password.encode('utf-8')).hexdigest()

def md5_with_salt(password, salt=SALT):
    """
    MD5加盐加密

    参数：
        password: 原始密码
        salt: 盐值（默认使用全局盐值）

    返回：
        加盐加密后的密码字符串
    """
    return hashlib.md5((password + salt).encode('utf-8')).hexdigest()

"""
文件：production.py
功能：生产环境配置
说明：Docker部署时使用的配置
"""

import os
from app.config.default import Config

class ProductionConfig(Config):
    """生产环境配置类"""

    # 关闭调试模式
    DEBUG = False

    # Docker容器名称作为主机名
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '123456')
    MYSQL_DB = os.getenv('MYSQL_DB', 'db_enterprise_ga')

    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4'

    # Chroma配置
    CHROMA_HOST = os.getenv('CHROMA_HOST', 'chroma-server')
    CHROMA_PORT = int(os.getenv('CHROMA_PORT', 8000))

    # Ollama配置
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'ollama')
    OLLAMA_PORT = int(os.getenv('OLLAMA_PORT', 11434))

    # 日志级别
    LOG_LEVEL = 'INFO'

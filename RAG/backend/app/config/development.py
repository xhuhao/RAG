"""
文件：development.py
功能：开发环境配置
说明：本地开发时使用的配置
"""

from app.config.default import Config

class DevelopmentConfig(Config):
    """开发环境配置类"""

    # 开启调试模式
    DEBUG = True

    # 本地服务地址
    MYSQL_HOST = 'localhost'
    CHROMA_HOST = 'localhost'
    OLLAMA_HOST = 'localhost'

    # 日志级别
    LOG_LEVEL = 'DEBUG'

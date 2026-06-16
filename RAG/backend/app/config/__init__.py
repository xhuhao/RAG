"""
文件：__init__.py
功能：配置模块初始化
说明：根据环境变量返回对应的配置类
"""

import os
from app.config.default import Config
from app.config.development import DevelopmentConfig
from app.config.production import ProductionConfig

def get_config():
    """
    根据环境变量返回配置类

    返回：
        配置类实例
    """
    env = os.getenv('FLASK_ENV', 'development')

    if env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig

"""
文件：__init__.py
功能：数据库模型模块初始化
说明：导入所有模型类
"""

from flask_sqlalchemy import SQLAlchemy

# 创建数据库实例
db = SQLAlchemy()

from app.models.user import User
from app.models.document import Document

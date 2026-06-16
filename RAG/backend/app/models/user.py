"""
文件：user.py
功能：用户数据模型
说明：定义用户表结构和方法
"""

from datetime import datetime
from app.models import db

class User(db.Model):
    """
    用户模型类

    属性：
        id: 用户ID（主键）
        username: 用户名（唯一）
        password: 密码（MD5加密）
        role: 角色（user/admin）
        status: 状态（1正常/0禁用）
        created_at: 注册时间
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password = db.Column(db.String(32), nullable=False, comment='密码（MD5加密）')
    role = db.Column(db.Enum('user', 'admin'), default='user', comment='角色')
    status = db.Column(db.SmallInteger, default=1, comment='状态：1正常 0禁用')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='注册时间')

    def to_dict(self):
        """
        将用户对象转换为字典

        返回：
            用户信息字典
        """
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

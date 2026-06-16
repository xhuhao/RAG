"""
文件：document.py
功能：文档数据模型
说明：定义文档表结构和方法
"""

from datetime import datetime
from app.models import db

class Document(db.Model):
    """
    文档模型类

    属性：
        id: 文档ID（主键）
        title: 文档标题
        category: 分类（院系）
        doc_type: 文档类型
        url: 文档URL
        version: 版本号
        is_active: 是否生效
        created_at: 创建时间
        updated_at: 更新时间
    """

    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='文档ID')
    title = db.Column(db.String(200), nullable=False, comment='文档标题')
    category = db.Column(db.String(50), comment='分类（院系）')
    doc_type = db.Column(db.String(50), comment='文档类型')
    url = db.Column(db.String(500), comment='文档URL')
    version = db.Column(db.Integer, default=1, comment='版本号')
    is_active = db.Column(db.SmallInteger, default=1, comment='是否生效')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """
        将文档对象转换为字典

        返回：
            文档信息字典
        """
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'doc_type': self.doc_type,
            'url': self.url,
            'version': self.version,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

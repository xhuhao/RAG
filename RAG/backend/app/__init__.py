"""
文件：__init__.py
功能：Flask应用初始化
说明：创建Flask应用实例，注册蓝图，配置扩展
"""

from flask import Flask
from flask_cors import CORS
from app.config import get_config
from app.models import db

def create_app():
    """
    创建Flask应用实例

    返回：
        Flask应用实例
    """
    app = Flask(__name__)

    # 加载配置
    config = get_config()
    app.config.from_object(config)

    # 初始化数据库
    db.init_app(app)

    # 配置跨域
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })

    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.document import document_bp
    from app.routes.chat import chat_bp
    from app.routes.admin import admin_bp
    from app.routes.sync import sync_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(sync_bp)

    return app

"""
文件：run.py
功能：Flask应用启动入口
说明：启动Flask开发服务器
"""

from app import create_app
from app.models import db

# 创建Flask应用
app = create_app()

# 初始化数据库
with app.app_context():
    db.create_all()
    print("数据库表创建完成")

if __name__ == '__main__':
    # 启动开发服务器
    print("Flask服务器启动中...")
    print("访问地址：http://localhost:5000")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

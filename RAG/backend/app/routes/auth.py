"""
文件：auth.py
功能：用户认证相关API
说明：处理用户登录、注册、登出等请求

接口列表：
- POST /api/auth/register    用户注册
- POST /api/auth/login       用户登录
- GET  /api/auth/logout      用户登出
"""

from flask import Blueprint, request, jsonify
from app.models import db
from app.models.user import User
from app.utils.md5 import md5_encrypt

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """
    用户注册接口

    请求参数：
        username (str): 用户名
        password (str): 密码
        confirm_password (str): 确认密码

    返回：
        success: {'code': 200, 'message': '注册成功', 'data': {'user': {...}}}
        failure: {'code': 400, 'message': '错误信息'}
    """
    # 获取请求数据
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()

    # 参数验证
    if not username:
        return jsonify({'code': 400, 'message': '用户名不能为空'})

    if not password:
        return jsonify({'code': 400, 'message': '密码不能为空'})

    if len(username) < 3 or len(username) > 20:
        return jsonify({'code': 400, 'message': '用户名长度应为3-20个字符'})

    if len(password) < 6:
        return jsonify({'code': 400, 'message': '密码长度不能少于6位'})

    if password != confirm_password:
        return jsonify({'code': 400, 'message': '两次密码不一致'})

    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'code': 400, 'message': '用户名已存在'})

    # 创建新用户
    try:
        new_user = User(
            username=username,
            password=md5_encrypt(password),
            role='user',
            status=1
        )
        db.session.add(new_user)
        db.session.commit()

        # 返回成功信息
        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': {
                'user': new_user.to_dict()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'注册失败：{str(e)}'})

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    用户登录接口

    请求参数：
        username (str): 用户名
        password (str): 密码

    返回：
        success: {'code': 200, 'message': '登录成功', 'data': {'user': {...}}}
        failure: {'code': 400, 'message': '错误信息'}
    """
    # 获取请求数据
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    # 参数验证
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'})

    # 查询用户
    user = User.query.filter_by(username=username).first()

    # 验证用户存在
    if not user:
        return jsonify({'code': 400, 'message': '用户名或密码错误'})

    # 验证密码
    if user.password != md5_encrypt(password):
        return jsonify({'code': 400, 'message': '用户名或密码错误'})

    # 验证用户状态
    if user.status == 0:
        return jsonify({'code': 400, 'message': '账号已被禁用'})

    # 登录成功
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'user': user.to_dict()
        }
    })

@auth_bp.route('/api/auth/logout', methods=['GET'])
def logout():
    """
    用户登出接口

    返回：
        {'code': 200, 'message': '登出成功'}
    """
    return jsonify({
        'code': 200,
        'message': '登出成功'
    })

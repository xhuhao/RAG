"""
文件：admin.py
功能：管理员相关API
说明：处理用户管理、统计等操作

接口列表：
- GET    /api/users          获取用户列表
- GET    /api/users/:id      获取用户详情
- PUT    /api/users/:id      更新用户
- DELETE /api/users/:id      删除用户
- PUT    /api/users/:id/reset-password  重置密码
- GET    /api/stats/overview 获取统计数据
- GET    /api/stats/trends   获取问答趋势
- GET    /api/stats/hot-questions 获取热门问题
"""

from flask import Blueprint, request, jsonify
from app.services.user_service import (
    get_user_list,
    get_user_by_id,
    update_user_record,
    delete_user_record,
    reset_user_password,
    get_user_stats
)
from app.services.stats_service import (
    get_overview_stats,
    get_question_trends,
    get_hot_questions
)

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/users', methods=['GET'])
def list_users():
    """
    获取用户列表接口

    请求参数：
        page (int): 页码（默认1）
        per_page (int): 每页数量（默认10）
        keyword (str): 搜索关键词

    返回：
        success: {'code': 200, 'data': {'items': [...], 'total': 100, ...}}
    """
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', None)

    try:
        result = get_user_list(page, per_page, keyword)
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@admin_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    获取用户详情接口

    参数：
        user_id: 用户ID

    返回：
        success: {'code': 200, 'data': {'user': {...}}}
        failure: {'code': 404, 'message': '用户不存在'}
    """
    user = get_user_by_id(user_id)

    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'})

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'user': user.to_dict()
        }
    })

@admin_bp.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    更新用户接口

    参数：
        user_id: 用户ID

    请求参数：
        username (str): 用户名
        role (str): 角色
        status (int): 状态

    返回：
        success: {'code': 200, 'message': '更新成功', 'data': {'user': {...}}}
        failure: {'code': 400, 'message': '错误信息'}
    """
    # 获取请求数据
    data = request.get_json()
    username = data.get('username')
    role = data.get('role')
    status = data.get('status')

    try:
        user = update_user_record(user_id, username, role, status)

        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'user': user.to_dict()
            }
        })
    except Exception as e:
        return jsonify({'code': 400, 'message': str(e)})

@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    删除用户接口

    参数：
        user_id: 用户ID

    返回：
        success: {'code': 200, 'message': '删除成功'}
        failure: {'code': 400, 'message': '错误信息'}
    """
    try:
        delete_user_record(user_id)

        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        return jsonify({'code': 400, 'message': str(e)})

@admin_bp.route('/api/users/<int:user_id>/reset-password', methods=['PUT'])
def reset_password(user_id):
    """
    重置密码接口

    参数：
        user_id: 用户ID

    返回：
        success: {'code': 200, 'message': '重置成功'}
        failure: {'code': 400, 'message': '错误信息'}
    """
    try:
        reset_user_password(user_id)

        return jsonify({
            'code': 200,
            'message': '密码重置成功，新密码为：123456'
        })
    except Exception as e:
        return jsonify({'code': 400, 'message': str(e)})

@admin_bp.route('/api/stats/overview', methods=['GET'])
def stats_overview():
    """
    获取统计数据接口

    返回：
        success: {
            'code': 200,
            'data': {
                'users': {'total': 10, 'active': 8, ...},
                'documents': {'total': 5, 'active': 4, ...},
                'questions': {'total': 100, 'today': 10, ...}
            }
        }
    """
    try:
        stats = get_overview_stats()

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': stats
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@admin_bp.route('/api/stats/trends', methods=['GET'])
def stats_trends():
    """
    获取问答趋势接口

    请求参数：
        days (int): 统计天数（默认7）

    返回：
        success: {
            'code': 200,
            'data': {
                'trends': [{'date': '06-01', 'count': 10}, ...]
            }
        }
    """
    days = request.args.get('days', 7, type=int)

    try:
        trends = get_question_trends(days)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'trends': trends
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@admin_bp.route('/api/stats/hot-questions', methods=['GET'])
def stats_hot_questions():
    """
    获取热门问题接口

    请求参数：
        top (int): 返回数量（默认10）

    返回：
        success: {
            'code': 200,
            'data': {
                'questions': [{'question': '...', 'count': 5}, ...]
            }
        }
    """
    top = request.args.get('top', 10, type=int)

    try:
        questions = get_hot_questions(top)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'questions': questions
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

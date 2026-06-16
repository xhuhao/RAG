"""
文件：user_service.py
功能：用户管理服务
说明：处理用户的查询、更新、删除等操作
"""

from app.models import db
from app.models.user import User
from app.utils.md5 import md5_encrypt

def get_user_list(page=1, per_page=10, keyword=None):
    """
    获取用户列表

    参数：
        page: 页码
        per_page: 每页数量
        keyword: 搜索关键词

    返回：
        用户列表和分页信息
    """
    query = User.query

    # 关键词搜索
    if keyword:
        query = query.filter(User.username.like(f'%{keyword}%'))

    # 分页
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return {
        'items': [user.to_dict() for user in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }

def get_user_by_id(user_id):
    """
    根据ID获取用户

    参数：
        user_id: 用户ID

    返回：
        用户记录对象
    """
    return User.query.get(user_id)

def update_user_record(user_id, username=None, role=None, status=None):
    """
    更新用户记录

    参数：
        user_id: 用户ID
        username: 用户名
        role: 角色
        status: 状态

    返回：
        更新后的用户记录
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise Exception("用户不存在")

        if username:
            # 检查用户名是否已存在
            existing = User.query.filter_by(username=username).first()
            if existing and existing.id != user_id:
                raise Exception("用户名已存在")
            user.username = username

        if role:
            user.role = role

        if status is not None:
            user.status = status

        db.session.commit()

        return user
    except Exception as e:
        db.session.rollback()
        raise Exception(f"更新用户失败：{str(e)}")

def delete_user_record(user_id):
    """
    删除用户记录

    参数：
        user_id: 用户ID

    返回：
        是否删除成功
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise Exception("用户不存在")

        # 不允许删除管理员
        if user.role == 'admin':
            raise Exception("不能删除管理员账号")

        db.session.delete(user)
        db.session.commit()

        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"删除用户失败：{str(e)}")

def reset_user_password(user_id, new_password='123456'):
    """
    重置用户密码

    参数：
        user_id: 用户ID
        new_password: 新密码（默认123456）

    返回：
        是否重置成功
    """
    try:
        user = User.query.get(user_id)
        if not user:
            raise Exception("用户不存在")

        user.password = md5_encrypt(new_password)
        db.session.commit()

        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"重置密码失败：{str(e)}")

def get_user_stats():
    """
    获取用户统计信息

    返回：
        用户统计数据
    """
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(status=1).count()
        admin_users = User.query.filter_by(role='admin').count()
        normal_users = User.query.filter_by(role='user').count()

        return {
            'total': total_users,
            'active': active_users,
            'admin': admin_users,
            'normal': normal_users
        }
    except Exception as e:
        raise Exception(f"获取用户统计失败：{str(e)}")

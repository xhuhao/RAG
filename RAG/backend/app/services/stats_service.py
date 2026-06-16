"""
文件：stats_service.py
功能：统计服务
说明：提供问答趋势、热门问题等统计数据
"""

from datetime import datetime, timedelta
from app.models import db
from app.models.user import User
from app.models.document import Document

# 模拟问答日志（实际应该存储到数据库）
_question_logs = []

def log_question(question, session_id, has_answer):
    """
    记录问答日志

    参数：
        question: 用户问题
        session_id: 会话ID
        has_answer: 是否有答案
    """
    global _question_logs

    _question_logs.append({
        'question': question,
        'session_id': session_id,
        'has_answer': has_answer,
        'created_at': datetime.now()
    })

    # 只保留最近1000条记录
    if len(_question_logs) > 1000:
        _question_logs = _question_logs[-1000:]

def get_question_trends(days=7):
    """
    获取问答趋势数据

    参数：
        days: 统计天数

    返回：
        每日问答数量列表
    """
    global _question_logs

    today = datetime.now().date()
    trends = []

    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)
        count = sum(1 for log in _question_logs if log['created_at'].date() == date)
        trends.append({
            'date': date.strftime('%m-%d'),
            'count': count
        })

    return trends

def get_hot_questions(top_n=10):
    """
    获取热门问题

    参数：
        top_n: 返回数量

    返回：
        热门问题列表
    """
    global _question_logs

    # 统计问题出现次数
    question_count = {}
    for log in _question_logs:
        question = log['question']
        if question in question_count:
            question_count[question] += 1
        else:
            question_count[question] = 1

    # 排序
    sorted_questions = sorted(question_count.items(), key=lambda x: x[1], reverse=True)

    # 返回前N个
    return [{'question': q, 'count': c} for q, c in sorted_questions[:top_n]]

def get_overview_stats():
    """
    获取总览统计数据

    返回：
        统计数据字典
    """
    global _question_logs

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)

    # 用户统计
    total_users = User.query.count()
    active_users = User.query.filter_by(status=1).count()

    # 文档统计
    total_docs = Document.query.count()
    active_docs = Document.query.filter_by(is_active=1).count()

    # 问答统计
    total_questions = len(_question_logs)
    today_questions = sum(1 for log in _question_logs if log['created_at'].date() == today)
    week_questions = sum(1 for log in _question_logs if log['created_at'].date() >= week_ago)

    return {
        'users': {
            'total': total_users,
            'active': active_users
        },
        'documents': {
            'total': total_docs,
            'active': active_docs
        },
        'questions': {
            'total': total_questions,
            'today': today_questions,
            'week': week_questions
        }
    }

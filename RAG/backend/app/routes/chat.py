"""
文件：chat.py
功能：问答相关API
说明：处理用户提问，返回答案和参考来源

接口列表：
- POST /api/chat/ask         提问
- POST /api/chat/clear       清空会话历史
"""

from flask import Blueprint, request, jsonify
from app.services.chat_service import chat_with_rag, clear_session_history

# 创建问答蓝图
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chat/ask', methods=['POST'])
def ask():
    """
    提问接口

    请求参数：
        question (str): 用户问题
        session_id (str): 会话ID（可选，默认使用用户名）

    返回：
        success: {
            'code': 200,
            'message': 'success',
            'data': {
                'answer': '回答内容',
                'references': [{'doc_id': 1, 'content': '...'}],
                'has_reference': True
            }
        }
        failure: {'code': 400, 'message': '错误信息'}
    """
    # 获取请求数据
    data = request.get_json()
    question = data.get('question', '').strip()
    session_id = data.get('session_id', 'default')

    # 参数验证
    if not question:
        return jsonify({'code': 400, 'message': '请输入问题'})

    try:
        # 调用RAG问答服务
        result = chat_with_rag(question, session_id)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'问答失败：{str(e)}'})

@chat_bp.route('/api/chat/clear', methods=['POST'])
def clear_history():
    """
    清空会话历史接口

    请求参数：
        session_id (str): 会话ID

    返回：
        success: {'code': 200, 'message': '清空成功'}
    """
    # 获取请求数据
    data = request.get_json()
    session_id = data.get('session_id', 'default')

    try:
        clear_session_history(session_id)

        return jsonify({
            'code': 200,
            'message': '清空成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'清空失败：{str(e)}'})

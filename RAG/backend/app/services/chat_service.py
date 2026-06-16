"""
文件：chat_service.py
功能：问答服务
说明：整合RAG检索和Deepseek生成答案
"""

import requests
from flask import current_app
from app.services.rag_service import search_similar_chunks
from app.services.stats_service import log_question

# 会话历史（内存存储，按用户ID分组）
_session_histories = {}

def get_session_history(session_id, max_turns=20):
    """
    获取会话历史

    参数：
        session_id: 会话ID（通常是用户名）
        max_turns: 最大保留轮数

    返回：
        会话历史列表
    """
    global _session_histories

    if session_id not in _session_histories:
        _session_histories[session_id] = []

    history = _session_histories[session_id]

    # 只保留最近的对话
    if len(history) > max_turns * 2:
        history = history[-(max_turns * 2):]
        _session_histories[session_id] = history

    return history

def add_to_session_history(session_id, user_message, assistant_message):
    """
    添加对话到会话历史

    参数：
        session_id: 会话ID
        user_message: 用户消息
        assistant_message: 助手回复
    """
    global _session_histories

    if session_id not in _session_histories:
        _session_histories[session_id] = []

    _session_histories[session_id].append({
        'role': 'user',
        'content': user_message
    })
    _session_histories[session_id].append({
        'role': 'assistant',
        'content': assistant_message
    })

def clear_session_history(session_id):
    """
    清空会话历史

    参数：
        session_id: 会话ID
    """
    global _session_histories

    if session_id in _session_histories:
        _session_histories[session_id] = []

def call_deepseek(messages):
    """
    调用Deepseek API生成回答

    参数：
        messages: 消息列表

    返回：
        生成的回答
    """
    try:
        api_key = current_app.config.get('DEEPSEEK_API_KEY', '')
        model = current_app.config.get('DEEPSEEK_MODEL', 'deepseek-v4-pro')
        temperature = current_app.config.get('DEEPSEEK_TEMPERATURE', 0.2)
        max_tokens = current_app.config.get('DEEPSEEK_MAX_TOKENS', 1024)
        top_p = current_app.config.get('DEEPSEEK_TOP_P', 0.9)

        # Deepseek API地址
        url = "https://api.deepseek.com/v1/chat/completions"

        # 请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # 请求数据
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        }

        # 发送请求
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()

        # 解析响应
        result = response.json()
        answer = result['choices'][0]['message']['content']

        return answer
    except Exception as e:
        raise Exception(f"调用Deepseek失败：{str(e)}")

def chat_with_rag(question, session_id=None):
    """
    使用RAG进行问答

    参数：
        question: 用户问题
        session_id: 会话ID

    返回：
        包含答案和参考来源的字典
    """
    try:
        # 1. 搜索相关文档块
        similar_chunks = search_similar_chunks(question, top_k=3)

        # 2. 构建上下文
        context = ""
        references = []

        if similar_chunks:
            context_parts = []
            for i, chunk in enumerate(similar_chunks):
                context_parts.append(f"[参考{i+1}] {chunk['content']}")

                # 提取参考来源信息
                if chunk['metadata']:
                    doc_id = chunk['metadata'].get('doc_id')
                    if doc_id:
                        references.append({
                            'doc_id': doc_id,
                            'content': chunk['content'][:200] + '...' if len(chunk['content']) > 200 else chunk['content']
                        })

            context = "\n\n".join(context_parts)

        # 3. 获取会话历史
        history = []
        if session_id:
            max_turns = current_app.config.get('MAX_HISTORY_TURNS', 20)
            history = get_session_history(session_id, max_turns)

        # 4. 构建消息列表
        system_message = """你是广西师范大学的智能问答助手。请根据提供的参考文档回答用户的问题。

要求：
1. 如果参考文档中有相关信息，请基于文档内容回答
2. 如果参考文档中没有相关信息，请直接回复"抱歉，未找到相关信息"
3. 回答要准确、简洁、有条理
4. 适当引用参考文档中的内容"""

        messages = [{"role": "system", "content": system_message}]

        # 添加历史对话
        messages.extend(history)

        # 添加当前问题和上下文
        if context:
            user_message = f"""参考文档：
{context}

用户问题：{question}"""
        else:
            user_message = question

        messages.append({"role": "user", "content": user_message})

        # 5. 调用Deepseek生成回答
        answer = call_deepseek(messages)

        # 6. 保存到会话历史
        if session_id:
            add_to_session_history(session_id, question, answer)

        # 7. 检查是否找到相关信息
        has_reference = len(references) > 0
        if "未找到相关信息" in answer or "抱歉" in answer:
            references = []
            has_reference = False

        # 8. 记录问答日志
        log_question(question, session_id, has_reference)

        return {
            'answer': answer,
            'references': references,
            'has_reference': has_reference
        }
    except Exception as e:
        raise Exception(f"问答失败：{str(e)}")

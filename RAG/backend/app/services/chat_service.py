"""
文件：chat_service.py
功能：问答服务
说明：整合RAG检索和Deepseek生成答案
"""

import requests
from flask import current_app
from app.services.rag_service import search_similar_chunks
from app.services.reranker_service import rerank_documents
from app.services.grounding_service import ground_answer
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

def call_llm(messages):
    """
    调用LLM API生成回答

    参数：
        messages: 消息列表

    返回：
        生成的回答
    """
    try:
        api_key = current_app.config.get('LLM_API_KEY', '')
        base_url = current_app.config.get('LLM_BASE_URL', 'https://api.xiaomimimo.com/v1')
        model = current_app.config.get('LLM_MODEL', 'mimo-v2.5-pro')
        temperature = current_app.config.get('LLM_TEMPERATURE', 0.1)
        max_tokens = current_app.config.get('LLM_MAX_TOKENS', 1024)
        top_p = current_app.config.get('LLM_TOP_P', 0.9)

        # LLM API地址
        url = f"{base_url}/chat/completions"

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
        message = result['choices'][0]['message']

        # 处理mimo-v2.5-pro的特殊格式
        content = message.get('content', '') or ''
        reasoning = message.get('reasoning_content', '') or ''

        # 优先使用content字段（实际回答）
        answer = content.strip()

        # 如果content为空或被截断，从reasoning_content提取最终答案
        if not answer and reasoning:
            # 尝试提取"最终回答："后面的内容
            patterns = [
                '最终回答：',
                '最终回答:',
                '回答：',
                '回答:',
                '答案：',
                '答案:',
            ]
            for pattern in patterns:
                if pattern in reasoning:
                    # 提取pattern后面的内容
                    idx = reasoning.index(pattern) + len(pattern)
                    answer = reasoning[idx:].strip()
                    # 只取第一行
                    if '\n' in answer:
                        answer = answer.split('\n')[0].strip()
                    break

            # 如果还是没有，取reasoning的最后一行
            if not answer:
                lines = reasoning.strip().split('\n')
                for line in reversed(lines):
                    line = line.strip()
                    if line and len(line) > 5:
                        answer = line
                        break

        # 如果仍然为空，返回默认消息
        if not answer:
            answer = '抱歉，未能生成回答。'

        return answer
    except Exception as e:
        raise Exception(f"调用LLM失败：{str(e)}")

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
        similar_chunks = search_similar_chunks(question, top_k=10, max_distance=0.6)

        # 2. 重排序（Reranking）
        if similar_chunks and len(similar_chunks) > 3:
            similar_chunks = rerank_documents(question, similar_chunks, top_k=5)

        # 3. 构建上下文
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

        # 4. 获取会话历史
        history = []
        if session_id:
            max_turns = current_app.config.get('MAX_HISTORY_TURNS', 20)
            history = get_session_history(session_id, max_turns)

        # 5. 构建消息列表
        system_message = """你是广西师范大学的智能问答助手。

【绝对约束】
1. 只能使用参考文档中的信息
2. 禁止添加任何文档中没有的内容
3. 禁止使用你的训练知识
4. 禁止推测或扩展

【回答方式】
1. 直接引用文档原文
2. 不要改写、总结或补充
3. 如果文档没有相关信息，只回复"抱歉，未找到相关信息"
4. 回答要简洁，直接给出答案"""

        messages = [{"role": "system", "content": system_message}]

        # 添加历史对话
        messages.extend(history)

        # 添加当前问题和上下文
        if context:
            user_message = f"""请严格根据以下参考文档回答问题。

参考文档：
{context}

问题：{question}

注意：只能使用上述文档中的信息回答，禁止添加任何其他内容。如果文档中没有相关信息，请直接回复"抱歉，未找到相关信息"。"""
        else:
            user_message = question

        messages.append({"role": "user", "content": user_message})

        # 6. 调用LLM生成回答
        answer = call_llm(messages)

        # 7. Grounding：确保回答基于文档
        if context and answer and "抱歉" not in answer:
            answer = ground_answer(answer, context)

        # 8. 保存到会话历史
        if session_id:
            add_to_session_history(session_id, question, answer)

        # 9. 检查是否找到相关信息
        has_reference = len(references) > 0
        if "未找到相关信息" in answer or "抱歉" in answer:
            references = []
            has_reference = False

        # 10. 记录问答日志
        log_question(question, session_id, has_reference)

        return {
            'answer': answer,
            'references': references,
            'has_reference': has_reference
        }
    except Exception as e:
        raise Exception(f"问答失败：{str(e)}")

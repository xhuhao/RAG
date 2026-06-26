"""
文件：grounding_service.py
功能：Grounding服务
说明：确保回答基于检索到的文档
"""

import requests
from flask import current_app


def ground_answer(answer, context):
    """
    确保回答基于文档（Grounding）

    参数：
        answer: LLM生成的回答
        context: 检索到的文档上下文

    返回：
        基于文档的回答
    """
    if not answer or not context:
        return answer

    try:
        # 将回答拆分成声明
        statements = split_into_statements(answer)

        if not statements:
            return answer

        # 检查每个声明是否能从文档推断
        grounded_statements = []
        for stmt in statements:
            if is_supported_by_context(stmt, context):
                grounded_statements.append(stmt)

        # 如果没有声明被支持，返回默认消息
        if not grounded_statements:
            return "抱歉，未找到相关信息"

        # 返回基于文档的回答
        return '。'.join(grounded_statements) + '。'

    except Exception as e:
        print(f"Grounding失败: {str(e)}")
        return answer


def split_into_statements(answer):
    """
    将回答拆分成独立的声明

    参数：
        answer: 回答文本

    返回：
        声明列表
    """
    # 按句号、分号、换行符拆分
    import re
    statements = re.split(r'[。；\n]', answer)
    statements = [s.strip() for s in statements if s.strip() and len(s.strip()) > 5]
    return statements


def is_supported_by_context(statement, context):
    """
    检查声明是否能从文档推断

    参数：
        statement: 声明文本
        context: 文档上下文

    返回：
        True/False
    """
    try:
        # 简单方法：检查声明中的关键词是否在文档中
        # 提取声明中的关键词（去掉停用词）
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}

        # 提取关键词
        keywords = []
        for word in statement:
            if len(word) >= 2 and word not in stop_words:
                keywords.append(word)

        # 检查关键词是否在文档中
        if not keywords:
            return True

        matched = sum(1 for kw in keywords if kw in context)
        match_ratio = matched / len(keywords)

        # 如果超过50%的关键词在文档中，认为是支持的
        return match_ratio >= 0.5

    except Exception as e:
        print(f"检查声明失败: {str(e)}")
        return True


def ground_answer_with_llm(answer, context, llm_call):
    """
    使用LLM进行Grounding（更精确但更慢）

    参数：
        answer: LLM生成的回答
        context: 检索到的文档上下文
        llm_call: LLM调用函数

    返回：
        基于文档的回答
    """
    if not answer or not context:
        return answer

    try:
        # 将回答拆分成声明
        statements = split_into_statements(answer)

        if not statements:
            return answer

        # 使用LLM检查每个声明
        grounded_statements = []
        for stmt in statements:
            prompt = f"""判断以下声明是否能从参考文档中推断出来。

声明：{stmt}
参考文档：{context[:1500]}

只回答"是"或"否"。"""

            response = llm_call([{"role": "user", "content": prompt}])

            if "是" in response:
                grounded_statements.append(stmt)

        # 如果没有声明被支持，返回默认消息
        if not grounded_statements:
            return "抱歉，未找到相关信息"

        # 返回基于文档的回答
        return '。'.join(grounded_statements) + '。'

    except Exception as e:
        print(f"LLM Grounding失败: {str(e)}")
        return answer

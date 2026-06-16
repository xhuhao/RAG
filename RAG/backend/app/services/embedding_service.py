"""
文件：embedding_service.py
功能：向量化服务
说明：调用Ollama嵌入模型生成文档向量
"""

import ollama
from flask import current_app

def get_embedding(text):
    """
    获取文本的向量表示

    参数：
        text: 要向量化的文本

    返回：
        向量列表
    """
    try:
        # 从配置获取Ollama设置
        host = current_app.config.get('OLLAMA_HOST', 'localhost')
        port = current_app.config.get('OLLAMA_PORT', 11434)
        model = current_app.config.get('OLLAMA_MODEL', 'qwen3-embedding:4b')

        # 创建Ollama客户端
        client = ollama.Client(host=f'http://{host}:{port}')

        # 获取向量
        response = client.embeddings(model=model, prompt=text)
        return response['embedding']
    except Exception as e:
        raise Exception(f"向量化失败：{str(e)}")

def get_embeddings_batch(texts):
    """
    批量获取文本的向量表示

    参数：
        texts: 文本列表

    返回：
        向量列表
    """
    try:
        embeddings = []
        for text in texts:
            embedding = get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    except Exception as e:
        raise Exception(f"批量向量化失败：{str(e)}")

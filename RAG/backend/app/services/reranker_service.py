"""
文件：reranker_service.py
功能：重排序服务
说明：使用CrossEncoder对检索结果重新排序
"""

from sentence_transformers import CrossEncoder

# 全局重排序模型
_reranker = None

def get_reranker():
    """获取重排序模型实例"""
    global _reranker
    if _reranker is None:
        # 使用中文重排序模型
        _reranker = CrossEncoder('BAAI/bge-reranker-base')
    return _reranker


def rerank_documents(query, documents, top_k=3):
    """
    对文档重新排序

    参数：
        query: 查询文本
        documents: 文档列表 [{"content": "...", "metadata": {...}, "distance": 0.5}]
        top_k: 返回数量

    返回：
        重新排序后的文档列表
    """
    if not documents:
        return []

    try:
        reranker = get_reranker()

        # 构建查询-文档对
        pairs = [(query, doc['content']) for doc in documents]

        # 计算相关性分数
        scores = reranker.predict(pairs)

        # 将分数添加到文档中
        scored_docs = []
        for doc, score in zip(documents, scores):
            doc_copy = doc.copy()
            doc_copy['rerank_score'] = float(score)
            scored_docs.append(doc_copy)

        # 按重排序分数降序排列
        scored_docs.sort(key=lambda x: x['rerank_score'], reverse=True)

        # 返回Top K
        return scored_docs[:top_k]

    except Exception as e:
        print(f"重排序失败: {str(e)}")
        # 失败时返回原始文档
        return documents[:top_k]

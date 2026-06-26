"""
文件：rag_service.py
功能：RAG检索服务
说明：使用Chroma向量数据库进行文档检索
"""

import chromadb
from flask import current_app
from app.services.embedding_service import get_embedding

# Chroma客户端（全局变量）
_chroma_client = None
_collection = None

def get_chroma_client():
    """
    获取Chroma客户端实例

    返回：
        Chroma客户端
    """
    global _chroma_client

    if _chroma_client is None:
        host = current_app.config.get('CHROMA_HOST', 'localhost')
        port = current_app.config.get('CHROMA_PORT', 8000)

        _chroma_client = chromadb.HttpClient(host=host, port=port)

    return _chroma_client

def get_collection():
    """
    获取或创建文档集合

    返回：
        Chroma集合对象
    """
    global _collection

    if _collection is None:
        client = get_chroma_client()
        # 使用自定义嵌入函数，禁用Chroma默认的嵌入函数
        _collection = client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},
            embedding_function=None  # 禁用默认嵌入函数
        )

    return _collection

def add_document_to_chroma(doc_id, chunks, metadata=None):
    """
    将文档块添加到Chroma

    参数：
        doc_id: 文档ID
        chunks: 文本块列表
        metadata: 元数据

    返回：
        添加的块数量
    """
    try:
        collection = get_collection()

        # 为每个块生成ID和向量
        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            # 生成唯一ID
            chunk_id = f"doc_{doc_id}_chunk_{i}"
            ids.append(chunk_id)

            # 文档内容
            documents.append(chunk)

            # 获取向量
            embedding = get_embedding(chunk)
            embeddings.append(embedding)

            # 元数据
            chunk_metadata = {
                'doc_id': doc_id,
                'chunk_index': i,
                'is_active': 1
            }
            if metadata:
                chunk_metadata.update(metadata)
            metadatas.append(chunk_metadata)

        # 添加到Chroma
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return len(chunks)
    except Exception as e:
        raise Exception(f"添加文档到Chroma失败：{str(e)}")

def search_similar_chunks(query, top_k=5, max_distance=0.5):
    """
    搜索相似的文档块（添加距离阈值过滤）

    参数：
        query: 查询文本
        top_k: 返回的结果数量
        max_distance: 最大距离阈值（越小越精确）

    返回：
        相似文档块列表
    """
    try:
        collection = get_collection()

        # 获取查询向量
        query_embedding = get_embedding(query)

        # 搜索相似块
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"is_active": 1}
        )

        # 整理结果（添加距离阈值过滤）
        chunks = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i] if results['distances'] else 0

                # 只返回距离在阈值内的结果
                if distance <= max_distance:
                    chunk = {
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': distance
                    }
                    chunks.append(chunk)

        return chunks
    except Exception as e:
        raise Exception(f"搜索相似文档失败：{str(e)}")

def search_with_context_enrichment(query, top_k=5, max_distance=0.6):
    """
    上下文增强检索（Context Enriched Retrieval）

    检索到相关块后，添加前后块的上下文，让LLM获得更完整的信息

    参数：
        query: 查询文本
        top_k: 返回的结果数量
        max_distance: 最大距离阈值

    返回：
        增强后的文档块列表
    """
    try:
        collection = get_collection()

        # 获取查询向量
        query_embedding = get_embedding(query)

        # 搜索相似块
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"is_active": 1}
        )

        # 整理结果并添加上下文
        enriched_chunks = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i] if results['distances'] else 0
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}

                # 只处理距离在阈值内的结果
                if distance <= max_distance:
                    # 获取当前块的信息
                    doc_id = metadata.get('doc_id')
                    chunk_index = metadata.get('chunk_index', 0)

                    # 获取同一文档的所有块
                    doc_chunks = collection.get(
                        where={"doc_id": doc_id},
                        include=['documents', 'metadatas']
                    )

                    # 构建上下文（添加前后块）
                    context_parts = []
                    if doc_chunks and doc_chunks['documents']:
                        chunks_list = doc_chunks['documents']
                        metadatas_list = doc_chunks['metadatas']

                        # 按chunk_index排序
                        indexed_chunks = list(zip(chunks_list, metadatas_list))
                        indexed_chunks.sort(key=lambda x: x[1].get('chunk_index', 0))

                        # 找到当前块的位置
                        current_idx = None
                        for idx, (chunk, meta) in enumerate(indexed_chunks):
                            if meta.get('chunk_index') == chunk_index:
                                current_idx = idx
                                break

                        if current_idx is not None:
                            # 添加前一块
                            if current_idx > 0:
                                context_parts.append(indexed_chunks[current_idx - 1][0])

                            # 添加当前块
                            context_parts.append(doc)

                            # 添加后一块
                            if current_idx < len(indexed_chunks) - 1:
                                context_parts.append(indexed_chunks[current_idx + 1][0])

                    # 组合上下文
                    enriched_content = '\n\n'.join(context_parts) if context_parts else doc

                    chunk = {
                        'content': enriched_content,
                        'original_content': doc,
                        'metadata': metadata,
                        'distance': distance
                    }
                    enriched_chunks.append(chunk)

        return enriched_chunks
    except Exception as e:
        raise Exception(f"上下文增强检索失败：{str(e)}")


def delete_document_from_chroma(doc_id):
    """
    从Chroma删除文档

    参数：
        doc_id: 文档ID

    返回：
        是否删除成功
    """
    try:
        collection = get_collection()

        # 查找该文档的所有块
        results = collection.get(
            where={"doc_id": doc_id}
        )

        if results and results['ids']:
            # 删除所有块
            collection.delete(ids=results['ids'])

        return True
    except Exception as e:
        raise Exception(f"从Chroma删除文档失败：{str(e)}")

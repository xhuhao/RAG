"""
文件：document_service.py
功能：文档处理服务
说明：处理PDF文档的上传、分块、向量化等操作
"""

import os
from datetime import datetime
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.models import db
from app.models.document import Document
from app.services.rag_service import add_document_to_chroma, delete_document_from_chroma

# 文档分块配置
CHUNK_SIZE = 1000  # 每块1000字符
CHUNK_OVERLAP = 200  # 重叠200字符

def save_uploaded_file(file, upload_folder):
    """
    保存上传的文件

    参数：
        file: 上传的文件对象
        upload_folder: 上传目录路径

    返回：
        保存的文件路径
    """
    # 确保上传目录存在
    os.makedirs(upload_folder, exist_ok=True)

    # 生成唯一的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(upload_folder, filename)

    # 保存文件
    file.save(filepath)

    return filepath

def extract_text_from_pdf(pdf_path):
    """
    从PDF文件中提取文本

    参数：
        pdf_path: PDF文件路径

    返回：
        提取的文本内容
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text.strip()
    except Exception as e:
        raise Exception(f"PDF解析失败：{str(e)}")

def split_text_into_chunks(text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """
    将文本切分成小块

    参数：
        text: 原始文本
        chunk_size: 每块的字符数
        chunk_overlap: 块之间的重叠字符数

    返回：
        文本块列表
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
    )

    chunks = text_splitter.split_text(text)
    return chunks

def create_document_record(title, category, doc_type, url, user_id):
    """
    创建文档记录

    参数：
        title: 文档标题
        category: 分类
        doc_type: 文档类型
        url: 文档URL
        user_id: 上传用户ID

    返回：
        文档记录对象
    """
    try:
        document = Document(
            title=title,
            category=category,
            doc_type=doc_type,
            url=url,
            version=1,
            is_active=1
        )
        db.session.add(document)
        db.session.commit()

        return document
    except Exception as e:
        db.session.rollback()
        raise Exception(f"创建文档记录失败：{str(e)}")

def get_document_list(page=1, per_page=10, keyword=None):
    """
    获取文档列表

    参数：
        page: 页码
        per_page: 每页数量
        keyword: 搜索关键词

    返回：
        文档列表和分页信息
    """
    query = Document.query

    # 关键词搜索
    if keyword:
        query = query.filter(Document.title.like(f'%{keyword}%'))

    # 分页
    pagination = query.order_by(Document.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return {
        'items': [doc.to_dict() for doc in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }

def get_document_by_id(doc_id):
    """
    根据ID获取文档

    参数：
        doc_id: 文档ID

    返回：
        文档记录对象
    """
    return Document.query.get(doc_id)

def update_document_record(doc_id, title=None, category=None, doc_type=None, url=None):
    """
    更新文档记录

    参数：
        doc_id: 文档ID
        title: 文档标题
        category: 分类
        doc_type: 文档类型
        url: 文档URL

    返回：
        更新后的文档记录
    """
    try:
        document = Document.query.get(doc_id)
        if not document:
            raise Exception("文档不存在")

        if title:
            document.title = title
        if category:
            document.category = category
        if doc_type:
            document.doc_type = doc_type
        if url:
            document.url = url

        document.version += 1
        db.session.commit()

        return document
    except Exception as e:
        db.session.rollback()
        raise Exception(f"更新文档失败：{str(e)}")

def delete_document_record(doc_id):
    """
    删除文档记录（标记为归档）

    参数：
        doc_id: 文档ID

    返回：
        是否删除成功
    """
    try:
        document = Document.query.get(doc_id)
        if not document:
            raise Exception("文档不存在")

        # 从Chroma删除向量
        try:
            delete_document_from_chroma(doc_id)
        except Exception as e:
            print(f"从Chroma删除文档失败：{str(e)}")

        document.is_active = 0
        db.session.commit()

        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f"删除文档失败：{str(e)}")

def process_document_upload(file, title, category, doc_type, url, upload_folder):
    """
    处理文档上传的完整流程

    参数：
        file: 上传的文件对象
        title: 文档标题
        category: 分类
        doc_type: 文档类型
        url: 文档URL
        upload_folder: 上传目录路径

    返回：
        文档记录对象
    """
    try:
        # 1. 保存文件
        file_path = save_uploaded_file(file, upload_folder)

        # 2. 提取文本
        text = extract_text_from_pdf(file_path)
        if not text:
            raise Exception("PDF文件无法提取文本")

        # 3. 分块
        chunks = split_text_into_chunks(text)
        print(f"文档分块完成，共 {len(chunks)} 个块")

        # 4. 创建文档记录
        document = create_document_record(title, category, doc_type, url, None)

        # 5. 向量化并存储到Chroma
        metadata = {
            'title': title,
            'category': category,
            'doc_type': doc_type,
            'url': url
        }
        add_document_to_chroma(document.id, chunks, metadata)
        print(f"文档向量化完成，已存储到Chroma")

        return document
    except Exception as e:
        raise Exception(f"处理文档上传失败：{str(e)}")

"""
文件：sync_service.py
功能：同步服务
说明：将爬取的文档同步到系统中，支持下载PDF和向量化
"""

import os
import sys
import re
import time
from datetime import datetime

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from crawlers import (
    GXNUCrawler,
    JWCCrawler,
    YJSCrawler,
    LIBCrawler,
    XGCCrawler,
    ZJCCrawler
)
from app.models import db
from app.models.document import Document
from app.services.document_service import (
    extract_text_from_pdf,
    split_text_into_chunks
)
from app.services.rag_service import add_document_to_chroma

# 爬虫实例
crawlers = {
    'gxnu': GXNUCrawler(),
    'jwc': JWCCrawler(),
    'yjs': YJSCrawler(),
    'lib': LIBCrawler(),
    'xgc': XGCCrawler(),
    'zjc': ZJCCrawler()
}

def extract_text_from_webpage(url):
    """
    从网页提取文本内容

    参数：
        url: 网页URL

    返回：
        提取的文本内容
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')

        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()

        # 提取正文内容
        # 尝试找文章内容区域
        content = None
        for selector in ['.article-content', '.content', '.main-content', 'article', '.post-content']:
            content = soup.select_one(selector)
            if content:
                break

        if not content:
            content = soup.body

        if content:
            text = content.get_text(separator='\n', strip=True)
            # 清理文本
            lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 5]
            return '\n'.join(lines)

        return None
    except Exception as e:
        print(f"提取网页内容失败 {url}: {str(e)}")
        return None

def sync_from_crawler(source, max_pages=5, upload_folder='uploads'):
    """
    从爬虫同步文档（提取网页内容 + 向量化）

    参数：
        source: 数据来源（gxnu/jwc/yjs/lib/xgc/zjc）
        max_pages: 最大爬取页数
        upload_folder: 上传目录

    返回：
        同步结果统计
    """
    if source not in crawlers:
        return {'success': 0, 'failed': 0, 'message': f'未知的数据来源：{source}'}

    crawler = crawlers[source]
    result = {'success': 0, 'failed': 0, 'message': ''}

    # 确保上传目录存在
    upload_path = os.path.join(backend_dir, upload_folder)
    os.makedirs(upload_path, exist_ok=True)

    try:
        # 获取文档列表
        documents = crawler.get_document_list(max_pages)

        for doc in documents:
            try:
                # 检查文档是否已存在
                existing = Document.query.filter_by(url=doc['url']).first()
                if existing:
                    print(f"文档已存在：{doc['title']}")
                    continue

                # 提取网页内容
                text = None
                if doc['url'].lower().endswith('.pdf'):
                    # 如果是PDF，下载并提取文本
                    pdf_path = crawler.download_pdf(doc['url'], upload_path)
                    if pdf_path and os.path.exists(pdf_path):
                        text = extract_text_from_pdf(pdf_path)
                    time.sleep(3)
                else:
                    # 如果是网页，提取网页内容
                    text = extract_text_from_webpage(doc['url'])
                    time.sleep(3)

                # 创建文档记录
                document = Document(
                    title=doc['title'],
                    category=doc['category'],
                    doc_type=doc['doc_type'],
                    url=doc['url'],
                    version=1,
                    is_active=1
                )
                db.session.add(document)
                db.session.commit()

                # 如果提取到文本，进行分块和向量化
                if text and len(text) > 50:
                    try:
                        # 分块
                        chunks = split_text_into_chunks(text)
                        print(f"文档分块完成：{doc['title']}，共 {len(chunks)} 个块")

                        # 向量化并存储到Chroma
                        metadata = {
                            'title': doc['title'],
                            'category': doc['category'],
                            'doc_type': doc['doc_type'],
                            'url': doc['url']
                        }
                        add_document_to_chroma(document.id, chunks, metadata)
                        print(f"向量化完成：{doc['title']}")
                    except Exception as e:
                        print(f"向量化失败：{doc['title']} - {str(e)}")
                else:
                    print(f"未提取到有效内容：{doc['title']}")

                result['success'] += 1
                print(f"同步成功：{doc['title']}")

            except Exception as e:
                db.session.rollback()
                result['failed'] += 1
                print(f"同步失败：{doc['title']} - {str(e)}")

    except Exception as e:
        result['message'] = f'爬取失败：{str(e)}'

    return result

def sync_all(max_pages=5, upload_folder='uploads'):
    """
    同步所有数据来源

    参数：
        max_pages: 每个来源的最大爬取页数
        upload_folder: 上传目录

    返回：
        同步结果统计
    """
    results = {}
    total_success = 0
    total_failed = 0

    for source in crawlers:
        print(f"开始同步 {source}...")
        result = sync_from_crawler(source, max_pages, upload_folder)
        results[source] = result
        total_success += result['success']
        total_failed += result['failed']
        time.sleep(5)  # 不同来源之间间隔5秒

    return {
        'total_success': total_success,
        'total_failed': total_failed,
        'details': results
    }

def download_pdfs_from_website(url, max_pdfs=10, upload_folder='uploads'):
    """
    从网站下载PDF文件

    参数：
        url: 网站URL
        max_pdfs: 最大下载数量
        upload_folder: 上传目录

    返回：
        下载结果统计
    """
    import requests
    from bs4 import BeautifulSoup
    from app.services.document_service import extract_text_from_pdf, split_text_into_chunks
    from app.services.rag_service import add_document_to_chroma

    result = {'success': 0, 'failed': 0, 'message': ''}

    # 确保上传目录存在
    upload_path = os.path.join(backend_dir, upload_folder)
    os.makedirs(upload_path, exist_ok=True)

    try:
        # 获取页面HTML
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.encoding = response.apparent_encoding
        html = response.text

        # 提取PDF链接
        pdf_pattern = r'<a[^>]+href=["\']([^"\']*\.pdf)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pdf_pattern, html, re.DOTALL)

        print(f"找到 {len(matches)} 个PDF链接")

        for href, title_html in matches[:max_pdfs]:
            try:
                # 清理标题
                title = re.sub(r'<[^>]+>', '', title_html).strip()

                # 构建完整URL
                pdf_url = href if href.startswith('http') else f'{url.rstrip("/")}/{href.lstrip("/")}'

                # 如果标题为空，从URL提取
                if not title:
                    title = os.path.basename(href).replace('.pdf', '')

                # 检查是否已存在
                existing = Document.query.filter_by(url=pdf_url).first()
                if existing:
                    print(f"PDF已存在：{title}")
                    continue

                # 下载PDF
                print(f"下载PDF：{title}")
                pdf_response = requests.get(pdf_url, timeout=60, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                pdf_response.raise_for_status()

                # 保存PDF文件
                filename = re.sub(r'[<>:"/\\|?*]', '_', title) + '.pdf'
                filepath = os.path.join(upload_path, filename)

                with open(filepath, 'wb') as f:
                    f.write(pdf_response.content)

                print(f"PDF保存成功：{filename}")

                # 提取PDF文本
                text = extract_text_from_pdf(filepath)
                if not text or len(text) < 50:
                    print(f"PDF文本提取失败或内容过少：{title}")
                    result['failed'] += 1
                    continue

                # 创建文档记录
                document = Document(
                    title=title[:200],
                    category='学校官网',
                    doc_type='PDF文档',
                    url=pdf_url,
                    version=1,
                    is_active=1
                )
                db.session.add(document)
                db.session.commit()

                # 分块
                chunks = split_text_into_chunks(text)
                print(f"文档分块完成：{title}，共 {len(chunks)} 个块")

                # 向量化并存储到Chroma
                metadata = {
                    'title': title,
                    'category': '学校官网',
                    'doc_type': 'PDF文档',
                    'url': pdf_url
                }
                add_document_to_chroma(document.id, chunks, metadata)
                print(f"向量化完成：{title}")

                result['success'] += 1
                time.sleep(3)  # 低频率下载

            except Exception as e:
                print(f"下载PDF失败：{title} - {str(e)}")
                result['failed'] += 1
                continue

    except Exception as e:
        result['message'] = f'获取页面失败：{str(e)}'

    return result

"""
文件：reprocess_all.py
功能：重新处理所有文档
说明：使用新的分块参数重新向量化所有文档
"""

import sys
import os
import time
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.document import Document
from app.models import db
from app.services.document_service import split_text_into_chunks
from app.services.rag_service import add_document_to_chroma
import chromadb

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def extract_text_from_url(url):
    """从URL提取文本内容"""
    try:
        response = requests.get(url, timeout=30, headers=HEADERS)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        for script in soup(['script', 'style']):
            script.decompose()

        content = None
        for selector in ['.article-content', '.content', '.main-content', 'article', '.post-content', '.wp_articlecontent', '#vsb_content', '.v_news_content']:
            content = soup.select_one(selector)
            if content:
                break

        if not content:
            content = soup.body

        if content:
            text = content.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 5]
            return '\n'.join(lines)
        return None
    except Exception as e:
        return None


def extract_text_from_htm(file_path):
    """从HTM文件提取文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')

        for script in soup(['script', 'style']):
            script.decompose()

        paragraphs = soup.find_all('p', class_='p_text_indent_2')
        if paragraphs:
            text = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        else:
            text = soup.get_text(separator='\n', strip=True)

        lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 5]
        return '\n'.join(lines)
    except Exception as e:
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 开始重新处理所有文档")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        # 获取所有文档
        docs = Document.query.filter_by(is_active=1).all()
        print(f'共有 {len(docs)} 篇文档需要处理')

        # 获取Chroma集合
        client = chromadb.HttpClient(host='localhost', port=8000)
        collection = client.get_or_create_collection('knowledge_base')
        print(f'当前向量数: {collection.count()}')

        success_count = 0
        fail_count = 0

        for i, doc in enumerate(docs):
            try:
                print(f'[{i+1}/{len(docs)}] {doc.title[:50]}...')

                # 提取文本
                text = None

                # 检查是否是本地HTM文件
                if 'library.gxnu.edu.cn' in doc.url:
                    # 尝试从本地HTM文件提取
                    title = doc.title.replace('图书馆_', '').replace('[公共服务]', '')
                    htm_file = f'D:/项目/RAG-CC/RAG/uploads/{title}.htm'
                    if os.path.exists(htm_file):
                        text = extract_text_from_htm(htm_file)

                # 如果本地文件没有，从URL提取
                if not text:
                    text = extract_text_from_url(doc.url)

                if text and len(text) > 50:
                    # 分块（使用新的参数）
                    chunks = split_text_into_chunks(text)

                    # 添加到Chroma
                    metadata = {
                        'title': doc.title,
                        'category': doc.category,
                        'doc_type': doc.doc_type,
                        'url': doc.url
                    }
                    add_document_to_chroma(doc.id, chunks, metadata)

                    success_count += 1
                    print(f'  ✅ 成功 ({len(chunks)}块)')
                else:
                    fail_count += 1
                    print(f'  ⚠️ 内容过少')

                # 每100个文档暂停一下
                if (i + 1) % 100 == 0:
                    print(f'  进度: {i+1}/{len(docs)}')
                    time.sleep(1)

            except Exception as e:
                fail_count += 1
                print(f'  ❌ 失败: {str(e)[:50]}')

        print("\n" + "=" * 60)
        print("📊 处理完成")
        print("=" * 60)
        print(f"✅ 成功: {success_count} 篇")
        print(f"❌ 失败: {fail_count} 篇")
        print(f"🔮 向量总数: {collection.count()}")


if __name__ == "__main__":
    main()

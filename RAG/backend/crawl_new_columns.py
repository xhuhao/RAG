"""
文件：crawl_new_columns.py
功能：采集新发现的栏目
说明：采集news.gxnu.edu.cn的8个新栏目
"""

import sys
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.document import Document
from app.models import db
from app.services.document_service import split_text_into_chunks
from app.services.rag_service import add_document_to_chroma

# 新发现的栏目配置
NEW_COLUMNS = [
    {"name": "资讯", "url": "http://news.gxnu.edu.cn/1330/list.htm", "category": "新闻资讯", "doc_type": "资讯"},
    {"name": "视点", "url": "http://news.gxnu.edu.cn/1331/list.htm", "category": "新闻资讯", "doc_type": "视点"},
    {"name": "视觉", "url": "http://news.gxnu.edu.cn/1332/list.htm", "category": "新闻资讯", "doc_type": "视觉"},
    {"name": "全媒体", "url": "http://news.gxnu.edu.cn/1333/list.htm", "category": "新闻资讯", "doc_type": "全媒体"},
    {"name": "影像师大", "url": "http://news.gxnu.edu.cn/1342/list.htm", "category": "新闻资讯", "doc_type": "影像"},
    {"name": "美丽师大", "url": "http://news.gxnu.edu.cn/1344/list.htm", "category": "新闻资讯", "doc_type": "校园风光"},
    {"name": "独秀之声", "url": "http://news.gxnu.edu.cn/1348/list.htm", "category": "新闻资讯", "doc_type": "独秀之声"},
    {"name": "在线投稿", "url": "http://news.gxnu.edu.cn/1438/list.htm", "category": "新闻资讯", "doc_type": "投稿"},
]

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
        for selector in ['.article-content', '.content', '.main-content', 'article', '.post-content', '.wp_articlecontent', '#vsb_content']:
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


def get_article_links_from_list(list_url, max_articles=30):
    """从列表页获取文章链接"""
    try:
        response = requests.get(list_url, timeout=30, headers=HEADERS)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        seen_urls = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text().strip()

            if 'page.htm' in href and title and len(title) > 3:
                full_url = urljoin(list_url, href)

                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    links.append({'title': title, 'url': full_url})

        return links[:max_articles]
    except Exception as e:
        print(f"  获取链接失败: {str(e)}")
        return []


def crawl_single_column(config, app):
    """采集单个栏目"""
    print(f"\n{'='*50}")
    print(f"采集栏目: {config['name']}")
    print(f"URL: {config['url']}")
    print(f"{'='*50}")

    success_count = 0
    fail_count = 0
    skip_count = 0

    links = get_article_links_from_list(config['url'], max_articles=30)
    print(f"  找到 {len(links)} 个文章链接")

    if not links:
        print(f"  ⚠️ 无文章链接，跳过")
        return 0, 0, 0

    with app.app_context():
        for i, link in enumerate(links):
            try:
                print(f"  [{i+1}/{len(links)}] {link['title'][:50]}...")

                existing = Document.query.filter_by(url=link['url']).first()
                if existing:
                    skip_count += 1
                    continue

                text = extract_text_from_url(link['url'])

                if text and len(text) > 50:
                    document = Document(
                        title=link['title'][:200],
                        category=config['category'],
                        doc_type=config['doc_type'],
                        url=link['url'],
                        version=1,
                        is_active=1
                    )
                    db.session.add(document)
                    db.session.commit()

                    chunks = split_text_into_chunks(text)
                    metadata = {
                        'title': link['title'][:200],
                        'category': config['category'],
                        'doc_type': config['doc_type'],
                        'url': link['url']
                    }
                    add_document_to_chroma(document.id, chunks, metadata)

                    success_count += 1
                    print(f"    ✅ 成功 ({len(chunks)}块)")
                else:
                    fail_count += 1
                    print(f"    ⚠️ 内容过少")

                time.sleep(1)

            except Exception as e:
                fail_count += 1
                print(f"    ❌ 失败: {str(e)}")

    print(f"  📊 本栏目统计: 成功{success_count} | 跳过{skip_count} | 失败{fail_count}")
    return success_count, fail_count, skip_count


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 开始采集新发现的栏目")
    print(f"📋 共 {len(NEW_COLUMNS)} 个栏目")
    print("=" * 60)

    app = create_app()

    total_success = 0
    total_fail = 0
    total_skip = 0

    for i, config in enumerate(NEW_COLUMNS):
        print(f"\n[{i+1}/{len(NEW_COLUMNS)}] 进度: {(i+1)/len(NEW_COLUMNS)*100:.1f}%")

        try:
            success, fail, skip = crawl_single_column(config, app)
            total_success += success
            total_fail += fail
            total_skip += skip
        except Exception as e:
            print(f"  ❌ 栏目采集失败: {str(e)}")
            total_fail += 1

        time.sleep(2)

    print("\n" + "=" * 60)
    print("📊 采集完成")
    print("=" * 60)
    print(f"✅ 新增: {total_success} 篇")
    print(f"⏭️ 跳过: {total_skip} 篇（已存在）")
    print(f"❌ 失败: {total_fail} 篇")

    with app.app_context():
        total_docs = Document.query.count()
        print(f"📄 数据库文档总数: {total_docs}")


if __name__ == "__main__":
    main()

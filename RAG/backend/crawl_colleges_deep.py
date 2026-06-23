"""
文件：crawl_colleges_deep.py
功能：深度采集每个院系的所有内容
说明：采集每个院系的新闻、通知、师资、学科等所有内容
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

# 所有院系配置
COLLEGES = [
    {'name': '文学院', 'url': 'http://www.cllc.gxnu.edu.cn/'},
    {'name': '历史文化与旅游学院', 'url': 'http://www.wlxy.gxnu.edu.cn/'},
    {'name': '马克思主义学院', 'url': 'http://www.mar.gxnu.edu.cn/'},
    {'name': '法学院', 'url': 'http://www.law.gxnu.edu.cn/'},
    {'name': '政治与公共管理学院', 'url': 'http://www.zgxy.gxnu.edu.cn/'},
    {'name': '经济管理学院', 'url': 'http://www.em.gxnu.edu.cn/'},
    {'name': '教育学部', 'url': 'http://jyxb.gxnu.edu.cn/'},
    {'name': '外国语学院', 'url': 'http://www.cofs.gxnu.edu.cn/'},
    {'name': '美术学院', 'url': 'http://www.art.gxnu.edu.cn/'},
    {'name': '音乐学院', 'url': 'http://www.music.gxnu.edu.cn/'},
    {'name': '数学与统计学院', 'url': 'http://www.math.gxnu.edu.cn/'},
    {'name': '物理科学与技术学院', 'url': 'http://www.pe.gxnu.edu.cn/'},
    {'name': '化学与药学学院', 'url': 'http://www.ce.gxnu.edu.cn/'},
    {'name': '生命科学学院', 'url': 'http://www.bio.gxnu.edu.cn/'},
    {'name': '环境与资源学院', 'url': 'http://www.zhx.gxnu.edu.cn/'},
    {'name': '计算机科学与工程学院', 'url': 'http://www.cs.gxnu.edu.cn/'},
    {'name': '体育与健康学院', 'url': 'http://www.tyxy.gxnu.edu.cn/'},
    {'name': '电子与信息工程学院', 'url': 'http://www.ee.gxnu.edu.cn/'},
    {'name': '职业技术师范学院', 'url': 'http://www.zsxy.gxnu.edu.cn/'},
    {'name': '设计学院', 'url': 'http://www.d.gxnu.edu.cn/'},
    {'name': '国际文化教育学院', 'url': 'http://www.cice.gxnu.edu.cn/'},
    {'name': '出版学院', 'url': 'https://cbxy.gxnu.edu.cn/'},
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


def get_all_article_links(base_url, max_articles=50):
    """获取网站所有文章链接"""
    try:
        response = requests.get(base_url, timeout=30, headers=HEADERS)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        seen_urls = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text().strip()

            # 只要文章详情页
            if 'page.htm' in href and title and len(title) > 3:
                full_url = urljoin(base_url, href)

                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    links.append({'title': title, 'url': full_url})

        return links[:max_articles]
    except Exception as e:
        return []


def crawl_college_deep(college, app):
    """深度采集单个院系"""
    print(f"\n{'='*60}")
    print(f"深度采集: {college['name']}")
    print(f"URL: {college['url']}")
    print(f"{'='*60}")

    success_count = 0
    fail_count = 0
    skip_count = 0

    # 获取所有文章链接
    links = get_all_article_links(college['url'], max_articles=50)
    print(f"  找到 {len(links)} 个文章链接")

    if not links:
        print(f"  ⚠️ 无文章链接")
        return 0, 0, 0

    with app.app_context():
        for i, link in enumerate(links):
            try:
                print(f"  [{i+1}/{len(links)}] {link['title'][:50]}...")

                # 检查是否已存在
                existing = Document.query.filter_by(url=link['url']).first()
                if existing:
                    skip_count += 1
                    continue

                # 提取文本
                text = extract_text_from_url(link['url'])

                if text and len(text) > 50:
                    # 创建文档记录
                    document = Document(
                        title=f"[{college['name']}]{link['title'][:150]}",
                        category='院系动态',
                        doc_type='院系新闻',
                        url=link['url'],
                        version=1,
                        is_active=1
                    )
                    db.session.add(document)
                    db.session.commit()

                    # 分块并添加到Chroma
                    chunks = split_text_into_chunks(text)
                    metadata = {
                        'title': f"[{college['name']}]{link['title'][:150]}",
                        'category': '院系动态',
                        'doc_type': '院系新闻',
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

    print(f"  📊 本院系统计: 成功{success_count} | 跳过{skip_count} | 失败{fail_count}")
    return success_count, fail_count, skip_count


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 开始深度采集每个院系的所有内容")
    print(f"📋 共 {len(COLLEGES)} 个院系")
    print("=" * 60)

    app = create_app()

    total_success = 0
    total_fail = 0
    total_skip = 0

    for i, college in enumerate(COLLEGES):
        print(f"\n[{i+1}/{len(COLLEGES)}] 进度: {(i+1)/len(COLLEGES)*100:.1f}%")

        try:
            success, fail, skip = crawl_college_deep(college, app)
            total_success += success
            total_fail += fail
            total_skip += skip
        except Exception as e:
            print(f"  ❌ 院系采集失败: {str(e)}")
            total_fail += 1

        time.sleep(3)  # 院系间隔3秒

    print("\n" + "=" * 60)
    print("📊 深度采集完成")
    print("=" * 60)
    print(f"✅ 新增: {total_success} 篇")
    print(f"⏭️ 跳过: {total_skip} 篇（已存在）")
    print(f"❌ 失败: {total_fail} 篇")

    with app.app_context():
        total_docs = Document.query.count()
        print(f"📄 数据库文档总数: {total_docs}")


if __name__ == "__main__":
    main()

"""
文件：crawl_departments_deep.py
功能：深度采集各部门和服务网站的所有内容
说明：采集8个部门和服务网站的所有可采集内容
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

# 部门和服务网站配置
DEPARTMENTS = [
    {'name': '党政群团部门', 'url': 'http://www.gxnu.edu.cn/1376/list.htm', 'category': '机构设置', 'doc_type': '部门介绍'},
    {'name': '招生信息', 'url': 'http://www.gxnu.edu.cn/1385/list.htm', 'category': '招生就业', 'doc_type': '招生信息'},
    {'name': '大学生就业网', 'url': 'http://gxnu.bysjy.com.cn/', 'category': '招生就业', 'doc_type': '就业信息'},
    {'name': '教学服务', 'url': 'http://www.gxnu.edu.cn/1389/list.htm', 'category': '公共服务', 'doc_type': '服务信息'},
    {'name': '办公服务', 'url': 'http://www.gxnu.edu.cn/1390/list.htm', 'category': '公共服务', 'doc_type': '服务信息'},
    {'name': '网络服务', 'url': 'http://www.nc.gxnu.edu.cn/', 'category': '公共服务', 'doc_type': '服务信息'},
    {'name': '后勤服务集团', 'url': 'https://hqjt.gxnu.edu.cn/', 'category': '公共服务', 'doc_type': '服务信息'},
    {'name': '其他服务', 'url': 'http://www.gxnu.edu.cn/1393/list.htm', 'category': '公共服务', 'doc_type': '服务信息'},
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


def get_all_links(base_url, max_links=50):
    """获取网站所有链接"""
    try:
        response = requests.get(base_url, timeout=30, headers=HEADERS)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        seen_urls = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text().strip()

            # 只要文章详情页或列表页
            if ('page.htm' in href or 'list.htm' in href) and title and len(title) > 3:
                full_url = urljoin(base_url, href)

                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    links.append({'title': title, 'url': full_url})

        return links[:max_links]
    except Exception as e:
        return []


def crawl_department_deep(dept, app):
    """深度采集单个部门"""
    print(f"\n{'='*60}")
    print(f"深度采集: {dept['name']}")
    print(f"URL: {dept['url']}")
    print(f"分类: {dept['category']} | 类型: {dept['doc_type']}")
    print(f"{'='*60}")

    success_count = 0
    fail_count = 0
    skip_count = 0

    # 获取所有链接
    links = get_all_links(dept['url'], max_links=50)
    print(f"  找到 {len(links)} 个链接")

    if not links:
        # 如果没有子链接，直接采集当前页面
        print(f"  无子链接，直接采集当前页面")
        with app.app_context():
            text = extract_text_from_url(dept['url'])
            if text and len(text) > 50:
                existing = Document.query.filter_by(url=dept['url']).first()
                if existing:
                    print(f"  已存在: ID={existing.id}")
                else:
                    document = Document(
                        title=dept['name'],
                        category=dept['category'],
                        doc_type=dept['doc_type'],
                        url=dept['url'],
                        version=1,
                        is_active=1
                    )
                    db.session.add(document)
                    db.session.commit()

                    chunks = split_text_into_chunks(text)
                    metadata = {
                        'title': dept['name'],
                        'category': dept['category'],
                        'doc_type': dept['doc_type'],
                        'url': dept['url']
                    }
                    add_document_to_chroma(document.id, chunks, metadata)

                    success_count += 1
                    print(f"  ✅ 成功: {len(text)}字, {len(chunks)}块")
            else:
                fail_count += 1
                print(f"  ⚠️ 内容过少")
        return success_count, fail_count, skip_count

    # 有子链接，逐个采集
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
                        title=f"[{dept['name']}]{link['title'][:150]}",
                        category=dept['category'],
                        doc_type=dept['doc_type'],
                        url=link['url'],
                        version=1,
                        is_active=1
                    )
                    db.session.add(document)
                    db.session.commit()

                    # 分块并添加到Chroma
                    chunks = split_text_into_chunks(text)
                    metadata = {
                        'title': f"[{dept['name']}]{link['title'][:150]}",
                        'category': dept['category'],
                        'doc_type': dept['doc_type'],
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

    print(f"  📊 本部门统计: 成功{success_count} | 跳过{skip_count} | 失败{fail_count}")
    return success_count, fail_count, skip_count


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 开始深度采集各部门和服务网站")
    print(f"📋 共 {len(DEPARTMENTS)} 个网站")
    print("=" * 60)

    app = create_app()

    total_success = 0
    total_fail = 0
    total_skip = 0

    for i, dept in enumerate(DEPARTMENTS):
        print(f"\n[{i+1}/{len(DEPARTMENTS)}] 进度: {(i+1)/len(DEPARTMENTS)*100:.1f}%")

        try:
            success, fail, skip = crawl_department_deep(dept, app)
            total_success += success
            total_fail += fail
            total_skip += skip
        except Exception as e:
            print(f"  ❌ 网站采集失败: {str(e)}")
            total_fail += 1

        time.sleep(3)

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

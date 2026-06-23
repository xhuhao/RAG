"""
文件：crawl_cice_deep.py
功能：深度采集国际文化教育学院网站的所有内容
说明：采集25个栏目的所有文章
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

# 国际文化教育学院的所有栏目
CICE_COLUMNS = [
    {'name': '单位概况', 'url': 'http://www.cice.gxnu.edu.cn/1098/list.htm'},
    {'name': '院处动态', 'url': 'http://www.cice.gxnu.edu.cn/1099/list.htm'},
    {'name': '因公出国（境）', 'url': 'http://www.cice.gxnu.edu.cn/1100/list.htm'},
    {'name': '孔子学院', 'url': 'http://www.cice.gxnu.edu.cn/1101/list.htm'},
    {'name': '留学师大', 'url': 'http://www.cice.gxnu.edu.cn/1102/list.htm'},
    {'name': '合作办学', 'url': 'http://www.cice.gxnu.edu.cn/1103/list.htm'},
    {'name': '境外学习', 'url': 'http://www.cice.gxnu.edu.cn/1104/list.htm'},
    {'name': '外专外教', 'url': 'http://www.cice.gxnu.edu.cn/1105/list.htm'},
    {'name': '单位简介', 'url': 'http://www.cice.gxnu.edu.cn/1106/list.htm'},
    {'name': '领导分工', 'url': 'http://www.cice.gxnu.edu.cn/1107/list.htm'},
    {'name': '科室设置', 'url': 'http://www.cice.gxnu.edu.cn/1108/list.htm'},
    {'name': '深入学习贯彻党的二十大精神', 'url': 'http://www.cice.gxnu.edu.cn/11080/list.htm'},
    {'name': '清廉师大', 'url': 'http://www.cice.gxnu.edu.cn/11081/list.htm'},
    {'name': '国际交流', 'url': 'http://www.cice.gxnu.edu.cn/1110/list.htm'},
    {'name': '孔院动态', 'url': 'http://www.cice.gxnu.edu.cn/1111/list.htm'},
    {'name': '院处工作', 'url': 'http://www.cice.gxnu.edu.cn/1112/list.htm'},
    {'name': '媒体报道', 'url': 'http://www.cice.gxnu.edu.cn/1113/list.htm'},
    {'name': '党团建设', 'url': 'http://www.cice.gxnu.edu.cn/1115/list.htm'},
    {'name': '留学生动态', 'url': 'http://www.cice.gxnu.edu.cn/1116/list.htm'},
    {'name': '国际文化节', 'url': 'http://www.cice.gxnu.edu.cn/1117/list.htm'},
    {'name': '中国学生动态', 'url': 'http://www.cice.gxnu.edu.cn/1118/list.htm'},
    {'name': '国际文化讲座', 'url': 'http://www.cice.gxnu.edu.cn/1119/list.htm'},
    {'name': '举办国际会议', 'url': 'http://www.cice.gxnu.edu.cn/1120/list.htm'},
    {'name': '签证要求', 'url': 'http://www.cice.gxnu.edu.cn/1121/list.htm'},
    {'name': '因公出国、赴港澳', 'url': 'http://www.cice.gxnu.edu.cn/1122/list.htm'},
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

    # 获取文章链接
    links = get_article_links_from_list(config['url'], max_articles=30)
    print(f"  找到 {len(links)} 个文章链接")

    if not links:
        print(f"  ⚠️ 无文章链接，跳过")
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
                        title=f"[国际文化教育学院]{link['title'][:150]}",
                        category='合作交流',
                        doc_type='国际交流',
                        url=link['url'],
                        version=1,
                        is_active=1
                    )
                    db.session.add(document)
                    db.session.commit()

                    # 分块并添加到Chroma
                    chunks = split_text_into_chunks(text)
                    metadata = {
                        'title': f"[国际文化教育学院]{link['title'][:150]}",
                        'category': '合作交流',
                        'doc_type': '国际交流',
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
    print("🚀 开始深度采集国际文化教育学院网站")
    print(f"📋 共 {len(CICE_COLUMNS)} 个栏目")
    print("=" * 60)

    app = create_app()

    total_success = 0
    total_fail = 0
    total_skip = 0

    for i, config in enumerate(CICE_COLUMNS):
        print(f"\n[{i+1}/{len(CICE_COLUMNS)}] 进度: {(i+1)/len(CICE_COLUMNS)*100:.1f}%")

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

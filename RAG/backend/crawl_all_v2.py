"""
文件：crawl_all_v2.py
功能：深度采集广西师范大学官网所有栏目
说明：进入每个栏目列表页，采集所有文章
"""

import sys
import os
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.document import Document
from app.models import db
from app.services.document_service import split_text_into_chunks
from app.services.rag_service import add_document_to_chroma

# 所有采集栏目配置
CRAWL_CONFIGS = [
    # 学校概况
    {"name": "学校简介", "url": "http://www.gxnu.edu.cn/1365/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "学校沿革", "url": "http://www.gxnu.edu.cn/1366/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "现任领导", "url": "http://www.gxnu.edu.cn/1367/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "历届党组织负责人", "url": "http://www.gxnu.edu.cn/1368/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "历届行政领导", "url": "http://www.gxnu.edu.cn/1369/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "校园地图", "url": "http://www.gxnu.edu.cn/1370/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "学校章程", "url": "http://www.gxnu.edu.cn/xxzc/list.htm", "category": "学校概况", "doc_type": "规章制度"},

    # 机构设置
    {"name": "教学单位", "url": "http://www.gxnu.edu.cn/1375/list.htm", "category": "机构设置", "doc_type": "部门介绍"},
    {"name": "党政群团部门", "url": "http://www.gxnu.edu.cn/1376/list.htm", "category": "机构设置", "doc_type": "部门介绍"},
    {"name": "派驻机构", "url": "http://www.gxnu.edu.cn/pzjg/list.htm", "category": "机构设置", "doc_type": "部门介绍"},
    {"name": "业务部门", "url": "http://www.gxnu.edu.cn/1377/list.htm", "category": "机构设置", "doc_type": "部门介绍"},
    {"name": "附属单位", "url": "http://www.gxnu.edu.cn/1378/list.htm", "category": "机构设置", "doc_type": "部门介绍"},

    # 学术研究
    {"name": "科研管理", "url": "http://www.gxnu.edu.cn/1381/list.htm", "category": "学术研究", "doc_type": "科研信息"},
    {"name": "科研机构", "url": "http://www.gxnu.edu.cn/1382/list.htm", "category": "学术研究", "doc_type": "科研信息"},
    {"name": "重点学科", "url": "http://www.gxnu.edu.cn/1383/list.htm", "category": "学术研究", "doc_type": "学科信息"},
    {"name": "学术刊物", "url": "http://www.gxnu.edu.cn/1384/list.htm", "category": "学术研究", "doc_type": "学术信息"},

    # 招生就业
    {"name": "招生信息", "url": "http://www.gxnu.edu.cn/1385/list.htm", "category": "招生就业", "doc_type": "招生信息"},

    # 公共服务
    {"name": "教学服务", "url": "http://www.gxnu.edu.cn/1389/list.htm", "category": "公共服务", "doc_type": "服务信息"},
    {"name": "办公服务", "url": "http://www.gxnu.edu.cn/1390/list.htm", "category": "公共服务", "doc_type": "服务信息"},
    {"name": "其他服务", "url": "http://www.gxnu.edu.cn/1393/list.htm", "category": "公共服务", "doc_type": "服务信息"},

    # 大学文化
    {"name": "广西师范大学颂", "url": "http://www.gxnu.edu.cn/gxsfdxs/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "校歌 校训 校徽", "url": "http://www.gxnu.edu.cn/1371/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "广西师范大学精神", "url": "http://www.gxnu.edu.cn/gxsfdxjs/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "校园十大文化景观", "url": "http://www.gxnu.edu.cn/xysdwhjg/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "雁栖湖碑刻景观", "url": "http://www.gxnu.edu.cn/yqhbkjg/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "博物馆", "url": "http://www.gxnu.edu.cn/bwg/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "学校视觉形象识别系统", "url": "http://www.gxnu.edu.cn/1374/list.htm", "category": "大学文化", "doc_type": "校园文化"},

    # 首页新闻
    {"name": "首页新闻", "url": "http://www.gxnu.edu.cn/4342/list.htm", "category": "新闻资讯", "doc_type": "新闻公告"},

    # 新闻资讯
    {"name": "师大要闻", "url": "http://news.gxnu.edu.cn/1334/list.htm", "category": "新闻资讯", "doc_type": "新闻公告"},
    {"name": "校园人物", "url": "http://news.gxnu.edu.cn/1340/list.htm", "category": "新闻资讯", "doc_type": "人物专访"},
    {"name": "学术活动", "url": "http://news.gxnu.edu.cn/1335/list.htm", "category": "新闻资讯", "doc_type": "学术活动"},
    {"name": "媒体关注", "url": "http://news.gxnu.edu.cn/1336/list.htm", "category": "新闻资讯", "doc_type": "媒体报道"},
    {"name": "综合新闻", "url": "http://news.gxnu.edu.cn/1337/list.htm", "category": "新闻资讯", "doc_type": "新闻公告"},

    # 专题专栏
    {"name": "树立和践行正确政绩观", "url": "http://news.gxnu.edu.cn/slhjxzqzjgxxjy/list.htm", "category": "专题专栏", "doc_type": "专题学习"},
    {"name": "党史学习教育", "url": "http://news.gxnu.edu.cn/dsxxjy/list.htm", "category": "专题专栏", "doc_type": "专题学习"},
    {"name": "乡村振兴", "url": "http://news.gxnu.edu.cn/tpgj/list.htm", "category": "专题专栏", "doc_type": "专题学习"},
    {"name": "全国文明校园", "url": "http://news.gxnu.edu.cn/wmxy/list.htm", "category": "专题专栏", "doc_type": "专题学习"},
    {"name": "清廉师大", "url": "http://news.gxnu.edu.cn/qlsd/list.htm", "category": "专题专栏", "doc_type": "专题学习"},
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

        # 查找所有包含page.htm的链接（文章详情页）
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text().strip()

            # 只要文章详情页
            if 'page.htm' in href and title and len(title) > 3:
                full_url = urljoin(list_url, href)

                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    links.append({'title': title, 'url': full_url})

        return links[:max_articles]
    except Exception as e:
        print(f"  获取链接失败: {str(e)}")
        return []


def crawl_single_config(config, app):
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
                        title=link['title'][:200],
                        category=config['category'],
                        doc_type=config['doc_type'],
                        url=link['url'],
                        version=1,
                        is_active=1
                    )
                    db.session.add(document)
                    db.session.commit()

                    # 分块并添加到Chroma
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
    print("🚀 开始深度采集广西师范大学官网")
    print(f"📋 共 {len(CRAWL_CONFIGS)} 个栏目")
    print("=" * 60)

    app = create_app()

    total_success = 0
    total_fail = 0
    total_skip = 0

    for i, config in enumerate(CRAWL_CONFIGS):
        print(f"\n[{i+1}/{len(CRAWL_CONFIGS)}] 进度: {(i+1)/len(CRAWL_CONFIGS)*100:.1f}%")

        try:
            success, fail, skip = crawl_single_config(config, app)
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

"""
文件：crawl_all.py
功能：批量采集广西师范大学官网所有栏目
说明：采集49个子栏目，预估510-930篇文档
"""

import sys
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.document import Document
from app.models import db
from app.services.document_service import split_text_into_chunks
from app.services.rag_service import add_document_to_chroma

# 所有采集栏目配置
CRAWL_CONFIGS = [
    # 一、学校概况
    {"name": "学校简介", "url": "http://www.gxnu.edu.cn/1365/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "学校沿革", "url": "http://www.gxnu.edu.cn/1366/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "现任领导", "url": "http://www.gxnu.edu.cn/1367/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "历届党组织负责人", "url": "http://www.gxnu.edu.cn/1368/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "历届行政领导", "url": "http://www.gxnu.edu.cn/1369/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "校园地图", "url": "http://www.gxnu.edu.cn/1370/list.htm", "category": "学校概况", "doc_type": "基本信息"},
    {"name": "学校章程", "url": "http://www.gxnu.edu.cn/xxzc/list.htm", "category": "学校概况", "doc_type": "规章制度"},

    # 二、机构设置
    {"name": "教学单位", "url": "http://www.gxnu.edu.cn/1375/list.htm", "category": "机构设置", "doc_type": "部门介绍"},
    {"name": "党政群团部门", "url": "http://www.gxnu.edu.cn/1376/list.htm", "category": "机构设置", "doc_type": "部门介绍"},
    {"name": "派驻机构", "url": "http://www.gxnu.edu.cn/pzjg/list.htm", "category": "机构设置", "doc_type": "部门介绍"},
    {"name": "业务部门", "url": "http://www.gxnu.edu.cn/1377/list.htm", "category": "机构设置", "doc_type": "部门介绍"},
    {"name": "附属单位", "url": "http://www.gxnu.edu.cn/1378/list.htm", "category": "机构设置", "doc_type": "部门介绍"},

    # 三、人才队伍
    {"name": "师资队伍", "url": "http://hr.gxnu.edu.cn/", "category": "人才队伍", "doc_type": "师资信息"},
    {"name": "人才招聘", "url": "https://mp.weixin.qq.com/s/L3POAIXr6SHAKIQpHQ7NqQ", "category": "人才队伍", "doc_type": "招聘信息"},

    # 四、学术研究
    {"name": "科研管理", "url": "http://www.gxnu.edu.cn/1381/list.htm", "category": "学术研究", "doc_type": "科研信息"},
    {"name": "科研机构", "url": "http://www.gxnu.edu.cn/1382/list.htm", "category": "学术研究", "doc_type": "科研信息"},
    {"name": "重点学科", "url": "http://www.gxnu.edu.cn/1383/list.htm", "category": "学术研究", "doc_type": "学科信息"},
    {"name": "学术刊物", "url": "http://www.gxnu.edu.cn/1384/list.htm", "category": "学术研究", "doc_type": "学术信息"},

    # 五、招生就业
    {"name": "招生信息", "url": "http://www.gxnu.edu.cn/1385/list.htm", "category": "招生就业", "doc_type": "招生信息"},
    {"name": "大学生就业网", "url": "http://gxnu.bysjy.com.cn/", "category": "招生就业", "doc_type": "就业信息"},

    # 六、图书档案
    {"name": "图书馆", "url": "http://www.library.gxnu.edu.cn/", "category": "图书档案", "doc_type": "图书馆"},
    {"name": "档案馆", "url": "http://dag.gxnu.edu.cn/", "category": "图书档案", "doc_type": "档案信息"},

    # 七、公共服务
    {"name": "教学服务", "url": "http://www.gxnu.edu.cn/1389/list.htm", "category": "公共服务", "doc_type": "服务信息"},
    {"name": "办公服务", "url": "http://www.gxnu.edu.cn/1390/list.htm", "category": "公共服务", "doc_type": "服务信息"},
    {"name": "网络服务", "url": "http://www.nc.gxnu.edu.cn/", "category": "公共服务", "doc_type": "服务信息"},
    {"name": "后勤服务集团", "url": "http://hqjt.gxnu.edu.cn", "category": "公共服务", "doc_type": "服务信息"},
    {"name": "其他服务", "url": "http://www.gxnu.edu.cn/1393/list.htm", "category": "公共服务", "doc_type": "服务信息"},

    # 八、校友天地
    {"name": "校友天地", "url": "http://xyzh.gxnu.edu.cn/", "category": "校友天地", "doc_type": "校友信息"},

    # 九、合作交流
    {"name": "合作交流", "url": "http://www.cice.gxnu.edu.cn/", "category": "合作交流", "doc_type": "交流合作"},

    # 十、大学文化
    {"name": "广西师范大学颂", "url": "http://www.gxnu.edu.cn/gxsfdxs/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "校歌 校训 校徽", "url": "http://www.gxnu.edu.cn/1371/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "广西师范大学精神", "url": "http://www.gxnu.edu.cn/gxsfdxjs/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "校园十大文化景观", "url": "http://www.gxnu.edu.cn/xysdwhjg/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "雁栖湖碑刻景观", "url": "http://www.gxnu.edu.cn/yqhbkjg/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "博物馆", "url": "http://www.gxnu.edu.cn/bwg/list.htm", "category": "大学文化", "doc_type": "校园文化"},
    {"name": "学校视觉形象识别系统", "url": "http://www.gxnu.edu.cn/1374/list.htm", "category": "大学文化", "doc_type": "校园文化"},

    # 十一、出版社集团
    {"name": "出版社集团", "url": "http://www.bbtpress.com", "category": "出版社集团", "doc_type": "出版信息"},

    # 十二、首页新闻
    {"name": "首页新闻", "url": "http://www.gxnu.edu.cn/4342/list.htm", "category": "新闻资讯", "doc_type": "新闻公告"},

    # 十三、新闻资讯
    {"name": "师大要闻", "url": "http://news.gxnu.edu.cn/1334/list.htm", "category": "新闻资讯", "doc_type": "新闻公告"},
    {"name": "校园人物", "url": "http://news.gxnu.edu.cn/1340/list.htm", "category": "新闻资讯", "doc_type": "人物专访"},
    {"name": "学术活动", "url": "http://news.gxnu.edu.cn/1335/list.htm", "category": "新闻资讯", "doc_type": "学术活动"},
    {"name": "媒体关注", "url": "http://news.gxnu.edu.cn/1336/list.htm", "category": "新闻资讯", "doc_type": "媒体报道"},
    {"name": "综合新闻", "url": "http://news.gxnu.edu.cn/1337/list.htm", "category": "新闻资讯", "doc_type": "新闻公告"},

    # 十四、专题专栏
    {"name": "树立和践行正确政绩观", "url": "http://news.gxnu.edu.cn/slhjxzqzjgxxjy/list.htm", "category": "专题专栏", "doc_type": "专题学习"},
    {"name": "党史学习教育", "url": "http://news.gxnu.edu.cn/dsxxjy/list.htm", "category": "专题专栏", "doc_type": "专题学习"},
    {"name": "乡村振兴", "url": "http://news.gxnu.edu.cn/tpgj/list.htm", "category": "专题专栏", "doc_type": "专题学习"},
    {"name": "全国文明校园", "url": "http://news.gxnu.edu.cn/wmxy/list.htm", "category": "专题专栏", "doc_type": "专题学习"},
    {"name": "清廉师大", "url": "http://news.gxnu.edu.cn/qlsd/list.htm", "category": "专题专栏", "doc_type": "专题学习"},
]


def extract_text_from_url(url):
    """从URL提取文本内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')

        # 移除script和style标签
        for script in soup(['script', 'style']):
            script.decompose()

        # 提取正文内容
        content = None
        for selector in ['.article-content', '.content', '.main-content', 'article', '.post-content', '.wp_articlecontent']:
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
        print(f"  提取失败: {str(e)}")
        return None


def get_article_links(list_url, max_articles=30):
    """获取列表页中的文章链接"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(list_url, timeout=30, headers=headers)
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找文章链接
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text().strip()

            # 过滤有效链接
            if ('page.htm' in href or 'list.htm' in href) and title and len(title) > 5:
                full_url = urljoin(list_url, href)
                links.append({'title': title, 'url': full_url})

        # 去重
        seen = set()
        unique_links = []
        for link in links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)

        return unique_links[:max_articles]
    except Exception as e:
        print(f"  获取链接失败: {str(e)}")
        return []


def crawl_single_config(config, app):
    """采集单个栏目"""
    print(f"\n{'='*50}")
    print(f"采集栏目: {config['name']}")
    print(f"URL: {config['url']}")
    print(f"分类: {config['category']} | 类型: {config['doc_type']}")
    print(f"{'='*50}")

    success_count = 0
    fail_count = 0

    with app.app_context():
        # 获取文章链接
        links = get_article_links(config['url'], max_articles=10)

        if not links:
            # 如果没有子链接，直接采集当前页面
            print(f"  无子链接，直接采集当前页面")
            text = extract_text_from_url(config['url'])

            if text and len(text) > 50:
                # 检查是否已存在
                existing = Document.query.filter_by(url=config['url']).first()
                if existing:
                    print(f"  文档已存在，跳过")
                    return 0, 0

                # 创建文档记录
                document = Document(
                    title=config['name'],
                    category=config['category'],
                    doc_type=config['doc_type'],
                    url=config['url'],
                    version=1,
                    is_active=1
                )
                db.session.add(document)
                db.session.commit()

                # 分块并添加到Chroma
                chunks = split_text_into_chunks(text)
                metadata = {
                    'title': config['name'],
                    'category': config['category'],
                    'doc_type': config['doc_type'],
                    'url': config['url']
                }
                add_document_to_chroma(document.id, chunks, metadata)

                print(f"  ✅ 成功: {config['name']} ({len(chunks)}块)")
                return 1, 0
            else:
                print(f"  ⚠️ 内容过少或提取失败")
                return 0, 1

        # 有子链接，逐个采集
        print(f"  找到 {len(links)} 个文章链接")

        for i, link in enumerate(links):
            try:
                print(f"  [{i+1}/{len(links)}] {link['title'][:40]}...")

                # 检查是否已存在
                existing = Document.query.filter_by(url=link['url']).first()
                if existing:
                    print(f"    已存在，跳过")
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

                time.sleep(1)  # 间隔1秒

            except Exception as e:
                fail_count += 1
                print(f"    ❌ 失败: {str(e)}")

    return success_count, fail_count


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 开始批量采集广西师范大学官网")
    print(f"📋 共 {len(CRAWL_CONFIGS)} 个栏目")
    print("=" * 60)

    app = create_app()

    total_success = 0
    total_fail = 0

    for i, config in enumerate(CRAWL_CONFIGS):
        print(f"\n[{i+1}/{len(CRAWL_CONFIGS)}] 进度: {(i+1)/len(CRAWL_CONFIGS)*100:.1f}%")

        try:
            success, fail = crawl_single_config(config, app)
            total_success += success
            total_fail += fail
        except Exception as e:
            print(f"  ❌ 栏目采集失败: {str(e)}")
            total_fail += 1

        time.sleep(2)  # 栏目间隔2秒

    print("\n" + "=" * 60)
    print("📊 采集完成")
    print("=" * 60)
    print(f"✅ 成功: {total_success} 篇")
    print(f"❌ 失败: {total_fail} 篇")

    # 统计总数
    with app.app_context():
        total_docs = Document.query.count()
        print(f"📄 数据库文档总数: {total_docs}")


if __name__ == "__main__":
    main()

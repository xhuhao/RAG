"""
文件：gxnu_crawler.py
功能：广西师范大学官网爬虫
说明：爬取学校官网的新闻公告
根据web-scraping技能最佳实践实现
"""

import re
import time
from crawlers.base_crawler import BaseCrawler

class GXNUCrawler(BaseCrawler):
    """
    广西师范大学官网爬虫

    爬取学校官网的新闻公告
    """

    def __init__(self):
        super().__init__(
            base_url="https://news.gxnu.edu.cn",
            source_name="学校官网"
        )

    def crawl(self, max_pages=5):
        """
        爬取学校官网的新闻公告

        参数：
            max_pages: 最大爬取页数

        返回：
            文档列表
        """
        documents = []

        # 新闻网和学校官网页面URL
        notice_urls = [
            "https://news.gxnu.edu.cn/",
            "https://news.gxnu.edu.cn/1334/list.htm",  # 师大要闻
            "https://news.gxnu.edu.cn/1335/list.htm",  # 大学学院
            "https://news.gxnu.edu.cn/1336/list.htm",  # 校园资讯
            "https://news.gxnu.edu.cn/1337/list.htm",  # 媒体师大
            "https://news.gxnu.edu.cn/1338/list.htm",  # 视频师大
            "https://news.gxnu.edu.cn/1340/list.htm",  # 师大学人
            "https://news.gxnu.edu.cn/1342/list.htm",  # 影像师大
            "https://news.gxnu.edu.cn/1344/list.htm",  # 校友师大
            "https://news.gxnu.edu.cn/1348/list.htm",  # 阅读师大
            "https://www.gxnu.edu.cn/1441/list.htm",   # 学校通知
            "https://www.gxnu.edu.cn/1442/list.htm",   # 学校新闻
        ]

        for notice_url in notice_urls:
            try:
                # 获取页面HTML
                response = self.session.get(notice_url, timeout=30)
                response.encoding = response.apparent_encoding
                html = response.text

                # 使用正则表达式提取page.htm链接和对应的标题
                pattern = r'<a[^>]+href=["\']([^"\']*page\.htm)["\'][^>]*>(.*?)</a>'
                matches = re.findall(pattern, html, re.DOTALL)

                for href, title_html in matches[:max_pages * 3]:
                    # 清理标题
                    title = re.sub(r'<[^>]+>', '', title_html).strip()

                    # 构建完整URL
                    url = href if href.startswith('http') else f'https://news.gxnu.edu.cn{href}'

                    # 使用基类的标题验证
                    if self.is_valid_title(title):
                        doc = {
                            'title': self.clean_text(title)[:100],
                            'url': url,
                            'category': '学校官网',
                            'doc_type': '新闻公告',
                            'source': 'gxnu'
                        }
                        documents.append(doc)

                        if len(documents) >= max_pages:
                            break

                # 速率限制：每次请求间隔3-5秒
                time.sleep(3 + (hash(notice_url) % 3))

            except Exception as e:
                print(f"爬取 {notice_url} 失败: {str(e)}")
                continue

        return documents

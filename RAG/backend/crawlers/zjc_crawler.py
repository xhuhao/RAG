"""
文件：zjc_crawler.py
功能：招生就业处爬虫
说明：爬取招生就业处的招生政策、就业信息等
根据web-scraping技能最佳实践实现
"""

import re
import time
from crawlers.base_crawler import BaseCrawler

class ZJCCrawler(BaseCrawler):
    """
    招生就业处爬虫

    爬取招生就业处的招生政策、就业信息等
    """

    def __init__(self):
        super().__init__(
            base_url="http://gxnu.bysjy.com.cn",
            source_name="招生就业处"
        )

    def crawl(self, max_pages=5):
        """
        爬取招生就业处的通知公告

        参数：
            max_pages: 最大爬取页数

        返回：
            文档列表
        """
        documents = []

        # 招生就业处页面URL
        notice_urls = [
            "http://gxnu.bysjy.com.cn/",  # 招生就业处独立网站
            "https://www.gxnu.edu.cn/1357/list.htm",
            "https://www.gxnu.edu.cn/1442/list.htm",  # 学校新闻（包含招生就业相关内容）
        ]

        for notice_url in notice_urls:
            try:
                # 获取页面HTML
                response = self.session.get(notice_url, timeout=30)
                response.encoding = response.apparent_encoding
                html = response.text

                # 使用正则表达式提取链接和标题
                pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
                matches = re.findall(pattern, html, re.DOTALL)

                for href, title_html in matches[:max_pages * 3]:
                    # 清理标题
                    title = re.sub(r'<[^>]+>', '', title_html).strip()

                    # 构建完整URL
                    if href.startswith('http'):
                        url = href
                    elif notice_url.startswith('http://gxnu.bysjy.com.cn'):
                        url = f'http://gxnu.bysjy.com.cn{href}'
                    else:
                        url = f'https://www.gxnu.edu.cn{href}'

                    # 使用基类的标题验证
                    if self.is_valid_title(title):
                        doc = {
                            'title': self.clean_text(title)[:100],
                            'url': url,
                            'category': '招生就业处',
                            'doc_type': '招生就业',
                            'source': 'zjc'
                        }
                        documents.append(doc)

                        if len(documents) >= max_pages:
                            break

                # 速率限制
                time.sleep(3 + (hash(notice_url) % 3))

            except Exception as e:
                print(f"爬取 {notice_url} 失败: {str(e)}")
                continue

        return documents

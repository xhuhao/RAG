"""
文件：jwc_crawler.py
功能：教务处爬虫
说明：爬取教务处的通知公告、考试安排等
根据web-scraping技能最佳实践实现
"""

import re
import time
from crawlers.base_crawler import BaseCrawler

class JWCCrawler(BaseCrawler):
    """
    教务处爬虫

    爬取教务处的通知公告、考试安排等
    """

    def __init__(self):
        super().__init__(
            base_url="https://www.gxnu.edu.cn",
            source_name="教务处"
        )

    def crawl(self, max_pages=5):
        """
        爬取教务处的通知公告

        参数：
            max_pages: 最大爬取页数

        返回：
            文档列表
        """
        documents = []

        # 教务处页面URL
        notice_urls = [
            "https://www.gxnu.edu.cn/1432/list.htm",
            "https://www.gxnu.edu.cn/1433/list.htm",
            "https://www.gxnu.edu.cn/1434/list.htm",
            "https://www.gxnu.edu.cn/1435/list.htm",
            "https://www.gxnu.edu.cn/1441/list.htm",  # 学校通知
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
                    url = href if href.startswith('http') else f'https://www.gxnu.edu.cn{href}'

                    # 使用基类的标题验证
                    if self.is_valid_title(title):
                        doc = {
                            'title': self.clean_text(title)[:100],
                            'url': url,
                            'category': '教务处',
                            'doc_type': '通知公告',
                            'source': 'jwc'
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

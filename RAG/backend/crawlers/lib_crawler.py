"""
文件：lib_crawler.py
功能：图书馆爬虫
说明：爬取图书馆的借阅规则、开馆时间等
根据web-scraping技能最佳实践实现
安全爬取配置：小批量 + 长间隔
"""

import re
import time
import random
from crawlers.base_crawler import BaseCrawler

class LIBCrawler(BaseCrawler):
    """
    图书馆爬虫

    爬取图书馆的借阅规则、开馆时间等
    安全配置：每次最多15页，间隔5-10秒
    """

    def __init__(self):
        super().__init__(
            base_url="http://www.library.gxnu.edu.cn",
            source_name="图书馆"
        )

    def crawl(self, max_pages=5):
        """
        爬取图书馆的规章制度

        参数：
            max_pages: 最大爬取页数（建议不超过15）

        返回：
            文档列表
        """
        documents = []

        # 安全配置
        safe_max_pages = min(max_pages, 15)  # 限制最多15页

        # 图书馆页面URL
        notice_urls = [
            "http://www.library.gxnu.edu.cn/",
        ]

        for notice_url in notice_urls:
            try:
                # 获取页面HTML
                response = self.session.get(notice_url, timeout=30)
                response.encoding = response.apparent_encoding
                html = response.text

                # 提取所有链接
                pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
                matches = re.findall(pattern, html, re.DOTALL)

                # 过滤中文链接
                for href, title_html in matches[:safe_max_pages * 3]:
                    title = re.sub(r'<[^>]+>', '', title_html).strip()

                    # 构建完整URL
                    url = href if href.startswith('http') else f'http://www.library.gxnu.edu.cn{href}'

                    # 使用基类的标题验证
                    if self.is_valid_title(title):
                        doc = {
                            'title': self.clean_text(title)[:100],
                            'url': url,
                            'category': '图书馆',
                            'doc_type': '规章制度',
                            'source': 'lib'
                        }
                        documents.append(doc)

                        if len(documents) >= safe_max_pages:
                            break

                # 安全间隔：5-10秒
                delay = 5 + random.randint(0, 5)
                print(f"安全间隔：等待 {delay} 秒...")
                time.sleep(delay)

            except Exception as e:
                print(f"爬取 {notice_url} 失败: {str(e)}")
                continue

        return documents

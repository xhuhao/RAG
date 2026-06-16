"""
文件：yjs_crawler.py
功能：研究生院爬虫
说明：爬取研究生院的招生信息、培养方案等
根据web-scraping技能最佳实践实现
"""

import re
import time
from crawlers.base_crawler import BaseCrawler

class YJSCrawler(BaseCrawler):
    """
    研究生院爬虫

    爬取研究生院的招生信息、培养方案等
    """

    def __init__(self):
        super().__init__(
            base_url="https://www.gxnu.edu.cn",
            source_name="研究生院"
        )

    def crawl(self, max_pages=5):
        """
        爬取研究生院的招生信息

        参数：
            max_pages: 最大爬取页数

        返回：
            文档列表
        """
        documents = []

        # 研究生院页面URL
        notice_urls = [
            "https://www.gxnu.edu.cn/1385/list.htm",
            "https://www.gxnu.edu.cn/1442/list.htm",  # 学校新闻（包含研究生相关内容）
            "http://www.yz.gxnu.edu.cn/",               # 研究生招生
            "http://www.cjy.gxnu.edu.cn/2399/list.htm",  # 成人教育
            "http://gxttc.gxnu.edu.cn/fwxz_10229/list.htm",  # 师范大学
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
                            'category': '研究生院',
                            'doc_type': '招生信息',
                            'source': 'yjs'
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

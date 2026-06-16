"""
文件：xgc_crawler.py
功能：学生工作处爬虫
说明：爬取学生工作处的奖助学金、宿舍管理等
根据web-scraping技能最佳实践实现
"""

import re
import time
from crawlers.base_crawler import BaseCrawler

class XGCCrawler(BaseCrawler):
    """
    学生工作处爬虫

    爬取学生工作处的奖助学金、宿舍管理等
    """

    def __init__(self):
        super().__init__(
            base_url="https://xgb.gxnu.edu.cn",
            source_name="学生工作处"
        )

    def crawl(self, max_pages=5):
        """
        爬取学生工作处的通知公告

        参数：
            max_pages: 最大爬取页数

        返回：
            文档列表
        """
        documents = []

        # 学生工作处页面URL
        notice_urls = [
            "https://xgb.gxnu.edu.cn/main.htm",  # 学生工作部主页
            "https://xgb.gxnu.edu.cn/1053/list.htm",  # 通知公告
            "https://xgb.gxnu.edu.cn/1075/list.htm",  # 思想教育
            "https://xgb.gxnu.edu.cn/1072/list.htm",  # 日常管理
            "https://xgb.gxnu.edu.cn/1074/list.htm",  # 资助管理
            "https://xgb.gxnu.edu.cn/1073/list.htm",  # 心理健康
            "https://xgb.gxnu.edu.cn/1071/list.htm",  # 学生社区
            "https://xgb.gxnu.edu.cn/1070/list.htm",  # 就业管理
            "https://xgb.gxnu.edu.cn/1069/list.htm",  # 国防教育
        ]

        for notice_url in notice_urls:
            try:
                # 获取页面HTML
                response = self.session.get(notice_url, timeout=30)
                response.encoding = response.apparent_encoding
                html = response.text

                # 使用正则表达式提取page.htm链接
                pattern = r'<a[^>]+href=["\']([^"\']*page\.htm)["\'][^>]*>(.*?)</a>'
                matches = re.findall(pattern, html, re.DOTALL)

                for href, title_html in matches[:max_pages * 3]:
                    # 清理标题
                    title = re.sub(r'<[^>]+>', '', title_html).strip()

                    # 构建完整URL
                    url = href if href.startswith('http') else f'https://xgb.gxnu.edu.cn{href}'

                    # 使用基类的标题验证
                    if self.is_valid_title(title):
                        # 确定文档类型
                        doc_type = '通知公告'
                        if '1075' in notice_url:
                            doc_type = '思想教育'
                        elif '1072' in notice_url:
                            doc_type = '日常管理'
                        elif '1074' in notice_url:
                            doc_type = '资助管理'
                        elif '1073' in notice_url:
                            doc_type = '心理健康'
                        elif '1071' in notice_url:
                            doc_type = '学生社区'
                        elif '1070' in notice_url:
                            doc_type = '就业管理'
                        elif '1069' in notice_url:
                            doc_type = '国防教育'

                        doc = {
                            'title': self.clean_text(title)[:100],
                            'url': url,
                            'category': '学生工作处',
                            'doc_type': doc_type,
                            'source': 'xgc'
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

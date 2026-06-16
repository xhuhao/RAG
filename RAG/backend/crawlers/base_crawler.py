"""
文件：base_crawler.py
功能：爬虫基类
说明：提供通用的爬虫功能，所有具体爬虫继承此类
根据web-scraping技能最佳实践实现
"""

import os
import re
import time
import hashlib
import random
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse

# 尝试导入BeautifulSoup
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("警告：BeautifulSoup未安装，将使用简单的HTML解析")

# User-Agent列表，轮换使用避免被封禁
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

class BaseCrawler:
    """
    爬虫基类

    提供通用的网页爬取、PDF下载、元数据提取等功能
    遵循web-scraping技能的最佳实践
    """

    def __init__(self, base_url, source_name):
        """
        初始化爬虫

        参数：
            base_url: 基础URL
            source_name: 数据来源名称
        """
        self.base_url = base_url
        self.source_name = source_name
        self.session = requests.Session()
        self._rotate_user_agent()

    def _rotate_user_agent(self):
        """轮换User-Agent"""
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS)
        })

    def fetch_page(self, url, timeout=30, max_retries=3):
        """
        获取页面内容（带重试逻辑）

        参数：
            url: 页面URL
            timeout: 超时时间
            max_retries: 最大重试次数

        返回：
            BeautifulSoup对象或原始HTML
        """
        for attempt in range(max_retries):
            try:
                # 轮换User-Agent
                self._rotate_user_agent()

                response = self.session.get(url, timeout=timeout)
                response.encoding = response.apparent_encoding

                # 检查响应状态
                if response.status_code == 200:
                    if HAS_BS4:
                        return BeautifulSoup(response.text, 'html.parser')
                    else:
                        return response.text
                elif response.status_code == 403:
                    print(f"被拒绝访问 {url}，等待后重试...")
                    time.sleep(5 * (attempt + 1))
                elif response.status_code == 429:
                    print(f"请求过于频繁 {url}，等待后重试...")
                    time.sleep(10 * (attempt + 1))
                else:
                    print(f"获取页面失败 {url}: HTTP {response.status_code}")
                    return None

            except requests.exceptions.Timeout:
                print(f"请求超时 {url}，重试 {attempt + 1}/{max_retries}")
                time.sleep(3 * (attempt + 1))
            except requests.exceptions.ConnectionError:
                print(f"连接错误 {url}，重试 {attempt + 1}/{max_retries}")
                time.sleep(5 * (attempt + 1))
            except Exception as e:
                print(f"获取页面失败 {url}: {str(e)}")
                return None

        print(f"获取页面失败 {url}: 已达最大重试次数")
        return None

    def extract_links(self, soup, pattern=None):
        """
        提取页面中的链接

        参数：
            soup: BeautifulSoup对象或HTML字符串
            pattern: URL匹配正则表达式

        返回：
            链接列表
        """
        links = []

        if HAS_BS4 and hasattr(soup, 'find_all'):
            # 使用BeautifulSoup解析
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(self.base_url, href)

                if pattern:
                    if re.search(pattern, full_url):
                        links.append({
                            'url': full_url,
                            'title': a_tag.get_text(strip=True)
                        })
                else:
                    links.append({
                        'url': full_url,
                        'title': a_tag.get_text(strip=True)
                    })
        else:
            # 使用正则表达式解析
            html = soup if isinstance(soup, str) else str(soup)
            a_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
            for match in re.finditer(a_pattern, html, re.DOTALL):
                href = match.group(1)
                title = re.sub(r'<[^>]+>', '', match.group(2)).strip()
                full_url = urljoin(self.base_url, href)

                if pattern:
                    if re.search(pattern, full_url):
                        links.append({
                            'url': full_url,
                            'title': title
                        })
                else:
                    links.append({
                        'url': full_url,
                        'title': title
                    })

        return links

    def extract_pdf_links(self, soup):
        """
        提取PDF链接

        参数：
            soup: BeautifulSoup对象或HTML字符串

        返回：
            PDF链接列表
        """
        pdf_links = []

        if HAS_BS4 and hasattr(soup, 'find_all'):
            # 使用BeautifulSoup解析
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if href.lower().endswith('.pdf'):
                    full_url = urljoin(self.base_url, href)
                    pdf_links.append({
                        'url': full_url,
                        'title': a_tag.get_text(strip=True)
                    })
        else:
            # 使用正则表达式解析
            html = soup if isinstance(soup, str) else str(soup)
            a_pattern = r'<a[^>]+href=["\']([^"\']+\.pdf)["\'][^>]*>(.*?)</a>'
            for match in re.finditer(a_pattern, html, re.DOTALL | re.IGNORECASE):
                href = match.group(1)
                title = re.sub(r'<[^>]+>', '', match.group(2)).strip()
                full_url = urljoin(self.base_url, href)
                pdf_links.append({
                    'url': full_url,
                    'title': title
                })

        return pdf_links

    def download_pdf(self, url, save_dir, filename=None, max_retries=3):
        """
        下载PDF文件（带重试逻辑）

        参数：
            url: PDF文件URL
            save_dir: 保存目录
            filename: 文件名（可选）
            max_retries: 最大重试次数

        返回：
            保存的文件路径
        """
        # 确保保存目录存在
        os.makedirs(save_dir, exist_ok=True)

        # 生成文件名
        if not filename:
            # 从URL提取文件名
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)

            # 如果文件名为空，生成一个
            if not filename or not filename.endswith('.pdf'):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                hash_str = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"{self.source_name}_{timestamp}_{hash_str}.pdf"

        # 确保文件名以.pdf结尾
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'

        # 清理文件名中的特殊字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

        filepath = os.path.join(save_dir, filename)

        # 下载文件（带重试）
        for attempt in range(max_retries):
            try:
                # 轮换User-Agent
                self._rotate_user_agent()

                response = self.session.get(url, timeout=60)
                response.raise_for_status()

                # 保存文件
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                print(f"下载成功: {filename}")
                return filepath

            except requests.exceptions.Timeout:
                print(f"下载超时 {url}，重试 {attempt + 1}/{max_retries}")
                time.sleep(3 * (attempt + 1))
            except requests.exceptions.ConnectionError:
                print(f"连接错误 {url}，重试 {attempt + 1}/{max_retries}")
                time.sleep(5 * (attempt + 1))
            except Exception as e:
                print(f"下载失败 {url}: {str(e)}")
                return None

        print(f"下载失败 {url}: 已达最大重试次数")
        return None

    def clean_text(self, text):
        """
        清理文本内容

        参数：
            text: 原始文本

        返回：
            清理后的文本
        """
        if not text:
            return ""

        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)

        # 移除特殊字符
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        return text.strip()

    def is_valid_title(self, title):
        """
        验证标题是否有效

        参数：
            title: 标题

        返回：
            是否有效
        """
        if not title:
            return False

        # 标题长度检查
        if len(title) < 5 or len(title) > 200:
            return False

        # 包含中文字符
        has_chinese = any('一' <= c <= '鿿' for c in title)

        # 不是导航链接
        skip_words = ['English', '首页', '导航', '登录', '注册', '更多', '返回', '上一页', '下一页']
        is_skip = any(word in title for word in skip_words)

        return has_chinese and not is_skip

    def crawl(self, max_pages=5):
        """
        爬取数据（子类实现）

        参数：
            max_pages: 最大爬取页数

        返回：
            文档列表
        """
        raise NotImplementedError("子类必须实现crawl方法")

    def get_document_list(self, max_pages=5):
        """
        获取文档列表

        参数：
            max_pages: 最大爬取页数

        返回：
            文档列表
        """
        try:
            documents = self.crawl(max_pages)
            print(f"从 {self.source_name} 获取到 {len(documents)} 篇文档")
            return documents
        except Exception as e:
            print(f"爬取 {self.source_name} 失败: {str(e)}")
            return []

"""
文件：sync.py
功能：同步相关API
说明：触发数据同步操作

接口列表：
- POST /api/sync/all      同步所有数据来源
- POST /api/sync/:source  同步指定数据来源
- POST /api/sync/download-pdfs  下载PDF文件
"""

import os
import sys
from flask import Blueprint, request, jsonify

# 添加backend目录到Python路径
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.sync_service import sync_from_crawler, sync_all, download_pdfs_from_website

# 创建同步蓝图
sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/api/sync/all', methods=['POST'])
def sync_all_sources():
    """
    同步所有数据来源

    请求参数：
        max_pages (int): 每个来源的最大爬取页数（默认5）

    返回：
        success: {
            'code': 200,
            'message': '同步完成',
            'data': {
                'total_success': 60,
                'total_failed': 0,
                'details': {...}
            }
        }
    """
    # 获取请求参数
    data = request.get_json() or {}
    max_pages = data.get('max_pages', 5)

    try:
        result = sync_all(max_pages)

        return jsonify({
            'code': 200,
            'message': '同步完成',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'同步失败：{str(e)}'})

@sync_bp.route('/api/sync/<source>', methods=['POST'])
def sync_single_source(source):
    """
    同步指定数据来源

    参数：
        source: 数据来源（gxnu/jwc/yjs/lib/xgc/zjc）

    请求参数：
        max_pages (int): 最大爬取页数（默认5）

    返回：
        success: {
            'code': 200,
            'message': '同步完成',
            'data': {
                'success': 10,
                'failed': 0
            }
        }
    """
    # 获取请求参数
    data = request.get_json() or {}
    max_pages = data.get('max_pages', 5)

    try:
        result = sync_from_crawler(source, max_pages)

        return jsonify({
            'code': 200,
            'message': '同步完成',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'同步失败：{str(e)}'})

@sync_bp.route('/api/sync/download-pdfs', methods=['POST'])
def download_pdfs():
    """
    从网站下载PDF文件

    请求参数：
        url (str): 网站URL（默认新闻网）
        max_pdfs (int): 最大下载数量（默认10）

    返回：
        success: {
            'code': 200,
            'message': '下载完成',
            'data': {
                'success': 5,
                'failed': 0
            }
        }
    """
    # 获取请求参数
    data = request.get_json() or {}
    url = data.get('url', 'https://news.gxnu.edu.cn/')
    max_pdfs = data.get('max_pdfs', 10)

    try:
        result = download_pdfs_from_website(url, max_pdfs)

        return jsonify({
            'code': 200,
            'message': '下载完成',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'下载失败：{str(e)}'})

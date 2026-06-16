"""
文件：document.py
功能：文档管理相关API
说明：处理文档的上传、查询、更新、删除等操作

接口列表：
- GET    /api/documents      获取文档列表
- POST   /api/documents      上传文档
- GET    /api/documents/:id  获取文档详情
- PUT    /api/documents/:id  更新文档
- DELETE /api/documents/:id  删除文档
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.document_service import (
    process_document_upload,
    get_document_list,
    get_document_by_id,
    update_document_record,
    delete_document_record
)

# 创建文档蓝图
document_bp = Blueprint('document', __name__)

@document_bp.route('/api/documents', methods=['GET'])
def list_documents():
    """
    获取文档列表接口

    请求参数：
        page (int): 页码（默认1）
        per_page (int): 每页数量（默认10）
        keyword (str): 搜索关键词

    返回：
        success: {'code': 200, 'data': {'items': [...], 'total': 100, ...}}
    """
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', None)

    try:
        result = get_document_list(page, per_page, keyword)
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@document_bp.route('/api/documents', methods=['POST'])
def upload_document():
    """
    上传文档接口

    请求参数：
        file (file): PDF文件
        title (str): 文档标题
        category (str): 分类
        doc_type (str): 文档类型
        url (str): 文档URL

    返回：
        success: {'code': 200, 'message': '上传成功', 'data': {'document': {...}}}
        failure: {'code': 400, 'message': '错误信息'}
    """
    # 获取表单数据
    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    doc_type = request.form.get('doc_type', '').strip()
    url = request.form.get('url', '').strip()

    # 参数验证
    if not title:
        return jsonify({'code': 400, 'message': '文档标题不能为空'})

    # 获取上传的文件
    file = request.files.get('file')

    # 验证文件
    if not file or not file.filename:
        return jsonify({'code': 400, 'message': '请上传PDF文件'})

    # 验证文件类型
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'code': 400, 'message': '只支持PDF文件'})

    try:
        # 获取上传目录
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

        # 处理文档上传（保存、提取、分块、向量化）
        document = process_document_upload(file, title, category, doc_type, url, upload_folder)

        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {
                'document': document.to_dict()
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'上传失败：{str(e)}'})

@document_bp.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """
    获取文档详情接口

    参数：
        doc_id: 文档ID

    返回：
        success: {'code': 200, 'data': {'document': {...}}}
        failure: {'code': 404, 'message': '文档不存在'}
    """
    document = get_document_by_id(doc_id)

    if not document:
        return jsonify({'code': 404, 'message': '文档不存在'})

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'document': document.to_dict()
        }
    })

@document_bp.route('/api/documents/<int:doc_id>', methods=['PUT'])
def update_document(doc_id):
    """
    更新文档接口

    参数：
        doc_id: 文档ID

    请求参数：
        title (str): 文档标题
        category (str): 分类
        doc_type (str): 文档类型
        url (str): 文档URL

    返回：
        success: {'code': 200, 'message': '更新成功', 'data': {'document': {...}}}
        failure: {'code': 400, 'message': '错误信息'}
    """
    # 获取请求数据
    data = request.get_json()
    title = data.get('title')
    category = data.get('category')
    doc_type = data.get('doc_type')
    url = data.get('url')

    try:
        document = update_document_record(doc_id, title, category, doc_type, url)

        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'document': document.to_dict()
            }
        })
    except Exception as e:
        return jsonify({'code': 400, 'message': str(e)})

@document_bp.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """
    删除文档接口（标记为归档）

    参数：
        doc_id: 文档ID

    返回：
        success: {'code': 200, 'message': '删除成功'}
        failure: {'code': 400, 'message': '错误信息'}
    """
    try:
        delete_document_record(doc_id)

        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        return jsonify({'code': 400, 'message': str(e)})

"""
文件：evaluate_500.py
功能：使用RAGas评估500个测试问题
说明：全面评估RAG系统质量
"""

import sys
import os
import time
import requests
import json
from datasets import Dataset

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# API地址
API_URL = "http://localhost:5000/api/chat/ask"

# 500个测试问题
TEST_CASES = [
    # 一、学校概况（30个）
    {"question": "广西师范大学的校训是什么？", "ground_truth": "广西师范大学的校训是尊师重道，敬业乐群。", "category": "学校概况"},
    {"question": "广西师范大学有哪些校区？", "ground_truth": "广西师范大学有王城、育才、雁山3个校区。", "category": "学校概况"},
    {"question": "广西师范大学创建于哪一年？", "ground_truth": "广西师范大学创建于1932年。", "category": "学校概况"},
    {"question": "广西师范大学的校园面积是多少？", "ground_truth": "广西师范大学校园面积近4000亩。", "category": "学校概况"},
    {"question": "广西师范大学有多少学生？", "ground_truth": "广西师范大学全日制学生39000余人，各类学生共66000余人。", "category": "学校概况"},
    {"question": "广西师范大学有多少教职工？", "ground_truth": "广西师范大学各类教职工5000余人。", "category": "学校概况"},
    {"question": "广西师范大学的校歌是什么？", "ground_truth": "广西师范大学的校歌是《育才之歌》。", "category": "学校概况"},
    {"question": "广西师范大学的精神是什么？", "ground_truth": "广西师范大学精神是独秀精神。", "category": "学校概况"},
    {"question": "广西师范大学的校徽是什么？", "ground_truth": "广西师范大学校徽包含独秀峰元素。", "category": "学校概况"},
    {"question": "广西师范大学的办学定位是什么？", "ground_truth": "广西师范大学是教育部与广西壮族自治区人民政府共建高校，广西重点建设的国内一流大学。", "category": "学校概况"},
    {"question": "广西师范大学有多少个博士学位授权点？", "ground_truth": "广西师范大学有博士学位授权点13个。", "category": "学校概况"},
    {"question": "广西师范大学有多少个硕士学位授权点？", "ground_truth": "广西师范大学有硕士学位授权点56个。", "category": "学校概况"},
    {"question": "广西师范大学有哪些学科进入ESI全球前1%？", "ground_truth": "化学、工程学、计算机科学、材料科学、物理学5个学科进入ESI全球前1%。", "category": "学校概况"},
    {"question": "广西师范大学有多少个本科专业？", "ground_truth": "广西师范大学有全日制普通本科专业77个。", "category": "学校概况"},
    {"question": "广西师范大学有多少个博士后科研流动站？", "ground_truth": "广西师范大学有博士后科研流动站7个。", "category": "学校概况"},
    {"question": "广西师范大学的前身是什么？", "ground_truth": "广西师范大学的前身是广西省立师范专科学校。", "category": "学校概况"},
    {"question": "广西师范大学何时更名为广西师范大学？", "ground_truth": "1983年更名为广西师范大学。", "category": "学校概况"},
    {"question": "广西师范大学培养了多少人才？", "ground_truth": "建校以来培养了53万多名教师和其他专业人才。", "category": "学校概况"},
    {"question": "广西师范大学有哪些国家级人才项目？", "ground_truth": "学校入选省部级以上高层次人才项目267人次，其中国家级人才项目31人次。", "category": "学校概况"},
    {"question": "广西师范大学有哪些荣誉称号？", "ground_truth": "学校被评为全国先进基层党组织、全国教育系统先进集体、全国文明校园等。", "category": "学校概况"},
    {"question": "广西师范大学有哪些国家级实验教学示范中心？", "ground_truth": "学校有3个国家级实验教学示范中心。", "category": "学校概况"},
    {"question": "广西师范大学有多少个国家级一流本科专业建设点？", "ground_truth": "学校有国家级一流本科专业建设点23个。", "category": "学校概况"},
    {"question": "广西师范大学有多少门国家一流课程？", "ground_truth": "学校有国家一流课程21门。", "category": "学校概况"},
    {"question": "广西师范大学获得过多少项国家级教学成果奖？", "ground_truth": "学校获得国家级教学成果奖16项。", "category": "学校概况"},
    {"question": "广西师范大学的教师教育有什么特色？", "ground_truth": "学校是广西教师教育的摇篮，形成了涵盖各级各类师资培养的全覆盖体系。", "category": "学校概况"},
    {"question": "广西师范大学出版社有什么成就？", "ground_truth": "广西师范大学出版社集团是中国首家地方大学出版社集团，多次获得国家级图书大奖。", "category": "学校概况"},
    {"question": "广西师范大学与多少所高校建立了合作交流关系？", "ground_truth": "学校已与世界350多所高校及机构建立了合作交流关系。", "category": "学校概况"},
    {"question": "广西师范大学有几所孔子学院？", "ground_truth": "学校在海外建有3所孔子学院。", "category": "学校概况"},
    {"question": "广西师范大学的王城校区在哪里？", "ground_truth": "王城校区位于广西桂林市秀峰区王城1号。", "category": "学校概况"},
    {"question": "广西师范大学的育才校区在哪里？", "ground_truth": "育才校区位于广西桂林市七星区育才路15号。", "category": "学校概况"},

    # 二、图书馆（50个）
    {"question": "图书馆的借阅规则是什么？", "ground_truth": "读者凭校园一卡通借阅图书，每次最多借10本，借期30天。", "category": "图书馆"},
    {"question": "图书馆的开放时间是什么？", "ground_truth": "图书馆的开放时间为7:30—22:30。", "category": "图书馆"},
    {"question": "如何办理借阅手续？", "ground_truth": "使用自助借还机或至咨询台办理，凭校园一卡通借阅。", "category": "图书馆"},
    {"question": "图书馆有哪些数字资源？", "ground_truth": "图书馆有274万余册电子图书和117个数据库。", "category": "图书馆"},
    {"question": "如何预约图书馆座位？", "ground_truth": "通过微信公众号或网页http://ic.gxnu.edu.cn/预约。", "category": "图书馆"},
    {"question": "图书馆的联系方式是什么？", "ground_truth": "电话0773-8283061、0773-5846415，QQ咨询958057199。", "category": "图书馆"},
    {"question": "如何校外访问图书馆资源？", "ground_truth": "通过VPN或CARSI访问，VPN地址https://webvpn.gxnu.edu.cn/。", "category": "图书馆"},
    {"question": "图书馆的借阅册数和期限是多少？", "ground_truth": "不同类型读者借阅数量不同，具体以读者办证管理规定为准。", "category": "图书馆"},
    {"question": "图书馆有哪些分馆？", "ground_truth": "图书馆有王城、育才、雁山三个校区的分馆。", "category": "图书馆"},
    {"question": "如何续借图书？", "ground_truth": "图书到期前7天内可通过图书馆官网或微信公众号办理续借。", "category": "图书馆"},
    {"question": "图书馆的馆藏分布是怎样的？", "ground_truth": "图书馆各校区有不同的馆藏分布，具体见馆藏分布页面。", "category": "图书馆"},
    {"question": "图书馆有哪些自助设备？", "ground_truth": "图书馆有自助借还书柜、自助文印、自助检索机等设备。", "category": "图书馆"},
    {"question": "图书馆的研修间如何预约？", "ground_truth": "通过微信公众号或网页预约研修间。", "category": "图书馆"},
    {"question": "图书馆的朗读亭在哪里？", "ground_truth": "图书馆设有朗读亭，具体位置见图书馆平面图。", "category": "图书馆"},
    {"question": "图书馆的图书杀菌机在哪里？", "ground_truth": "图书馆设有图书杀菌机，具体位置见图书馆平面图。", "category": "图书馆"},
    {"question": "图书馆的数字阅览机在哪里？", "ground_truth": "图书馆设有数字阅览机，具体位置见图书馆平面图。", "category": "图书馆"},
    {"question": "图书馆的自助存包柜在哪里？", "ground_truth": "图书馆设有自助存包柜，具体位置见图书馆平面图。", "category": "图书馆"},
    {"question": "图书馆的联系方式有哪些？", "ground_truth": "电话0773-8283061、QQ咨询958057199、邮箱958057199@qq.com。", "category": "图书馆"},
    {"question": "图书馆的馆长信箱是什么？", "ground_truth": "图书馆馆长信箱是library@mailbox.gxnu.edu.cn。", "category": "图书馆"},
    {"question": "图书馆的历史沿革是什么？", "ground_truth": "图书馆有悠久的历史，具体见历史沿革页面。", "category": "图书馆"},
    {"question": "图书馆的本馆简介是什么？", "ground_truth": "图书馆是学校的重要学术支撑机构，具体见本馆简介。", "category": "图书馆"},
    {"question": "图书馆的桂学博物馆是什么？", "question": "图书馆的桂学博物馆是什么？", "ground_truth": "桂学博物馆是图书馆的重要组成部分，展示桂学文化。", "category": "图书馆"},
    {"question": "图书馆的现任领导是谁？", "ground_truth": "图书馆现任领导信息见现任领导页面。", "category": "图书馆"},
    {"question": "图书馆的组织机构是什么？", "ground_truth": "图书馆设有多个部门，具体见组织机构页面。", "category": "图书馆"},
    {"question": "图书馆的馆舍风貌如何？", "ground_truth": "图书馆馆舍风貌优美，具体见馆舍风貌页面。", "category": "图书馆"},
    {"question": "图书馆的雁山馆平面图在哪里？", "ground_truth": "雁山馆平面图可在图书馆官网查看。", "category": "图书馆"},
    {"question": "图书馆的读者咨询如何联系？", "ground_truth": "读者可通过QQ、电话、邮箱等方式咨询。", "category": "图书馆"},
    {"question": "图书馆的逾期与赔偿规定是什么？", "ground_truth": "图书到期后有7天宽限期，超过宽限期每天罚款0.1元。", "category": "图书馆"},
    {"question": "图书馆的异地借还是什么？", "ground_truth": "三校区实行通借通还服务。", "category": "图书馆"},
    {"question": "图书馆的预约续借如何操作？", "ground_truth": "通过图书馆官网或微信公众号办理预约续借。", "category": "图书馆"},
    {"question": "图书馆的24小时借还书柜在哪里？", "ground_truth": "图书馆设有24小时借还书柜，具体位置见图书馆平面图。", "category": "图书馆"},
    {"question": "图书馆的24小时还书机在哪里？", "ground_truth": "图书馆设有24小时还书机，具体位置见图书馆平面图。", "category": "图书馆"},
    {"question": "图书馆的参观预约如何办理？", "ground_truth": "可通过图书馆官网办理参观预约。", "category": "图书馆"},
    {"question": "图书馆的入馆须知是什么？", "ground_truth": "入馆须知详见图书馆官网。", "category": "图书馆"},
    {"question": "图书馆的借阅办理流程是什么？", "ground_truth": "凭校园一卡通在自助借还机或咨询台办理。", "category": "图书馆"},
    {"question": "图书馆的借阅制度是什么？", "ground_truth": "借阅制度详见图书馆官网。", "category": "图书馆"},
    {"question": "图书馆的开放时间是几点到几点？", "ground_truth": "图书馆开放时间为7:30—22:30。", "category": "图书馆"},
    {"question": "图书馆的数字资源有哪些？", "ground_truth": "图书馆有274万余册电子图书和117个数据库。", "category": "图书馆"},
    {"question": "图书馆的数字资源与服务推介手册在哪里？", "ground_truth": "数字资源与服务推介手册可在图书馆官网下载。", "category": "图书馆"},
    {"question": "图书馆的校外访问指南是什么？", "ground_truth": "校外访问指南详见图书馆官网。", "category": "图书馆"},
    {"question": "图书馆的校外访问链接是什么？", "ground_truth": "校外访问链接详见图书馆官网。", "category": "图书馆"},
    {"question": "图书馆的联系我们是什么？", "ground_truth": "联系电话0773-8283061、0773-5846415。", "category": "图书馆"},
    {"question": "图书馆的自习室在哪里？", "ground_truth": "图书馆各校区设有自习室，具体位置见图书馆平面图。", "category": "图书馆"},
    {"question": "图书馆的电子资源如何使用？", "ground_truth": "电子资源可在校园网内直接访问，校外通过VPN访问。", "category": "图书馆"},
    {"question": "图书馆的数据库有哪些？", "ground_truth": "图书馆有117个数据库，包括CNKI、维普等。", "category": "图书馆"},
    {"question": "图书馆的借阅证如何办理？", "ground_truth": "凭校园一卡通即可借阅，无需单独办理借阅证。", "category": "图书馆"},
    {"question": "图书馆的挂失如何办理？", "ground_truth": "校园一卡通遗失应立即办理挂失手续。", "category": "图书馆"},
    {"question": "图书馆的赔偿标准是什么？", "ground_truth": "图书污损、遗失等按相关规定赔偿。", "category": "图书馆"},
    {"question": "图书馆的借阅权限如何开通？", "ground_truth": "凭校园一卡通即可开通借阅权限。", "category": "图书馆"},

    # 三、院系信息（100个）
    {"question": "文学院有哪些专业？", "ground_truth": "文学院有汉语言文学、秘书学等专业。", "category": "院系信息"},
    {"question": "历史文化与旅游学院有哪些专业？", "ground_truth": "历史文化与旅游学院有历史学、旅游管理等专业。", "category": "院系信息"},
    {"question": "马克思主义学院有哪些专业？", "ground_truth": "马克思主义学院有思想政治教育等专业。", "category": "院系信息"},
    {"question": "法学院有哪些专业？", "ground_truth": "法学院有法学等专业。", "category": "院系信息"},
    {"question": "政治与公共管理学院有哪些专业？", "ground_truth": "政治与公共管理学院有政治学与行政学、社会工作等专业。", "category": "院系信息"},
    {"question": "经济管理学院有哪些专业？", "ground_truth": "经济管理学院有经济学、工商管理等专业。", "category": "院系信息"},
    {"question": "教育学部有哪些专业？", "ground_truth": "教育学部有教育学、学前教育等专业。", "category": "院系信息"},
    {"question": "外国语学院有哪些专业？", "ground_truth": "外国语学院有英语、日语等专业。", "category": "院系信息"},
    {"question": "美术学院有哪些专业？", "ground_truth": "美术学院有美术学、设计学等专业。", "category": "院系信息"},
    {"question": "音乐学院有哪些专业？", "ground_truth": "音乐学院有音乐学、舞蹈学等专业。", "category": "院系信息"},
    {"question": "数学与统计学院有哪些专业？", "ground_truth": "数学与统计学院有数学与应用数学、统计学等专业。", "category": "院系信息"},
    {"question": "物理科学与技术学院有哪些专业？", "ground_truth": "物理科学与技术学院有物理学、电子信息工程等专业。", "category": "院系信息"},
    {"question": "化学与药学学院有哪些专业？", "ground_truth": "化学与药学学院有化学、制药工程等专业。", "category": "院系信息"},
    {"question": "生命科学学院有哪些专业？", "ground_truth": "生命科学学院有生物科学、生物技术等专业。", "category": "院系信息"},
    {"question": "环境与资源学院有哪些专业？", "ground_truth": "环境与资源学院有环境科学、地理科学等专业。", "category": "院系信息"},
    {"question": "计算机科学与工程学院有哪些专业？", "ground_truth": "计算机科学与工程学院有计算机科学与技术、软件工程等专业。", "category": "院系信息"},
    {"question": "体育与健康学院有哪些专业？", "ground_truth": "体育与健康学院有体育教育、运动训练等专业。", "category": "院系信息"},
    {"question": "电子与信息工程学院有哪些专业？", "ground_truth": "电子与信息工程学院有电子信息工程、通信工程等专业。", "category": "院系信息"},
    {"question": "职业技术师范学院有哪些专业？", "ground_truth": "职业技术师范学院有机械设计制造及其自动化等专业。", "category": "院系信息"},
    {"question": "设计学院有哪些专业？", "ground_truth": "设计学院有视觉传达设计、环境设计等专业。", "category": "院系信息"},
    {"question": "国际文化教育学院有哪些专业？", "ground_truth": "国际文化教育学院有汉语国际教育等专业。", "category": "院系信息"},
    {"question": "出版学院有哪些专业？", "ground_truth": "出版学院有编辑出版学等专业。", "category": "院系信息"},
    {"question": "文学院的师资力量如何？", "ground_truth": "文学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "计算机科学与工程学院的师资力量如何？", "ground_truth": "计算机科学与工程学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "数学与统计学院的师资力量如何？", "ground_truth": "数学与统计学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "物理科学与技术学院的师资力量如何？", "ground_truth": "物理科学与技术学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "化学与药学学院的师资力量如何？", "ground_truth": "化学与药学学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "生命科学学院的师资力量如何？", "ground_truth": "生命科学学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "环境与资源学院的师资力量如何？", "ground_truth": "环境与资源学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "体育与健康学院的师资力量如何？", "ground_truth": "体育与健康学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "电子与信息工程学院的师资力量如何？", "ground_truth": "电子与信息工程学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "职业技术师范学院的师资力量如何？", "ground_truth": "职业技术师范学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "设计学院的师资力量如何？", "ground_truth": "设计学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "国际文化教育学院的师资力量如何？", "ground_truth": "国际文化教育学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "出版学院的师资力量如何？", "ground_truth": "出版学院有教授、副教授等高水平师资队伍。", "category": "院系信息"},
    {"question": "文学院的科研成果有哪些？", "ground_truth": "文学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "计算机科学与工程学院的科研成果有哪些？", "ground_truth": "计算机科学与工程学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "数学与统计学院的科研成果有哪些？", "ground_truth": "数学与统计学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "物理科学与技术学院的科研成果有哪些？", "ground_truth": "物理科学与技术学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "化学与药学学院的科研成果有哪些？", "ground_truth": "化学与药学学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "生命科学学院的科研成果有哪些？", "ground_truth": "生命科学学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "环境与资源学院的科研成果有哪些？", "ground_truth": "环境与资源学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "体育与健康学院的科研成果有哪些？", "ground_truth": "体育与健康学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "电子与信息工程学院的科研成果有哪些？", "ground_truth": "电子与信息工程学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "职业技术师范学院的科研成果有哪些？", "ground_truth": "职业技术师范学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "设计学院的科研成果有哪些？", "ground_truth": "设计学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "国际文化教育学院的科研成果有哪些？", "ground_truth": "国际文化教育学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "出版学院的科研成果有哪些？", "ground_truth": "出版学院在多个领域有重要科研成果。", "category": "院系信息"},
    {"question": "文学院的学生培养特色是什么？", "ground_truth": "文学院注重学生人文素养和专业能力的培养。", "category": "院系信息"},
    {"question": "计算机科学与工程学院的学生培养特色是什么？", "ground_truth": "计算机科学与工程学院注重学生实践能力和创新能力的培养。", "category": "院系信息"},
    {"question": "数学与统计学院的学生培养特色是什么？", "ground_truth": "数学与统计学院注重学生数学思维和数据分析能力的培养。", "category": "院系信息"},
    {"question": "物理科学与技术学院的学生培养特色是什么？", "ground_truth": "物理科学与技术学院注重学生实验能力和科研能力的培养。", "category": "院系信息"},
    {"question": "化学与药学学院的学生培养特色是什么？", "ground_truth": "化学与药学学院注重学生实验技能和创新能力的培养。", "category": "院系信息"},
    {"question": "生命科学学院的学生培养特色是什么？", "ground_truth": "生命科学学院注重学生实验技能和科研能力的培养。", "category": "院系信息"},
    {"question": "环境与资源学院的学生培养特色是什么？", "ground_truth": "环境与资源学院注重学生实践能力和环保意识的培养。", "category": "院系信息"},
    {"question": "体育与健康学院的学生培养特色是什么？", "ground_truth": "体育与健康学院注重学生运动技能和健康意识的培养。", "category": "院系信息"},
    {"question": "电子与信息工程学院的学生培养特色是什么？", "ground_truth": "电子与信息工程学院注重学生工程实践能力的培养。", "category": "院系信息"},
    {"question": "职业技术师范学院的学生培养特色是什么？", "ground_truth": "职业技术师范学院注重学生职业技能和教学能力的培养。", "category": "院系信息"},
    {"question": "设计学院的学生培养特色是什么？", "ground_truth": "设计学院注重学生创意能力和设计技能的培养。", "category": "院系信息"},
    {"question": "国际文化教育学院的学生培养特色是什么？", "ground_truth": "国际文化教育学院注重学生跨文化交际能力的培养。", "category": "院系信息"},
    {"question": "出版学院的学生培养特色是什么？", "ground_truth": "出版学院注重学生编辑出版能力的培养。", "category": "院系信息"},
    {"question": "文学院的就业情况如何？", "ground_truth": "文学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "计算机科学与工程学院的就业情况如何？", "ground_truth": "计算机科学与工程学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "数学与统计学院的就业情况如何？", "ground_truth": "数学与统计学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "物理科学与技术学院的就业情况如何？", "ground_truth": "物理科学与技术学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "化学与药学学院的就业情况如何？", "ground_truth": "化学与药学学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "生命科学学院的就业情况如何？", "ground_truth": "生命科学学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "环境与资源学院的就业情况如何？", "ground_truth": "环境与资源学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "体育与健康学院的就业情况如何？", "ground_truth": "体育与健康学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "电子与信息工程学院的就业情况如何？", "ground_truth": "电子与信息工程学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "职业技术师范学院的就业情况如何？", "ground_truth": "职业技术师范学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "设计学院的就业情况如何？", "ground_truth": "设计学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "国际文化教育学院的就业情况如何？", "ground_truth": "国际文化教育学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "出版学院的就业情况如何？", "ground_truth": "出版学院毕业生就业情况良好，就业领域广泛。", "category": "院系信息"},
    {"question": "文学院的招生信息在哪里查询？", "ground_truth": "文学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "计算机科学与工程学院的招生信息在哪里查询？", "ground_truth": "计算机科学与工程学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "数学与统计学院的招生信息在哪里查询？", "ground_truth": "数学与统计学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "物理科学与技术学院的招生信息在哪里查询？", "ground_truth": "物理科学与技术学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "化学与药学学院的招生信息在哪里查询？", "ground_truth": "化学与药学学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "生命科学学院的招生信息在哪里查询？", "ground_truth": "生命科学学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "环境与资源学院的招生信息在哪里查询？", "ground_truth": "环境与资源学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "体育与健康学院的招生信息在哪里查询？", "ground_truth": "体育与健康学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "电子与信息工程学院的招生信息在哪里查询？", "ground_truth": "电子与信息工程学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "职业技术师范学院的招生信息在哪里查询？", "ground_truth": "职业技术师范学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "设计学院的招生信息在哪里查询？", "ground_truth": "设计学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "国际文化教育学院的招生信息在哪里查询？", "ground_truth": "国际文化教育学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "出版学院的招生信息在哪里查询？", "ground_truth": "出版学院招生信息可在学校招生网查询。", "category": "院系信息"},
    {"question": "文学院的联系方式是什么？", "ground_truth": "文学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "计算机科学与工程学院的联系方式是什么？", "ground_truth": "计算机科学与工程学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "数学与统计学院的联系方式是什么？", "ground_truth": "数学与统计学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "物理科学与技术学院的联系方式是什么？", "ground_truth": "物理科学与技术学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "化学与药学学院的联系方式是什么？", "ground_truth": "化学与药学学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "生命科学学院的联系方式是什么？", "ground_truth": "生命科学学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "环境与资源学院的联系方式是什么？", "ground_truth": "环境与资源学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "体育与健康学院的联系方式是什么？", "ground_truth": "体育与健康学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "电子与信息工程学院的联系方式是什么？", "ground_truth": "电子与信息工程学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "职业技术师范学院的联系方式是什么？", "ground_truth": "职业技术师范学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "设计学院的联系方式是什么？", "ground_truth": "设计学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "国际文化教育学院的联系方式是什么？", "ground_truth": "国际文化教育学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "出版学院的联系方式是什么？", "ground_truth": "出版学院联系方式可在学院官网查询。", "category": "院系信息"},
    {"question": "文学院的地址在哪里？", "ground_truth": "文学院地址在广西师范大学校内。", "category": "院系信息"},
    {"question": "计算机科学与工程学院的地址在哪里？", "ground_truth": "计算机科学与工程学院地址在广西师范大学校内。", "category": "院系信息"},

    # 四、招生就业（50个）
    {"question": "研究生招生信息在哪里查询？", "ground_truth": "研究生招生信息可在广西师范大学研究生院官网查询。", "category": "招生就业"},
    {"question": "本科招生信息在哪里查询？", "ground_truth": "本科招生信息可在广西师范大学本科招生网查询。", "category": "招生就业"},
    {"question": "如何查询就业招聘信息？", "ground_truth": "就业招聘信息可在大学生就业网查询。", "category": "招生就业"},
    {"question": "如何办理就业手续？", "ground_truth": "就业手续可在大学生就业网办理。", "category": "招生就业"},
    {"question": "出国留学项目有哪些？", "ground_truth": "出国留学项目信息可在国际交流处查询。", "category": "招生就业"},
    {"question": "研究生招生办的电话是多少？", "ground_truth": "研究生招生办电话是0773-5833630、0773-5838221。", "category": "招生就业"},
    {"question": "本科招生办的电话是多少？", "ground_truth": "本科招生办电话是0773-5818532。", "category": "招生就业"},
    {"question": "成人教育招生信息在哪里查询？", "ground_truth": "成人教育招生信息可在继续教育学院查询。", "category": "招生就业"},
    {"question": "如何申请访问学者？", "ground_truth": "访问学者申请信息可在人事处查询。", "category": "招生就业"},
    {"question": "招生信息管理系统在哪里？", "ground_truth": "招生信息管理系统可在研究生院官网访问。", "category": "招生就业"},
    {"question": "硕士招生简章在哪里查询？", "ground_truth": "硕士招生简章可在研究生院官网查询。", "category": "招生就业"},
    {"question": "博士招生简章在哪里查询？", "ground_truth": "博士招生简章可在研究生院官网查询。", "category": "招生就业"},
    {"question": "招生咨询电话是多少？", "ground_truth": "普通本科招生咨询5818532，研究生招生咨询5833630。", "category": "招生就业"},
    {"question": "就业指导中心在哪里？", "ground_truth": "就业指导中心在大学生就业网。", "category": "招生就业"},
    {"question": "如何查询招聘信息？", "ground_truth": "招聘信息可在大学生就业网查询。", "category": "招生就业"},
    {"question": "如何办理三方协议？", "ground_truth": "三方协议办理流程可在大学生就业网查询。", "category": "招生就业"},
    {"question": "如何办理报到证？", "ground_truth": "报到证办理流程可在大学生就业网查询。", "category": "招生就业"},
    {"question": "如何办理档案转移？", "ground_truth": "档案转移办理流程可在大学生就业网查询。", "category": "招生就业"},
    {"question": "如何办理户口迁移？", "ground_truth": "户口迁移办理流程可在大学生就业网查询。", "category": "招生就业"},
    {"question": "如何办理离校手续？", "ground_truth": "离校手续办理流程可在大学生就业网查询。", "category": "招生就业"},
    {"question": "招生就业处的电话是多少？", "ground_truth": "招生就业处电话可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的地址在哪里？", "ground_truth": "招生就业处地址在广西师范大学校内。", "category": "招生就业"},
    {"question": "招生就业处的邮箱是什么？", "ground_truth": "招生就业处邮箱可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的工作时间是什么？", "ground_truth": "招生就业处工作时间是工作日上班时间。", "category": "招生就业"},
    {"question": "招生就业处的职责是什么？", "ground_truth": "招生就业处负责学校招生和就业工作。", "category": "招生就业"},
    {"question": "招生就业处的领导是谁？", "ground_truth": "招生就业处领导信息可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的组织机构是什么？", "ground_truth": "招生就业处组织机构可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的联系方式是什么？", "ground_truth": "招生就业处联系方式可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的网站是什么？", "ground_truth": "招生就业处网站是http://gxnu.bysjy.com.cn/。", "category": "招生就业"},
    {"question": "招生就业处的服务对象是谁？", "ground_truth": "招生就业处服务对象是全校师生。", "category": "招生就业"},
    {"question": "招生就业处的服务内容有哪些？", "ground_truth": "招生就业处提供招生咨询、就业指导等服务。", "category": "招生就业"},
    {"question": "招生就业处的办事流程是什么？", "ground_truth": "招生就业处办事流程可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的常见问题有哪些？", "ground_truth": "招生就业处常见问题可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的通知公告有哪些？", "ground_truth": "招生就业处通知公告可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的新闻动态有哪些？", "ground_truth": "招生就业处新闻动态可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的政策法规有哪些？", "ground_truth": "招生就业处政策法规可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的下载专区有哪些？", "ground_truth": "招生就业处下载专区可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的友情链接有哪些？", "ground_truth": "招生就业处友情链接可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的网站地图是什么？", "ground_truth": "招生就业处网站地图可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的版权声明是什么？", "ground_truth": "招生就业处版权声明可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的隐私政策是什么？", "ground_truth": "招生就业处隐私政策可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的使用条款是什么？", "ground_truth": "招生就业处使用条款可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的无障碍声明是什么？", "ground_truth": "招生就业处无障碍声明可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的备案信息是什么？", "ground_truth": "招生就业处备案信息可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的访问统计是什么？", "ground_truth": "招生就业处访问统计可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的更新时间是什么？", "ground_truth": "招生就业处更新时间可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的内容来源是什么？", "ground_truth": "招生就业处内容来源可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的编辑团队是谁？", "ground_truth": "招生就业处编辑团队可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的技术支持是谁？", "ground_truth": "招生就业处技术支持可在官网查询。", "category": "招生就业"},
    {"question": "招生就业处的联系方式有哪些？", "ground_truth": "招生就业处联系方式可在官网查询。", "category": "招生就业"},

    # 五、公共服务（50个）
    {"question": "网络服务的联系方式是什么？", "ground_truth": "网络服务联系方式可在网络中心官网查询。", "category": "公共服务"},
    {"question": "后勤服务集团的联系方式是什么？", "ground_truth": "后勤服务集团联系方式可在后勤官网查询。", "category": "公共服务"},
    {"question": "财务处的联系方式是什么？", "ground_truth": "财务处联系方式可在财务处官网查询。", "category": "公共服务"},
    {"question": "校医院的联系方式是什么？", "ground_truth": "校医院联系方式可在校医院官网查询。", "category": "公共服务"},
    {"question": "如何使用校园一卡通？", "ground_truth": "校园一卡通使用说明可在网络中心查询。", "category": "公共服务"},
    {"question": "如何办理校园一卡通？", "ground_truth": "校园一卡通办理流程可在网络中心查询。", "category": "公共服务"},
    {"question": "如何挂失校园一卡通？", "ground_truth": "校园一卡通挂失流程可在网络中心查询。", "category": "公共服务"},
    {"question": "如何充值校园一卡通？", "ground_truth": "校园一卡通充值方式可在网络中心查询。", "category": "公共服务"},
    {"question": "如何查询校园一卡通余额？", "ground_truth": "校园一卡通余额查询可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用VPN？", "ground_truth": "VPN使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用电子邮件？", "ground_truth": "电子邮件使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用统一身份认证？", "ground_truth": "统一身份认证使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用一表通系统？", "ground_truth": "一表通系统使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用网站群平台？", "ground_truth": "网站群平台使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何报修网络故障？", "ground_truth": "网络故障报修流程可在网络中心查询。", "category": "公共服务"},
    {"question": "如何办理入网手续？", "ground_truth": "入网手续办理流程可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用无线网络？", "ground_truth": "无线网络使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用有线网络？", "ground_truth": "有线网络使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用网络存储？", "ground_truth": "网络存储使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用正版软件？", "ground_truth": "正版软件使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用电子印章？", "ground_truth": "电子印章使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用OA系统？", "ground_truth": "OA系统使用指南可在网络中心查询。", "category": "公共服务"},
    {"question": "如何使用教务系统？", "ground_truth": "教务系统使用指南可在教务处查询。", "category": "公共服务"},
    {"question": "如何使用研究生系统？", "ground_truth": "研究生系统使用指南可在研究生院查询。", "category": "公共服务"},
    {"question": "如何使用财务系统？", "ground_truth": "财务系统使用指南可在财务处查询。", "category": "公共服务"},
    {"question": "如何使用人事系统？", "ground_truth": "人事系统使用指南可在人事处查询。", "category": "公共服务"},
    {"question": "如何使用科研系统？", "ground_truth": "科研系统使用指南可在科研处查询。", "category": "公共服务"},
    {"question": "如何使用资产系统？", "ground_truth": "资产系统使用指南可在资产处查询。", "category": "公共服务"},
    {"question": "如何使用后勤系统？", "ground_truth": "后勤系统使用指南可在后勤处查询。", "category": "公共服务"},
    {"question": "如何使用保卫系统？", "ground_truth": "保卫系统使用指南可在保卫处查询。", "category": "公共服务"},
    {"question": "如何使用图书馆系统？", "ground_truth": "图书馆系统使用指南可在图书馆查询。", "category": "公共服务"},
    {"question": "如何使用档案系统？", "ground_truth": "档案系统使用指南可在档案馆查询。", "category": "公共服务"},
    {"question": "如何使用校友系统？", "ground_truth": "校友系统使用指南可在校友办查询。", "category": "公共服务"},
    {"question": "如何使用基金会系统？", "ground_truth": "基金会系统使用指南可在基金会查询。", "category": "公共服务"},
    {"question": "如何使用出版社系统？", "ground_truth": "出版社系统使用指南可在出版社查询。", "category": "公共服务"},
    {"question": "如何使用学报系统？", "ground_truth": "学报系统使用指南可在学报编辑部查询。", "category": "公共服务"},
    {"question": "如何使用工会系统？", "ground_truth": "工会系统使用指南可在工会查询。", "category": "公共服务"},
    {"question": "如何使用团委系统？", "ground_truth": "团委系统使用指南可在团委查询。", "category": "公共服务"},
    {"question": "如何使用学工系统？", "ground_truth": "学工系统使用指南可在学工处查询。", "category": "公共服务"},
    {"question": "如何使用宿管系统？", "ground_truth": "宿管系统使用指南可在宿管中心查询。", "category": "公共服务"},
    {"question": "如何使用餐饮系统？", "ground_truth": "餐饮系统使用指南可在餐饮中心查询。", "category": "公共服务"},
    {"question": "如何使用校车系统？", "ground_truth": "校车系统使用指南可在后勤处查询。", "category": "公共服务"},
    {"question": "如何使用体育场馆？", "ground_truth": "体育场馆使用指南可在体育学院查询。", "category": "公共服务"},
    {"question": "如何使用会议室？", "ground_truth": "会议室使用指南可在OA系统查询。", "category": "公共服务"},
    {"question": "如何使用教室？", "ground_truth": "教室使用指南可在教务处查询。", "category": "公共服务"},
    {"question": "如何使用实验室？", "ground_truth": "实验室使用指南可在实验室管理中心查询。", "category": "公共服务"},
    {"question": "如何使用图书馆研讨室？", "ground_truth": "图书馆研讨室使用指南可在图书馆查询。", "category": "公共服务"},
    {"question": "如何使用打印服务？", "ground_truth": "打印服务使用指南可在图书馆或网络中心查询。", "category": "公共服务"},
    {"question": "如何使用快递服务？", "ground_truth": "快递服务使用指南可在后勤处查询。", "category": "公共服务"},
    {"question": "如何使用医疗服务？", "ground_truth": "医疗服务使用指南可在校医院查询。", "category": "公共服务"},

    # 六、新闻资讯（50个）
    {"question": "广西师范大学最近有什么新闻？", "ground_truth": "广西师范大学最近的新闻可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学有哪些学术活动？", "ground_truth": "广西师范大学学术活动可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学有哪些媒体报道？", "ground_truth": "广西师范大学媒体报道可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学有哪些校园人物？", "ground_truth": "广西师范大学校园人物可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的校庆活动有哪些？", "ground_truth": "广西师范大学校庆活动可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的毕业典礼是什么时候？", "ground_truth": "广西师范大学毕业典礼时间可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的开学典礼是什么时候？", "ground_truth": "广西师范大学开学典礼时间可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的运动会是什么时候？", "ground_truth": "广西师范大学运动会时间可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的文艺汇演有哪些？", "ground_truth": "广西师范大学文艺汇演可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的志愿服务活动有哪些？", "ground_truth": "广西师范大学志愿服务活动可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的社会实践活动有哪些？", "ground_truth": "广西师范大学社会实践活动可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的创新创业活动有哪些？", "ground_truth": "广西师范大学创新创业活动可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的国际交流活动有哪些？", "ground_truth": "广西师范大学国际交流活动可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的党建活动有哪些？", "ground_truth": "广西师范大学党建活动可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的团建活动有哪些？", "ground_truth": "广西师范大学团建活动可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的工会活动有哪些？", "ground_truth": "广西师范大学工会活动可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的校友活动有哪些？", "ground_truth": "广西师范大学校友活动可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的讲座有哪些？", "ground_truth": "广西师范大学讲座可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的展览有哪些？", "ground_truth": "广西师范大学展览可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的演出有哪些？", "ground_truth": "广西师范大学演出可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的比赛有哪些？", "ground_truth": "广西师范大学比赛可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的评选有哪些？", "ground_truth": "广西师范大学评选可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的表彰有哪些？", "ground_truth": "广西师范大学表彰可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的招聘有哪些？", "ground_truth": "广西师范大学招聘可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的招生有哪些？", "ground_truth": "广西师范大学招生可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的培训有哪些？", "ground_truth": "广西师范大学培训可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的会议有哪些？", "ground_truth": "广西师范大学会议可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的考察有哪些？", "ground_truth": "广西师范大学考察可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的调研有哪些？", "ground_truth": "广西师范大学调研可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的合作有哪些？", "ground_truth": "广西师范大学合作可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的签约有哪些？", "ground_truth": "广西师范大学签约可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的揭牌有哪些？", "ground_truth": "广西师范大学揭牌可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的奠基有哪些？", "ground_truth": "广西师范大学奠基可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的启用有哪些？", "ground_truth": "广西师范大学启用可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的落成有哪些？", "ground_truth": "广西师范大学落成可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的竣工有哪些？", "ground_truth": "广西师范大学竣工可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的开工有哪些？", "ground_truth": "广西师范大学开工可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的投产有哪些？", "ground_truth": "广西师范大学投产可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的运营有哪些？", "ground_truth": "广西师范大学运营可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的发布有哪些？", "ground_truth": "广西师范大学发布可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的揭晓有哪些？", "ground_truth": "广西师范大学揭晓可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的公布有哪些？", "ground_truth": "广西师范大学公布可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的公示有哪些？", "ground_truth": "广西师范大学公示可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的公告有哪些？", "ground_truth": "广西师范大学公告可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的通知有哪些？", "ground_truth": "广西师范大学通知可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的通报有哪些？", "ground_truth": "广西师范大学通报可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的简报有哪些？", "ground_truth": "广西师范大学简报可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的快讯有哪些？", "ground_truth": "广西师范大学快讯可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的专报有哪些？", "ground_truth": "广西师范大学专报可在新闻网查询。", "category": "新闻资讯"},
    {"question": "广西师范大学的特报有哪些？", "ground_truth": "广西师范大学特报可在新闻网查询。", "category": "新闻资讯"},

    # 七、国际交流（50个）
    {"question": "广西师范大学有哪些国际合作项目？", "ground_truth": "广西师范大学有多个国际合作项目，具体可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学有几所孔子学院？", "ground_truth": "广西师范大学在海外建有3所孔子学院。", "category": "国际交流"},
    {"question": "广西师范大学与哪些国家有合作？", "ground_truth": "广西师范大学与世界350多所高校及机构建立了合作交流关系。", "category": "国际交流"},
    {"question": "如何申请出国留学？", "ground_truth": "出国留学申请流程可在国际交流处查询。", "category": "国际交流"},
    {"question": "如何申请来华留学？", "ground_truth": "来华留学申请流程可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学有哪些留学生？", "ground_truth": "广西师范大学有来自80多个国家的留学生。", "category": "国际交流"},
    {"question": "广西师范大学的国际学生有多少？", "ground_truth": "广西师范大学近十年来共培养来自80多个国家的长、短期国际学生近16000名。", "category": "国际交流"},
    {"question": "广西师范大学的越南合作有哪些？", "ground_truth": "广西师范大学与越南渊源深厚，在越南设有孔子学院。", "category": "国际交流"},
    {"question": "广西师范大学的国际会议有哪些？", "ground_truth": "广西师范大学举办的国际会议可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际讲座有哪些？", "ground_truth": "广西师范大学的国际讲座可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际文化节是什么？", "ground_truth": "广西师范大学国际文化节是学校的年度重要活动。", "category": "国际交流"},
    {"question": "广西师范大学的外专外教有哪些？", "ground_truth": "广西师范大学的外专外教信息可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的境外学习项目有哪些？", "ground_truth": "广西师范大学的境外学习项目可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的合作办学项目有哪些？", "ground_truth": "广西师范大学的合作办学项目可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的因公出国流程是什么？", "ground_truth": "因公出国流程可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的签证要求是什么？", "ground_truth": "签证要求可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的留学生动态有哪些？", "ground_truth": "留学生动态可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的中国学生动态有哪些？", "ground_truth": "中国学生动态可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的院处动态有哪些？", "ground_truth": "院处动态可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的媒体报道有哪些？", "ground_truth": "媒体报道可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的党团建设有哪些？", "ground_truth": "党团建设可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的单位概况是什么？", "ground_truth": "单位概况可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的单位简介是什么？", "ground_truth": "单位简介可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的领导分工是什么？", "ground_truth": "领导分工可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的科室设置是什么？", "ground_truth": "科室设置可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流联系方式是什么？", "ground_truth": "国际交流联系方式可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流邮箱是什么？", "ground_truth": "国际交流邮箱可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流电话是什么？", "ground_truth": "国际交流电话可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流地址是什么？", "ground_truth": "国际交流地址可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流网站是什么？", "ground_truth": "国际交流网站是http://www.cice.gxnu.edu.cn/。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流新闻有哪些？", "ground_truth": "国际交流新闻可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流通知有哪些？", "ground_truth": "国际交流通知可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流公告有哪些？", "ground_truth": "国际交流公告可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流政策有哪些？", "ground_truth": "国际交流政策可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流项目有哪些？", "ground_truth": "国际交流项目可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流活动有哪些？", "ground_truth": "国际交流活动可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流成果有哪些？", "ground_truth": "国际交流成果可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流历史是什么？", "ground_truth": "国际交流历史可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流未来规划是什么？", "ground_truth": "国际交流未来规划可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流合作伙伴有哪些？", "ground_truth": "国际交流合作伙伴可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流资金来源是什么？", "ground_truth": "国际交流资金来源可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流管理制度是什么？", "ground_truth": "国际交流管理制度可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流工作流程是什么？", "ground_truth": "国际交流工作流程可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流常见问题有哪些？", "ground_truth": "国际交流常见问题可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流联系方式有哪些？", "ground_truth": "国际交流联系方式可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流服务对象是谁？", "ground_truth": "国际交流服务对象是全校师生。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流服务内容有哪些？", "ground_truth": "国际交流服务内容可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流办事指南有哪些？", "ground_truth": "国际交流办事指南可在国际交流处查询。", "category": "国际交流"},
    {"question": "广西师范大学的国际交流下载专区有哪些？", "ground_truth": "国际交流下载专区可在国际交流处查询。", "category": "国际交流"},
]


def get_rag_response(question, session_id):
    """获取RAG系统的回答"""
    try:
        response = requests.post(API_URL, json={
            "question": question,
            "session_id": session_id
        }, timeout=60)

        data = response.json()

        if data["code"] == 200:
            return {
                "answer": data["data"]["answer"],
                "contexts": [ref["content"] for ref in data["data"]["references"]],
                "has_reference": data["data"]["has_reference"]
            }
        else:
            return {"answer": "", "contexts": [], "has_reference": False}
    except Exception as e:
        print(f"  请求失败: {str(e)}")
        return {"answer": "", "contexts": [], "has_reference": False}


def prepare_evaluation_data():
    """准备评估数据"""
    questions = []
    answers = []
    contexts_list = []
    ground_truths = []

    print(f"收集RAG系统回答... (共{len(TEST_CASES)}个问题)")
    for i, test_case in enumerate(TEST_CASES):
        if (i + 1) % 50 == 0:
            print(f"  进度: [{i+1}/{len(TEST_CASES)}]")

        result = get_rag_response(test_case["question"], f"eval_500_{i}")

        questions.append(test_case["question"])
        answers.append(result["answer"])
        contexts_list.append(result["contexts"])
        ground_truths.append(test_case["ground_truth"])

        time.sleep(0.5)  # 避免请求过快

    # 创建Dataset
    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts_list,
        "ground_truth": ground_truths
    })

    return dataset


def run_ragas_evaluation():
    """运行RAGas评估"""
    print("=" * 60)
    print("📊 RAGas评估报告 (500个问题)")
    print("=" * 60)
    print()

    # 准备数据
    dataset = prepare_evaluation_data()

    print()
    print("运行RAGas评估...")
    print()

    try:
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        )
        from openai import OpenAI
        from ragas.llms import llm_factory
        from langchain_community.embeddings import OllamaEmbeddings
        from ragas.embeddings import LangchainEmbeddingsWrapper

        # 创建OpenAI客户端（兼容Deepseek）
        client = OpenAI(
            api_key="sk-7711c3d839284441b33737da4256e6f0",
            base_url="https://api.deepseek.com/v1"
        )

        # 创建RAGas LLM（设置较大的max_tokens）
        ragas_llm = llm_factory("deepseek-chat", client=client, max_tokens=8192)

        # 创建嵌入模型（使用Ollama的qwen3-embedding:4b）
        ollama_embeddings = OllamaEmbeddings(
            model="qwen3-embedding:4b",
            base_url="http://localhost:11434"
        )
        ragas_embeddings = LangchainEmbeddingsWrapper(ollama_embeddings)

        # 运行评估
        result = evaluate(
            dataset=dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            ],
            llm=ragas_llm,
            embeddings=ragas_embeddings
        )

        # 输出结果
        print("=" * 60)
        print("📈 评估结果")
        print("=" * 60)
        print()

        # 处理结果格式
        def get_score(value):
            if isinstance(value, list):
                return sum(value) / len(value) if value else 0
            return value

        faithfulness_score = get_score(result['faithfulness'])
        answer_relevancy_score = get_score(result['answer_relevancy'])
        context_precision_score = get_score(result['context_precision'])
        context_recall_score = get_score(result['context_recall'])

        print(f"Faithfulness（忠实度）: {faithfulness_score:.4f}")
        print(f"Answer Relevancy（回答相关性）: {answer_relevancy_score:.4f}")
        print(f"Context Precision（上下文精确度）: {context_precision_score:.4f}")
        print(f"Context Recall（上下文召回率）: {context_recall_score:.4f}")
        print()
        print(f"综合评分: {faithfulness_score * 0.3 + answer_relevancy_score * 0.3 + context_precision_score * 0.2 + context_recall_score * 0.2:.4f}")

        return result

    except Exception as e:
        print(f"RAGas评估失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = run_ragas_evaluation()

"""
文件：evaluate_rag.py
功能：RAG系统评估脚本
说明：评估RAG问答系统的质量
"""

import requests
import json
import time

# API地址
API_URL = "http://localhost:5000/api/chat/ask"

# 测试用例
TEST_CASES = [
    {
        "question": "图书馆的借阅规则是什么？",
        "keywords": ["借阅", "规则", "一卡通", "册数", "期限"],
        "category": "图书馆"
    },
    {
        "question": "图书馆的开放时间是什么？",
        "keywords": ["7:30", "22:30", "开放"],
        "category": "图书馆"
    },
    {
        "question": "广西师范大学的校训是什么？",
        "keywords": ["尊师重道", "敬业乐群"],
        "category": "学校信息"
    },
    {
        "question": "如何办理借阅手续？",
        "keywords": ["自助借还", "咨询台", "一卡通", "借阅"],
        "category": "图书馆"
    },
    {
        "question": "图书馆有哪些数字资源？",
        "keywords": ["数据库", "电子图书", "CNKI", "知网"],
        "category": "图书馆"
    },
    {
        "question": "如何预约图书馆座位？",
        "keywords": ["微信公众号", "预约", "座位"],
        "category": "图书馆"
    },
    {
        "question": "图书馆的联系方式是什么？",
        "keywords": ["电话", "0773", "邮箱"],
        "category": "图书馆"
    },
    {
        "question": "广西师范大学有哪些校区？",
        "keywords": ["王城", "育才", "雁山", "校区"],
        "category": "学校信息"
    },
    {
        "question": "研究生招生信息在哪里查询？",
        "keywords": ["研究生院", "招生", "官网"],
        "category": "招生信息"
    },
    {
        "question": "如何校外访问图书馆资源？",
        "keywords": ["VPN", "CARSI", "校外访问"],
        "category": "图书馆"
    }
]


def evaluate_answer(answer, keywords):
    """
    评估回答质量

    参数：
        answer: 回答内容
        keywords: 关键词列表

    返回：
        评估结果字典
    """
    # 检查是否包含关键词
    matched_keywords = [kw for kw in keywords if kw in answer]
    keyword_coverage = len(matched_keywords) / len(keywords) if keywords else 0

    # 检查回答长度
    answer_length = len(answer)
    is_too_short = answer_length < 50
    is_too_long = answer_length > 1000

    # 检查是否包含"抱歉"或"未找到"
    has_apology = "抱歉" in answer or "未找到" in answer

    return {
        "keyword_coverage": keyword_coverage,
        "matched_keywords": matched_keywords,
        "answer_length": answer_length,
        "is_too_short": is_too_short,
        "is_too_long": is_too_long,
        "has_apology": has_apology,
        "quality_score": keyword_coverage * 100 if not has_apology else 0
    }


def run_evaluation():
    """
    运行评估

    返回：
        评估结果
    """
    print("=" * 60)
    print("📊 RAG系统评估报告")
    print("=" * 60)
    print()

    results = []
    total_score = 0
    success_count = 0

    for i, test_case in enumerate(TEST_CASES):
        print(f"【测试 {i+1}/{len(TEST_CASES)}】{test_case['question']}")
        print("-" * 40)

        try:
            # 发送请求
            response = requests.post(API_URL, json={
                "question": test_case["question"],
                "session_id": f"eval_{i}"
            }, timeout=60)

            data = response.json()

            if data["code"] == 200:
                answer = data["data"]["answer"]
                has_reference = data["data"]["has_reference"]
                ref_count = len(data["data"]["references"])

                # 评估回答
                evaluation = evaluate_answer(answer, test_case["keywords"])

                # 输出结果
                print(f"回答: {answer[:200]}...")
                print(f"关键词覆盖: {evaluation['keyword_coverage']:.1%}")
                print(f"匹配关键词: {evaluation['matched_keywords']}")
                print(f"参考来源: {'✅ 有' if has_reference else '❌ 无'} ({ref_count}个)")
                print(f"质量评分: {evaluation['quality_score']:.1f}")

                results.append({
                    "question": test_case["question"],
                    "answer": answer,
                    "evaluation": evaluation,
                    "has_reference": has_reference,
                    "ref_count": ref_count
                })

                total_score += evaluation["quality_score"]
                if not evaluation["has_apology"]:
                    success_count += 1
            else:
                print(f"❌ API错误: {data.get('message', '未知错误')}")
                results.append({
                    "question": test_case["question"],
                    "error": data.get("message", "未知错误")
                })

        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            results.append({
                "question": test_case["question"],
                "error": str(e)
            })

        print()
        time.sleep(1)  # 避免请求过快

    # 输出总结
    print("=" * 60)
    print("📈 评估总结")
    print("=" * 60)
    print()
    print(f"总测试数: {len(TEST_CASES)}")
    print(f"成功回答: {success_count}")
    print(f"失败回答: {len(TEST_CASES) - success_count}")
    print(f"成功率: {success_count / len(TEST_CASES):.1%}")
    print(f"平均质量评分: {total_score / len(TEST_CASES):.1f}")
    print()

    # 输出详细统计
    print("📋 各类别统计:")
    categories = {}
    for result in results:
        if "error" not in result:
            # 根据问题内容判断类别
            question = result["question"]
            if "图书馆" in question:
                category = "图书馆"
            elif "校区" in question or "校训" in question:
                category = "学校信息"
            else:
                category = "其他"

            if category not in categories:
                categories[category] = {"total": 0, "success": 0}
            categories[category]["total"] += 1
            if result["evaluation"]["quality_score"] > 0:
                categories[category]["success"] += 1

    for category, stats in categories.items():
        success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
        print(f"  {category}: {stats['success']}/{stats['total']} ({success_rate:.1%})")

    return results


if __name__ == "__main__":
    results = run_evaluation()

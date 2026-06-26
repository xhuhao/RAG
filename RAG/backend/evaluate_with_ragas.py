"""
文件：evaluate_with_ragas.py
功能：使用RAGas评估RAG系统
说明：基于RAGas库的RAG系统质量评估
"""

import requests
import json
import time
from datasets import Dataset

# API地址
API_URL = "http://localhost:5000/api/chat/ask"

# 测试用例（包含标准答案）
TEST_CASES = [
    {
        "question": "图书馆的借阅规则是什么？",
        "ground_truth": "广西师范大学图书馆的借阅规则包括：读者凭本人已开通借书功能的校园一卡通借阅图书；校园一卡通仅限本人使用，禁止转借；不同类型读者的借阅册数和期限不同；图书到期前7天内可办理续借。",
        "category": "图书馆"
    },
    {
        "question": "图书馆的开放时间是什么？",
        "ground_truth": "广西师范大学图书馆的开放时间为7:30—22:30。",
        "category": "图书馆"
    },
    {
        "question": "广西师范大学的校训是什么？",
        "ground_truth": "广西师范大学的校训是尊师重道，敬业乐群。尊师重道意为尊敬师长，重视道义与道德修养。敬业乐群意为专心致力于学业或事业，乐于与同伴合作共处，出自《礼记·学记》。",
        "category": "学校信息"
    },
    {
        "question": "如何办理借阅手续？",
        "ground_truth": "办理借阅手续有两种方式：1.使用自助借还机办理（推荐），可使用电子证或一卡通；2.至各校区图书馆咨询台办理。借阅时需凭本人已开通借书功能的校园一卡通。",
        "category": "图书馆"
    },
    {
        "question": "图书馆有哪些数字资源？",
        "ground_truth": "广西师范大学图书馆拥有274万余册电子图书和117个数据库，涵盖图书、期刊、报纸、学位论文、会议论文、标准、专利等资源类型，包括CNKI中国知网等数据库。",
        "category": "图书馆"
    },
    {
        "question": "如何预约图书馆座位？",
        "ground_truth": "预约图书馆座位可通过以下方式：1.微信预约，关注广西师范大学图书馆公众号；2.PC端或移动设备网页预约，访问http://ic.gxnu.edu.cn/；使用个人数字校园账号登录后即可预约。",
        "category": "图书馆"
    },
    {
        "question": "图书馆的联系方式是什么？",
        "ground_truth": "广西师范大学图书馆的联系方式包括：电话0773-8283061、0773-5846415；QQ咨询958057199；咨询邮箱958057199@qq.com；馆长信箱library@mailbox.gxnu.edu.cn。",
        "category": "图书馆"
    },
    {
        "question": "广西师范大学有哪些校区？",
        "ground_truth": "广西师范大学共有三个校区：王城校区位于广西桂林市秀峰区王城1号；育才校区位于广西桂林市七星区育才路15号；雁山校区位于广西桂林市雁山区雁中路1号。",
        "category": "学校信息"
    },
    {
        "question": "研究生招生信息在哪里查询？",
        "ground_truth": "研究生招生信息可通过以下渠道查询：1.广西师范大学研究生院官网；2.中国研究生招生信息网（研招网）；3.各二级招生单位官网；4.电话咨询研招办0773-5838221。",
        "category": "招生信息"
    },
    {
        "question": "如何校外访问图书馆资源？",
        "ground_truth": "校外访问图书馆资源有两种方式：1.VPN访问，教职员工可通过https://sslvpn.gxnu.edu.cn/访问，教职员工及学生可通过https://webvpn.gxnu.edu.cn/访问；2.CARSI访问，部分数据库支持CARSI方式，无需VPN。",
        "category": "图书馆"
    }
]


def get_rag_response(question, session_id):
    """
    获取RAG系统的回答

    参数：
        question: 用户问题
        session_id: 会话ID

    返回：
        回答和参考来源
    """
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
        print(f"请求失败: {str(e)}")
        return {"answer": "", "contexts": [], "has_reference": False}


def prepare_evaluation_data():
    """
    准备评估数据

    返回：
        RAGas格式的评估数据
    """
    questions = []
    answers = []
    contexts_list = []
    ground_truths = []

    print("收集RAG系统回答...")
    for i, test_case in enumerate(TEST_CASES):
        print(f"  [{i+1}/{len(TEST_CASES)}] {test_case['question']}")

        result = get_rag_response(test_case["question"], f"eval_{i}")

        questions.append(test_case["question"])
        answers.append(result["answer"])
        contexts_list.append(result["contexts"])
        ground_truths.append(test_case["ground_truth"])

        time.sleep(1)  # 避免请求过快

    # 创建Dataset
    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts_list,
        "ground_truth": ground_truths
    })

    return dataset


def run_ragas_evaluation():
    """
    运行RAGas评估
    """
    print("=" * 60)
    print("📊 RAGas评估报告")
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

        # 创建OpenAI客户端（使用mimo-v2.5-pro）
        client = OpenAI(
            api_key="sk-cv3c0g0f4v2lzn48dmeqyupdhks79i0roym3hkvz81l9hc8f",
            base_url="https://api.xiaomimimo.com/v1"
        )

        # 创建RAGas LLM（设置较大的max_tokens）
        ragas_llm = llm_factory("mimo-v2.5-pro", client=client, max_tokens=8192)

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

        # 处理结果格式（可能是列表或单个值）
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

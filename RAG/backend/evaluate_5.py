"""
文件：evaluate_5.py
功能：5个问题的RAGas快速评估
"""

import sys
import os
import time
import requests
from datasets import Dataset

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# API地址
API_URL = "http://localhost:5000/api/chat/ask"

# 5个测试问题
TEST_CASES = [
    {
        "question": "图书馆的借阅规则是什么？",
        "ground_truth": "读者凭校园一卡通借阅图书，每次最多借10本，借期30天。",
        "category": "图书馆"
    },
    {
        "question": "广西师范大学的校训是什么？",
        "ground_truth": "广西师范大学的校训是尊师重道，敬业乐群。",
        "category": "学校信息"
    },
    {
        "question": "图书馆的开放时间是什么？",
        "ground_truth": "图书馆的开放时间为7:30—22:30。",
        "category": "图书馆"
    },
    {
        "question": "广西师范大学有哪些校区？",
        "ground_truth": "广西师范大学有王城、育才、雁山三个校区。",
        "category": "学校信息"
    },
    {
        "question": "如何预约图书馆座位？",
        "ground_truth": "通过微信公众号或网页http://ic.gxnu.edu.cn/预约图书馆座位。",
        "category": "图书馆"
    }
]


def get_rag_response(question, session_id):
    """获取RAG系统的回答"""
    try:
        response = requests.post(API_URL, json={
            "question": question,
            "session_id": session_id
        }, timeout=120)

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

    print("收集RAG系统回答...")
    for i, test_case in enumerate(TEST_CASES):
        print(f"  [{i+1}/{len(TEST_CASES)}] {test_case['question']}")

        result = get_rag_response(test_case["question"], f"eval_5_{i}")

        questions.append(test_case["question"])
        answers.append(result["answer"])
        contexts_list.append(result["contexts"])
        ground_truths.append(test_case["ground_truth"])

        time.sleep(1)

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
    print("📊 RAGas评估报告 (5个问题)")
    print("=" * 60)
    print()

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

        # 创建RAGas LLM
        ragas_llm = llm_factory("mimo-v2.5-pro", client=client, max_tokens=4096)

        # 创建嵌入模型
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

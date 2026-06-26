"""
检查哪些问题没有答案
"""
import sys
import os
import requests
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

API_URL = 'http://localhost:5000/api/chat/ask'

from evaluate_500 import TEST_CASES

print('=' * 60)
print('📋 检查哪些问题没有答案')
print('=' * 60)

no_answer = []
has_answer = []

for i, tc in enumerate(TEST_CASES):
    try:
        resp = requests.post(API_URL, json={'question': tc['question'], 'session_id': f'c{i}'}, timeout=30)
        data = resp.json()
        if data['code'] == 200:
            answer = data['data']['answer']
            if '抱歉' in answer or '未找到' in answer or not answer:
                no_answer.append({'i': i+1, 'q': tc['question'], 'cat': tc.get('category', '?')})
            else:
                has_answer.append({'i': i+1, 'q': tc['question'], 'cat': tc.get('category', '?')})
        else:
            no_answer.append({'i': i+1, 'q': tc['question'], 'cat': tc.get('category', '?')})
    except Exception as e:
        no_answer.append({'i': i+1, 'q': tc['question'], 'cat': tc.get('category', '?')})

    if (i + 1) % 50 == 0:
        print(f'  进度: {i+1}/{len(TEST_CASES)}')

print()
print(f'总问题: {len(TEST_CASES)}')
print(f'有答案: {len(has_answer)} ({len(has_answer)/len(TEST_CASES)*100:.1f}%)')
print(f'无答案: {len(no_answer)} ({len(no_answer)/len(TEST_CASES)*100:.1f}%)')
print()

cats = {}
for q in no_answer:
    c = q['cat']
    if c not in cats:
        cats[c] = []
    cats[c].append(q)

print('=' * 60)
print('❌ 无答案的问题（按分类）')
print('=' * 60)
for c, qs in cats.items():
    print(f'\n【{c}】({len(qs)}个无答案)')
    print('-' * 40)
    for q in qs:
        print(f"  {q['i']}. {q['q']}")

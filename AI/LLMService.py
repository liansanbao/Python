# _*_ coding: utf-8 _*_
# @Time : 2026/2/25 星期三 10:13
# @Author : 韦丽
# @Version: V 1.0
# @File : LLMService.py
# @desc :


import requests
import json


class LLMService:
    def __init__(self, api_key, model_name="qwen-plus"):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def generate_answer(self, query, context, stream=False):
        prompt = f"基于以下资料回答问题：\n\n{context}\n\n问题：{query}\n回答："
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "stream": stream,
                "temperature": 0.7
            }
        }

        response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
        if stream:
            return response
        else:
            result = response.json()
            return result['output']['text']

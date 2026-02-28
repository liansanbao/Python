# _*_ coding: utf-8 _*_
# @Time : 2026/2/25 星期三 10:14
# @Author : 韦丽
# @Version: V 1.0
# @File : TTSService.py
# @desc :


import requests
import json


class TTSService:
    def __init__(self, access_key_id, access_key_secret, app_key):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.app_key = app_key
        self.token = self._get_token()

    def _get_token(self):
        # 简化token获取逻辑
        return "mock_token"

    def synthesize_speech(self, text, output_file):
        url = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/tts"
        headers = {
            "X-NLS-Token": self.token,
            "Content-Type": "application/json"
        }
        data = {
            "appkey": self.app_key,
            "text": text,
            "format": "wav",
            "sample_rate": 16000
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return True
        return False

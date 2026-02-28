# _*_ coding: utf-8 _*_
# @Time : 2026/2/25 星期三 10:13
# @Author : 韦丽
# @Version: V 1.0
# @File : ASRService.py
# @desc :


import requests
import base64


class ASRService:
    def __init__(self, access_key_id, access_key_secret, app_key):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.app_key = app_key
        self.token = self._get_token()

    def _get_token(self):
        # 简化token获取逻辑
        return "mock_token"

    def recognize_audio(self, audio_file_path):
        with open(audio_file_path, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('utf-8')

        url = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr"
        headers = {
            "X-NLS-Token": self.token,
            "Content-Type": "application/octet-stream"
        }
        params = {
            "appkey": self.app_key,
            "format": "wav",
            "sample_rate": 16000
        }

        response = requests.post(url, headers=headers, params=params, data=audio_data)
        result = response.json()
        return result.get('result', '')


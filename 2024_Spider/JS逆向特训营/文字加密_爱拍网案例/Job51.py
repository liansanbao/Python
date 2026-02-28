# _*_ coding: utf-8 _*_
# @Time : 2025/4/28 23:16
# @Author : 韦丽
# @Version: V 1.0
# @File : Job51.py
# @desc :
import hmac
import hashlib

"""
计算消息的 HMAC 值

:param message: 原始消息（字符串）
:param secret_key: 密钥（字符串）
:return: HMAC 十六进制字符串
"""
def hmac_calculator(message: str, secret_key: str) -> str:
    # 统一编码为字节
    key_bytes = secret_key.encode('utf-8')
    msg_bytes = message.encode('utf-8')
    # 获取哈希函数
    digest_mod = getattr(hashlib, 'sha256')
    # 创建 HMAC 实例并计算
    hmac_obj = hmac.new(key_bytes, msg_bytes, digest_mod)
    return hmac_obj.hexdigest()


par = '/wuhan-dhxjs/coB2RSM144UmUEZQ1nVDc.html'
key = 'abfc8f9dcf8c3f3d8aa294ac5f2cf2cc7767e5592590f39c3f503271dd68562b'
print(hmac_calculator(par, key))
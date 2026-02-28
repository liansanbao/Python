# _*_ coding: utf-8 _*_
# @Time : 2025/4/14 21:53
# @Author : 韦丽
# @Version: V 1.0
# @File : 爱拍网分析.py
# @desc :MD5加密

"""
目标网站：https://www.aipai.com/
需求：实现登录的逆向
登录接口url:
    https://www.aipai.com/login.php

    参数
        action: loginNew
        user: mv0/PgRhdXrva6Sx4ldrt/iNrQZpd5cFkiHh2WwvfMIOGVQU1yianVZMBHWnvnWFG+AUqe3IBvFPVzUsqX2LR8qZ40AB/KmkU6K405OjhrLZKjRqje7JrRsX50kCpqEKBys54FgREjkwKWO0qnmwYXvV/J8dgH1HjcK6aN+bJ3w=
        password: e10adc3949ba59abbe56e057f20f883e
        keeplogin: 1
        comouterTime: 1
        userNowTime: 1743509041

    逆向：
        user,password

定位：
    全局搜索：
        password:
    位置：
        data: {
                action: f,
                user: b,
                password: e.md5(q),
                keeplogin: a,
                comouterTime: a,
                userNowTime: g
            }

在线工具：https://www.toolhelper.cn/DigestAlgorithm/MD5

加密：
    e.md5(q)--经过分析，该密文是一个标准的md5
    工具加密：e10adc3949ba59abbe56e057f20f883e
    网站加密：e10adc3949ba59abbe56e057f20f883e
    自己加密：e10adc3949ba59abbe56e057f20f883e

     var l = m.encrypt(h);
     var b = l.replace(/\s|\n|\r\n/g, "+");

RSA加密：
    1.创建对象
    var m = new JSEncrypt();

    2.设置公钥
    m.setPublicKey(o);

    3.加密
    m.encrypt(h);


nodejs安装：https://nodejs.org/en/download
  **** cmd 已管理者身份运行
MD5 安装js加密库进行md5加密：npm install crypto-js
JSEncrypt 安装js加密库进行RSA加密：>npm install jsencrypt
"""

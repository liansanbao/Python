# _*_ coding: utf-8 _*_
# @Time : 2025/4/15 20:48
# @Author : 韦丽
# @Version: V 1.0
# @File : 抓取音频.py
# @desc :
"""
目标网站：https://www.qtfm.cn/channels/345534/
目的：采集不同节目单的音频集  初识js逆向

步骤：
    抓取多个音频的数据包做对比看参数变化情况  python生成加密参数值  发送请求

第一个音频：
https://audio.qtfm.cn/audiostream/redirect/345534/14334001?access_token=&device_id=MOBILESITE&qingting_id=&t=1740830648764&sign=b9f75510fab1c4a1fea24e414811e2ba

第二个音频：
https://audio.qtfm.cn/audiostream/redirect/345534/14334002?access_token=&device_id=MOBILESITE&qingting_id=&t=1740830912881&sign=ddd71ef682322cf90e8fbcee9d570580

第三个音频：
https://audio.qtfm.cn/audiostream/redirect/345534/14334003?access_token=&device_id=MOBILESITE&qingting_id=&t=1740830988633&sign=93984499777e6ed71250ff269e82705b
https://audio.qtfm.cn/audiostream/redirect/345534/14334001?access_token=&device_id=MOBILESITE&qingting_id=&t=1740835044725&sign=37abb362c4b7cc126d4e3ba3728238c7
参数变化 注意数字
345534  节目单主页id
14334001  单个节目id
t 变化了 1740830648764  时间戳 python生成
sign   u.a.createHmac("md5", "7l8CZ)SgZgM_bkrw").update(s).digest("hex").toString()  hmac md5

结合三个url发现  有4个参数会变化
有t和sign不能直接获取
需要到网页找t和sign的生成过程 生成对应的加密值拼接到url发送网络请求

学会快速定位加密的位置
access_token:
device_id: MOBILESITE
qingting_id:
t: 1740831540298
sign: 1183854fd96d1198d049a3a9bb4a7e12
小贴士：可以从写固定的参数名/参数值，去找加密的位置   打断点
Date.now()  python能生成  时间戳【从1970年1.1号0时0分0秒到此刻为止所经过的秒数】
"""

"""
345534  节目单主页id
14334001  单个节目id
t 变化了 1740830648764  时间戳 python生成
sign 
"""

# mainurl = 'https://www.qtfm.cn/channels/345534/'
import time

time1 = int(time.time() * 1000)
# 1740836246666
# 1740836150146
print(time1)
import hmac

msg = f'/audiostream/redirect/345534/14334001?access_token=&device_id=MOBILESITE&qingting_id=&t={time1}'

# "" + n + s + "&sign=" + u.a.createHmac("md5", "7l8CZ)SgZgM_bkrw").update(s).digest("hex").toString() 可以用Python hmac 库解决
object1 = hmac.new(key=b"7l8CZ)SgZgM_bkrw", digestmod='md5')
object1.update(msg.encode())
sign = object1.hexdigest()
print(sign)

audio_url = f'https://audio.qtfm.cn/audiostream/redirect/345534/14334001?access_token=&device_id=MOBILESITE&qingting_id=&t={time1}&sign={sign}'
#             https://audio.qtfm.cn/audiostream/redirect/345534/14334001?access_token=&device_id=MOBILESITE&qingting_id=&t=1744724125343&sign=b630ac80969d20b52098ffb9f3ef7817
#             https://audio.qtfm.cn/audiostream/redirect/345534/14334001?access_token=&device_id=MOBILESITE&qingting_id=&t=1744724125343&sign=b630ac80969d20b52098ffb9f3ef7817
#             https://audio.qtfm.cn/audiostream/redirect/345534/14334001?access_token=&device_id=MOBILESITE&qingting_id=&t=1744729123242&sign=4abbca520cf140405331c91a6ca1c4e0
print(audio_url)

# 37abb362c4b7cc126d4e3ba3728238c7
# 37abb362c4b7cc126d4e3ba3728238c7
# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/4/1 22:36
# @Author : 连三保
# @Version: V 1.0
# @File : MongoDBTest.py
# @desc :
import pymongo

# mongoDB连接
clint = pymongo.MongoClient(host='192.168.1.17', port=27017)
# 连接DB
db = clint["doubanSpider"]
# 集合
# db["douban"].drop()
col = db["douban"]

# col.insert_one({'name': '窃听风暴', 'score': '9.2'})
with clint.start_session() as session:
    session.start_transaction()
    try:
        col.update_one(
            {'电影名称': '肖申克的救赎2'},
            {'$set': {'电影名称':'肖申克的救赎6'}},
            upsert=True,
            session=session
        )
        session.commit_transaction()
    except Exception as e:
        session.abort_transaction()
        print(f'事务回滚： {str(e)}')

for item in col.find():
    print(item)


clint.close()
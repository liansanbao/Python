# _*_ coding: utf-8 _*_
# @Time : 2025/8/13 星期三 16:43
# @Author : 韦丽
# @Version: V 1.0
# @File : Mymodels.py
# @desc : 商品采集任务表

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ProductCollectTable(Base):
    __tablename__ = 'product_collect'

    id = Column(Integer, primary_key=True)
    platform = Column(String(20))
    product_type = Column(String(20))
    product_id = Column(String(50))
    product_url = Column(String(1024))
    status = Column(TINYINT, default='0')
    create_time = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    update_time = Column(DateTime, server_default='CURRENT_TIMESTAMP')

class ProductHistoryTable(Base):
    __tablename__ = 'product_history'

    id = Column(Integer, primary_key=True)
    platform = Column(String(20))
    product_type = Column(String(20))
    product_id = Column(String(50))
    product_url = Column(String(1024))
    status = Column(TINYINT, default='0')
    create_time = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    update_time = Column(DateTime, server_default='CURRENT_TIMESTAMP')

class SchedulerTable(Base):
    __tablename__ = 'scheduler'

    id = Column(Integer, primary_key=True)
    platform = Column(String(20))
    product_type = Column(String(20))
    product_type_url = Column(String(1024))
    status = Column(TINYINT, default='0')
    create_time = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    update_time = Column(DateTime, server_default='CURRENT_TIMESTAMP')


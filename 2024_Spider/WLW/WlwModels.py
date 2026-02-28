# _*_ coding: utf-8 _*_
# @Time : 2025/8/21 星期四 17:24
# @Author : 韦丽
# @Version: V 1.0
# @File : WlwModels.py
# @desc : 表结构

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GridistStockTable(Base):
    __tablename__ = 'GRIDIST_STOCK'

    CREATE_DATE = Column(DateTime, primary_key=True)
    F12 = Column(String(20), primary_key=True)
    F14 = Column(String(20))
    F2 = Column(String(20))
    F3 = Column(String(20))
    F4 = Column(String(20))
    F5 = Column(String(20))
    F6 = Column(String(20))
    F7 = Column(String(20))
    F8 = Column(String(20))
    F9 = Column(String(20))
    F10 = Column(String(20))
    F15 = Column(String(20))
    F16 = Column(String(20))
    F17 = Column(String(20))
    F18 = Column(String(20))
    F23 = Column(String(20))
    hybk = Column(String(45))


class AboardTable(Base):
    __tablename__ = 'ABOARD'

    CREATE_DATE = Column(DateTime, primary_key=True)
    F12 = Column(String(20), primary_key=True)
    F14 = Column(String(20))
    F2 = Column(String(20))
    F3 = Column(String(20))
    F4 = Column(String(20))
    F5 = Column(String(20))
    F6 = Column(String(20))
    F7 = Column(String(20))
    F8 = Column(String(20))
    F9 = Column(String(20))
    F10 = Column(String(20))
    F15 = Column(String(20))
    F16 = Column(String(20))
    F17 = Column(String(20))
    F18 = Column(String(20))
    F23 = Column(String(20))
    hybk = Column(String(45))
    status = Column(TINYINT, default='0')
    create_time = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    update_time = Column(DateTime, server_default='CURRENT_TIMESTAMP')

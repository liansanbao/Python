# _*_ coding: utf-8 _*_
# @Time : 2025/8/21 星期四 17:22
# @Author : 韦丽
# @Version: V 1.0
# @File : Wlw_repository.py
# @desc : WLw系统数据处理

import asyncio
import configparser
import datetime
import json
import os
from typing import Dict

import pandas
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, exists, update
from sqlalchemy.orm import sessionmaker
from WlwModels import AboardTable
from LoggingWLW import logger

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', 'utf-8')  # 确保config.ini文件存在

# 获取股票json文件配置
outJsonPath = config.get('JSONPATH', 'outJsonPath')

# 获取行业板块json文件配置
hybkJsonPath = config.get('JSONPATH', 'hybkJsonPath')

class WLWRepository:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(
            f"mysql+aiomysql://{db_url}",
            pool_recycle=3600,  # 1小时回收连接
            pool_pre_ping=True,  # 执行前检查连接有效性
            pool_timeout=30,  # 获取连接超时时间
            max_overflow=10  # 允许超出pool_size的连接数
        )
        self.async_session = sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        # 表字段名称
        self.gridistStock_header_list = []
        # 自定义pandas列标题
        self.customer_data_header = ['所属板块', '数量', '交易日期', '等级', '股票名称', '股票代码', '最新价', '涨跌幅', '涨跌额',
                                '成交量(手)', '成交额', '振幅', '换手率', '市盈率（动态）', '量比', '最高',
                                '最低', '今开', '昨收', '市净率']
        # 交易日
        self.now_date_list = [
                              '2029-10-20', '2029-10-21', '2029-10-22', '2029-10-23', '2029-10-24', '2029-10-27', '2029-10-28', '2029-10-29', '2029-10-30', '2029-10-31',
                              '2029-11-03', '2029-11-04', '2029-11-05', '2029-11-06', '2029-11-07', '2029-11-10', '2029-11-11', '2029-11-12', '2029-11-13', '2029-11-14',
                              '2029-11-17', '2029-11-18', '2029-11-19', '2029-11-20', '2029-11-21', '2029-11-24', '2029-11-25', '2029-11-26', '2029-11-27', '2029-11-28',
                              '2029-12-01', '2029-12-02', '2029-12-03', '2029-12-04', '2029-12-05', '2029-12-08', '2029-12-09', '2029-12-10', '2029-12-11', '2029-12-12',
                              '2029-12-13', '2029-12-14', '2029-12-15', '2029-12-16', '2029-12-17', '2029-12-20', '2029-12-21', '2029-12-22', '2029-12-23', '2029-12-24',
                              '2029-12-27', '2029-12-28', '2029-12-29', '2029-12-30', '2029-12-31',
                              '2030-10-06', '2030-10-07', '2030-10-08', '2030-10-09', '2030-10-10', '2030-10-13', '2030-10-14', '2030-10-15', '2030-10-16', '2030-10-17',
                              '2030-10-20', '2030-10-21', '2030-10-22', '2030-10-23', '2030-10-24', '2030-10-27', '2030-10-28', '2030-10-29', '2030-10-30', '2030-10-31',
                              '2030-11-03', '2030-11-04', '2030-11-05', '2030-11-06', '2030-11-07', '2030-11-10', '2030-11-11', '2030-11-12', '2030-11-13', '2030-11-14',
                              '2030-11-17', '2030-11-18', '2030-11-19', '2030-11-20', '2030-11-21', '2030-11-24', '2030-11-25', '2030-11-26', '2030-11-27', '2030-11-28',
                              '2030-12-01', '2030-12-02', '2030-12-03', '2030-12-04', '2030-12-05', '2030-12-08', '2030-12-09', '2030-12-10', '2030-12-11', '2030-12-12',
                              '2030-12-13', '2030-12-14', '2030-12-15', '2030-12-16', '2030-12-17', '2030-12-20', '2030-12-21', '2030-12-22', '2030-12-23', '2030-12-24',
                              '2030-12-27', '2030-12-28', '2030-12-29', '2030-12-30', '2030-12-31',
                              '2031-10-06', '2031-10-07', '2031-10-08', '2031-10-09', '2031-10-10', '2031-10-13', '2031-10-14', '2031-10-15', '2031-10-16', '2031-10-17',
                              '2031-10-20', '2031-10-21', '2031-10-22', '2031-10-23', '2031-10-24', '2031-10-27', '2031-10-28', '2031-10-29', '2031-10-30', '2031-10-31',
                              '2031-11-03', '2031-11-04', '2031-11-05', '2031-11-06', '2031-11-07', '2031-11-10', '2031-11-11', '2031-11-12', '2031-11-13', '2031-11-14',
                              '2031-11-17', '2031-11-18', '2031-11-19', '2031-11-20', '2031-11-21', '2031-11-24', '2031-11-25', '2031-11-26', '2031-11-27', '2031-11-28',
                              '2031-12-01', '2031-12-02', '2031-12-03', '2031-12-04', '2031-12-05', '2031-12-08', '2031-12-09', '2031-12-10', '2031-12-11', '2031-12-12',
                              '2031-12-13', '2031-12-14', '2031-12-15', '2031-12-16', '2031-12-17', '2031-12-20', '2031-12-21', '2031-12-22', '2031-12-23', '2031-12-24',
                              '2031-12-27', '2031-12-28', '2031-12-29', '2031-12-30', '2031-12-31',
                              '2032-10-06', '2032-10-07', '2032-10-08', '2032-10-09', '2032-10-10', '2032-10-13', '2032-10-14', '2032-10-15', '2032-10-16', '2032-10-17',
                              '2032-10-20', '2032-10-21', '2032-10-22', '2032-10-23', '2032-10-24', '2032-10-27', '2032-10-28', '2032-10-29', '2032-10-30', '2032-10-31',
                              '2032-11-03', '2032-11-04', '2032-11-05', '2032-11-06', '2032-11-07', '2032-11-10', '2032-11-11', '2032-11-12', '2032-11-13', '2032-11-14',
                              '2032-11-17', '2032-11-18', '2032-11-19', '2032-11-20', '2032-11-21', '2032-11-24', '2032-11-25', '2032-11-26', '2032-11-27', '2032-11-28',
                              '2032-12-01', '2032-12-02', '2032-12-03', '2032-12-04', '2032-12-05', '2032-12-08', '2032-12-09', '2032-12-10', '2032-12-11', '2032-12-12',
                              '2032-12-13', '2032-12-14', '2032-12-15', '2032-12-16', '2032-12-17', '2032-12-20', '2032-12-21', '2032-12-22', '2032-12-23', '2032-12-24',
                              '2032-12-27', '2032-12-28', '2032-12-29', '2032-12-30', '2032-12-31'
                              ]
        # 执行统计
        self.execTotal = 0

    async def get_aboard_exists(self, now_date) -> int:
        """获取数据列表"""
        async with self.async_session() as session:
            try:
                # 当日日期取得
                # now_date = datetime.date.today().strftime('%Y-%m-%d')
                result = await session.scalar(
                    select(
                        exists().where(
                            AboardTable.CREATE_DATE == now_date,
                            AboardTable.status == 0
                        )
                    )
                )
                print(f'检索条件：now_date = {now_date}')
                return result
            except Exception as e:
                logger.error(f"获取数据列表_exists失败: {str(e)}")
                raise

    # 将今日处理的数据状态更新成已处理
    async def update_aboard_status(self, now_date):
        async with self.async_session() as session:
            try:
                # 当日日期取得
                # now_date = datetime.date.today().strftime('%Y-%m-%d')
                status = 1
                await session.execute(
                    update(AboardTable)
                    .where(AboardTable.CREATE_DATE == now_date)
                    .values(status=status)
                )
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"中国A股大盘更新失败: {str(e)}")
                return False

    async def get_aboard_list(self, now_date, hybkFlag):
        """获取数据列表"""
        async with self.async_session() as session:
            async with session.begin():  # 使用事务上下文管理器
                try:
                    # 从中国A股大盘表中，取出指定交易日的数据。
                    # now_date = datetime.date.today().strftime('%Y-%m-%d')
                    result = await session.execute(
                        select(AboardTable)
                        .where(AboardTable.CREATE_DATE == now_date)
                        .limit(10000)
                        .with_for_update(skip_locked=True) # 跳过已被锁定的行
                    )

                    # 遍历检索结果，获取字段名称并将数据转成list类型保存
                    gridistStock_list = []
                    for row in result.scalars():
                        # 表字段名获取
                        if len(self.gridistStock_header_list) == 0:
                            self.gridistStock_header_list = self._row_to_header(row)

                        # 将表数据转换成list
                        gridistStock_list.append(self._row_to_list(row))

                    # 检索数据转pandas
                    pandas_list = pandas.DataFrame(data=gridistStock_list, columns=self.gridistStock_header_list)
                    # 按涨幅进行从小到大的排序和按所属板块分组
                    sort_f3_list = (
                        pandas_list
                        .sort_values('F3', ascending=False)  # 先按涨幅降序)
                        .groupby(by='hybk')  # 按所属板块分组
                    )
                    customer_data = []

                    # 行业板块数据保存至JSON文件
                    if hybkFlag:
                        hybkDict = {row['F12']: row['hybk'] for _, row in pandas_list.iterrows()}
                        await self.write_hybk_json(hybkDict)

                    # 按涨幅进行从小到大的排序和按所属板块分组后的数据
                    for hybk, groupbyRow in sort_f3_list:
                        # 板块个股数量
                        hybkNum = len(groupbyRow)
                        # 板块个股按股价从小到大进行排序
                        sortF2 = groupbyRow.sort_values(by=['F2'], ascending=False) # 最新价从大到小的排序
                        # 股价区间取得
                        levelF2Dict = await self.level_f2(sortF2)
                        # print(f'{hybk}_{hybkNum}_levelF2Dict: {levelF2Dict}')
                        # 所有股票交易日期、股票名称。。。
                        stockCreateDateDict = {row['F12']: row['CREATE_DATE'] for _, row in sortF2.iterrows()}  # 交易日期
                        stockF14Dict = {row['F12']: row['F14'] for _, row in sortF2.iterrows()} # 股票名称
                        stockF12Dict = {row['F12']: row['F12'] for _, row in sortF2.iterrows()}  # 股票代码
                        stockF2Dict = {row['F12']: row['F2'] for _, row in sortF2.iterrows()} # 最新价
                        stockF3Dict = {row['F12']: row['F3'] for _, row in sortF2.iterrows()} # 涨跌幅
                        stockF4Dict = {row['F12']: row['F4'] for _, row in sortF2.iterrows()} # 涨跌额
                        stockF5Dict = {row['F12']: row['F5'] for _, row in sortF2.iterrows()} # 成交量(手)
                        stockF6Dict = {row['F12']: row['F6'] for _, row in sortF2.iterrows()} # 成交额
                        stockF7Dict = {row['F12']: row['F7'] for _, row in sortF2.iterrows()} # 振幅
                        stockF8Dict = {row['F12']: row['F8'] for _, row in sortF2.iterrows()} # 换手率
                        stockF9Dict = {row['F12']: row['F9'] for _, row in sortF2.iterrows()} # 市盈率（动态）
                        stockF10Dict = {row['F12']: row['F10'] for _, row in sortF2.iterrows()} # 量比
                        stockF15Dict = {row['F12']: row['F15'] for _, row in sortF2.iterrows()} # 最高
                        stockF16Dict = {row['F12']: row['F16'] for _, row in sortF2.iterrows()} # 最低
                        stockF17Dict = {row['F12']: row['F17'] for _, row in sortF2.iterrows()} # 今开
                        stockF18Dict = {row['F12']: row['F18'] for _, row in sortF2.iterrows()} # 昨收
                        stockF23Dict = {row['F12']: row['F23'] for _, row in sortF2.iterrows()} # 市净率

                        customer_data.append([
                            hybk, hybkNum, stockCreateDateDict, levelF2Dict, stockF14Dict, stockF12Dict, stockF2Dict, stockF3Dict, stockF4Dict, stockF5Dict,
                            stockF6Dict, stockF7Dict, stockF8Dict, stockF9Dict, stockF10Dict, stockF15Dict,
                            stockF16Dict, stockF17Dict, stockF18Dict, stockF23Dict
                                              ])
                    # 以行业板块统计之后的数据
                    customer_pandas = pandas.DataFrame(data=customer_data, columns=self.customer_data_header).sort_values(by='数量', ascending=False)
                    # print(f'customer_pandas: {customer_pandas}')
                    customer_level_dict = {}

                    # 从配置文件中读取指定的检索股价区间
                    levels = config.get('LEVELPRICE', 'levels')
                    levels_list = json.loads(levels)

                    reportDict = {}
                    # 从统计完了的数据中，检索出指定股票价格区间的股票
                    for indexNo in customer_pandas.index:
                        # 结果中股价区间取得
                        level = dict(customer_pandas.loc[indexNo, '等级'])
                        # 指定的股价区间
                        for leve in levels_list:
                            # 指定的区间是否在结果中的区间里面
                            if leve in level.keys():
                                # 存在，获取区间中所有股票代码
                                stockNos = str(level[leve]).split(',')
                                # 取出区间中所有股票数据
                                customer_level_list = await self.customerLevel(customer_pandas, indexNo, stockNos, reportDict)
                                # 将取出的结果做保存
                                if len(customer_level_dict) == 0:
                                    customer_level_dict[leve] = customer_level_list
                                else:
                                    if leve in customer_level_dict.keys():
                                        level_list = []
                                        level_list.extend(customer_level_dict[leve])
                                        level_list.extend(customer_level_list)
                                        customer_level_dict[leve] = level_list
                                    else:
                                        customer_level_dict[leve] = customer_level_list
                    # 打印满足检索区间的股票数量
                    for leve in customer_level_dict.keys():
                        print(f'{now_date}/{leve}: {len(customer_level_dict[leve])}')

                    # 报告
                    for key, value in reportDict.items():
                        print(f"{key} : {value}")
                    self.execTotal += 1
                except Exception as e:
                    logger.error(f"获取数据列表查询失败: {str(e)}")
                    # 事务会自动回滚
                    raise

    async def printData(self, customer_level):
        for row in customer_level:
            print(row)

    # 股价区间以行业来统计
    async def customerLevel(self, customer_pandas, indexNo, stockNos, reportDict):
        customer_level = []
        # 板块名称 单一
        sshy = customer_pandas.loc[indexNo, '所属板块']
        # 所属行业板块的股票数
        sshyNum = customer_pandas.loc[indexNo, '数量']
        # 所有股票的交易日期、股票名称、最新价、涨跌幅、涨跌额、成交量、成交额、振幅、换手率。。。
        stockCreateDateDict = customer_pandas.loc[indexNo, '交易日期']
        stockF14Dict = customer_pandas.loc[indexNo, '股票名称']
        stockF2Dict = customer_pandas.loc[indexNo, '最新价']
        stockF3Dict = customer_pandas.loc[indexNo, '涨跌幅']
        stockF4Dict = customer_pandas.loc[indexNo, '涨跌额']
        stockF5Dict = customer_pandas.loc[indexNo, '成交量(手)']
        stockF6Dict = customer_pandas.loc[indexNo, '成交额']
        stockF7Dict = customer_pandas.loc[indexNo, '振幅']
        stockF8Dict = customer_pandas.loc[indexNo, '换手率']
        stockF9Dict = customer_pandas.loc[indexNo, '市盈率（动态）']
        stockF10Dict = customer_pandas.loc[indexNo, '量比']
        stockF15Dict = customer_pandas.loc[indexNo, '最高']
        stockF16Dict = customer_pandas.loc[indexNo, '最低']
        stockF17Dict = customer_pandas.loc[indexNo, '今开']
        stockF18Dict = customer_pandas.loc[indexNo, '昨收']
        stockF23Dict = customer_pandas.loc[indexNo, '市净率']

        for stock in stockNos:
            stockInfoDict = {'所属板块': sshy, '数量': sshyNum, '交易日期': stockCreateDateDict[stock], '股票名称': stockF14Dict[stock], '股票代码': stock, '最新价': stockF2Dict[stock],
                                    '涨跌幅': stockF3Dict[stock], '涨跌额': stockF4Dict[stock], '成交量(手)': stockF5Dict[stock],
                                    '成交额': stockF6Dict[stock], '振幅': stockF7Dict[stock], '换手率': stockF8Dict[stock],
                                    '市盈率（动态）': stockF9Dict[stock], '量比': stockF10Dict[stock], '最高': stockF15Dict[stock],
                                    '最低': stockF16Dict[stock], '今开': stockF17Dict[stock], '昨收': stockF18Dict[stock], '市净率': stockF23Dict[stock]}
            customer_level.append(stockInfoDict)
            # M5、M10、M20、M60、M120、M250值计算
            await self.editMOfStock(stockInfoDict, reportDict)

        return customer_level

    # M5、M10、M20、M60、M120、M250值计算
    async def editMOfStock(self, stockInfoDict, reportDict):
        # 测试用
        now_date = stockInfoDict['交易日期']
        # if len(self.now_date_list) > self.execTotal:
        #     now_date = self.now_date_list[self.execTotal]
        # else:
        #     # 测试数据没有了，结束处理
        #     return
        # Json文件夹处理
        OUTPUT_FILE_PATH = outJsonPath
        if not os.path.exists(OUTPUT_FILE_PATH):
            # 不存在时，创建
            os.makedirs(OUTPUT_FILE_PATH)

        # Json文件名称
        stockJsonFileName = f"{OUTPUT_FILE_PATH}{stockInfoDict['所属板块']}_{stockInfoDict['股票代码']}_{stockInfoDict['股票名称']}.json"
        # 存在，读取
        logger.info(f'stockJsonFileName: {stockJsonFileName}')
        print(f'stockJsonFileName: {stockJsonFileName}')

        # 判断股票Json文件是否存在
        if not os.path.exists(stockJsonFileName):
            # 不存在，创建Json文件
            with open(stockJsonFileName, 'w', encoding='utf-8') as writer:
                try:
                    # M5
                    json_data = json.dumps({'M5': {str(stockInfoDict['交易日期']): [str(stockInfoDict['交易日期']), str(stockInfoDict['最新价']),
                                                 str(stockInfoDict['涨跌幅']), str(stockInfoDict['成交量(手)']),
                                                 str(stockInfoDict['换手率']), str(stockInfoDict['最高']),
                                                 str(stockInfoDict['最低']), str(stockInfoDict['今开']), '', '',
                                                 '', '', '', '']}}, ensure_ascii=False) + '\n'
                    writer.write(json_data)
                    # M10
                    json_data = json.dumps({'M10': None}, ensure_ascii=False) + '\n'
                    writer.write(json_data)
                    # M20
                    json_data = json.dumps({'M20': None}, ensure_ascii=False) + '\n'
                    writer.write(json_data)
                    # M60
                    json_data = json.dumps({'M60': None}, ensure_ascii=False) + '\n'
                    writer.write(json_data)
                    # M120
                    json_data = json.dumps({'M120': None}, ensure_ascii=False) + '\n'
                    writer.write(json_data)
                    # M250
                    json_data = json.dumps({'M250': None}, ensure_ascii=False) + '\n'
                    writer.write(json_data)
                    # 最低值
                    json_data = json.dumps({'SminVal': None}, ensure_ascii=False) + '\n'
                    writer.write(json_data)
                    # N个交易日(当出现最低值时，下一个交易日开始统计)
                    json_data = json.dumps({'WhichSale': None}, ensure_ascii=False) + '\n'
                    writer.write(json_data)
                    # 投资报告内容
                    json_data = json.dumps({'ReportContent': None}, ensure_ascii=False) + '\n'
                    writer.write(json_data)
                except Exception as e:
                    logger.error(f"创建Json文件{stockJsonFileName}失败: {e}\n")
        else:
            result = []
            # Json文件内容读取
            with open(stockJsonFileName, 'r', encoding='utf-8') as reader:
                for line in reader:
                    line = line.strip()
                    if line:  # 跳过空行
                        try:
                            # 替换中文引号或单引号为英文双引号
                            line = line.replace("'", "\"").replace("“", "\"").replace("”", "\"")
                            data = json.loads(line)  # 直接解析为字典，无需再调用dict()
                            result.append(data)
                        except Exception as e:
                            logger.error(f"Json文件内容读取失败: {e}\n问题行内容: {line}")
            # 计算均线值并保存到Json文件中
            with open(stockJsonFileName, 'w', encoding='utf-8') as w:
                try:
                    m5dict = None
                    m5MinSaleInfo = None
                    total5 = 0.0
                    m10dict = None
                    m10MinSaleInfo = None
                    total10 = 0.0
                    m20dict = None
                    m20MinSaleInfo = None
                    total20 = 0.0
                    m60dict = None
                    m60MinSaleInfo = None
                    total60 = 0.0
                    m120dict = None
                    m120MinSaleInfo = None
                    total120 = 0.0
                    m250dict = None

                    mMinValueDict = {}
                    sminValList = []
                    whichSaleList = []

                    reportContent = []

                    # M系列值计算
                    for item in result:
                        itemKeys = dict(item).keys()
                        # M5
                        if 'M5' in itemKeys:
                            m5dict = dict(item['M5']) if item['M5'] else {}
                            # 将今日信息保存
                            m5dict[str(now_date)] = [str(now_date), str(stockInfoDict['最新价']),
                                                     str(stockInfoDict['涨跌幅']), str(stockInfoDict['成交量(手)']),
                                                     str(stockInfoDict['换手率']), str(stockInfoDict['最高']),
                                                     str(stockInfoDict['最低']), str(stockInfoDict['今开']), '', '',
                                                     '', '', '', '']

                            if len(m5dict) == 6:
                                # M5中筛选交易日最低值
                                mMinValueDict['M05'] = await self.stockMinOfSale(m5dict, 6)
                                # 删除最小交易的数据
                                min5Sale = min(m5dict.keys())
                                m5MinSaleInfo = m5dict[min5Sale]
                                m5dict.pop(min5Sale)
                                # 统计第2个元素的总和
                                total5 = sum(float(data[1]) for data in m5dict.values())
                                m5dict[str(now_date)][8] = f'{round((total5 / 5), 2)}'
                                logger.info(f'M5情报: {m5dict[str(now_date)]}, 最小交易日: {min5Sale}, M5总和: {total5}')
                                print(f'M5情报: {m5dict[str(now_date)]}, 最小交易日: {min5Sale}, M5总和: {total5}')

                        # M10
                        elif 'M10' in itemKeys:
                            m10dict = dict(item['M10']) if item['M10'] else {}
                            # 将今日信息保存
                            if m5MinSaleInfo:
                                m10dict[m5MinSaleInfo[0]] = m5MinSaleInfo

                                if len(m10dict) == 6:
                                    # M10中筛选交易日最低值
                                    mMinValueDict['M10'] = await self.stockMinOfSale(m10dict, 6)
                                    # 删除最小交易的数据
                                    min10Sale = min(m10dict.keys())
                                    m10MinSaleInfo = m10dict[min10Sale]
                                    m10dict.pop(min10Sale)
                                    # 统计第2个元素的总和
                                    total10 = sum(float(data[1]) for data in m10dict.values()) + total5
                                    m5dict[str(now_date)][9] = f'{round((total10 / 10), 2)}'
                                    logger.info(
                                        f'M10情报: {m5dict[str(now_date)]}, 最小交易日: {min10Sale}, M10总和: {total10}')
                                    print(
                                        f'M10情报: {m5dict[str(now_date)]}, 最小交易日: {min10Sale}, M10总和: {total10}')

                        # M20
                        elif 'M20' in itemKeys:
                            m20dict = dict(item['M20']) if item['M20'] else {}
                            # 将今日信息保存
                            if m10MinSaleInfo:
                                m20dict[m10MinSaleInfo[0]] = m10MinSaleInfo

                                if len(m20dict) == 11:
                                    # M20中筛选交易日最低值
                                    mMinValueDict['M20'] = await self.stockMinOfSale(m20dict, 6)
                                    # 删除最小交易的数据
                                    min20Sale = min(m20dict.keys())
                                    m20MinSaleInfo = m20dict[min20Sale]
                                    m20dict.pop(min20Sale)
                                    # 统计第2个元素的总和
                                    total20 = sum(float(data[1]) for data in m20dict.values()) + total10
                                    m5dict[str(now_date)][10] = f'{round((total20 / 20), 2)}'
                                    logger.info(
                                        f'M20情报: {m5dict[str(now_date)]}, 最小交易日: {min20Sale}, M20总和: {total20}')
                                    print(
                                        f'M20情报: {m5dict[str(now_date)]}, 最小交易日: {min20Sale}, M20总和: {total20}')

                        # M60
                        elif 'M60' in itemKeys:
                            m60dict = dict(item['M60']) if item['M60'] else {}
                            # 将今日信息保存
                            if m20MinSaleInfo:
                                m60dict[m20MinSaleInfo[0]] = m20MinSaleInfo

                                if len(m60dict) == 41:
                                    # 删除最小交易的数据
                                    min60Sale = min(m60dict.keys())
                                    m60MinSaleInfo = m60dict[min60Sale]
                                    m60dict.pop(min60Sale)
                                    # 统计第2个元素的总和
                                    total60 = sum(float(data[1]) for data in m60dict.values()) + total20
                                    m5dict[str(now_date)][11] = f'{round((total60 / 60), 2)}'
                                    logger.info(
                                        f'M60情报: {m5dict[str(now_date)]}, 最小交易日: {min60Sale}, M60总和: {total60}')
                                    print(
                                        f'M60情报: {m5dict[str(now_date)]}, 最小交易日: {min60Sale}, M60总和: {total60}')

                        # M120
                        elif 'M120' in itemKeys:
                            m120dict = dict(item['M120']) if item['M120'] else {}
                            # 将今日信息保存
                            if m60MinSaleInfo:
                                m120dict[m60MinSaleInfo[0]] = m60MinSaleInfo

                                if len(m120dict) == 61:
                                    # 删除最小交易的数据
                                    min120Sale = min(m120dict.keys())
                                    m120MinSaleInfo = m120dict[min120Sale]
                                    m120dict.pop(min120Sale)
                                    # 统计第2个元素的总和
                                    total120 = sum(float(data[1]) for data in m120dict.values()) + total60
                                    m5dict[str(now_date)][12] = f'{round((total120 / 120), 2)}'
                                    logger.info(
                                        f'M120情报: {m5dict[str(now_date)]}, 最小交易日: {min120Sale}, M120总和: {total120}')
                                    print(
                                        f'M120情报: {m5dict[str(now_date)]}, 最小交易日: {min120Sale}, M120总和: {total120}')

                        # M250
                        elif 'M250' in itemKeys:
                            m250dict = dict(item['M250']) if item['M250'] else {}
                            # 将今日信息保存
                            if m120MinSaleInfo:
                                m250dict[m120MinSaleInfo[0]] = m120MinSaleInfo

                                if len(m250dict) == 131:
                                    # 删除最小交易的数据
                                    min250Sale = min(m250dict.keys())
                                    m250dict.pop(min250Sale)
                                    # 统计第2个元素的总和
                                    total250 = sum(float(data[1]) for data in m250dict.values()) + total120
                                    m5dict[str(now_date)][13] = f'{round((total250 / 250), 2)}'
                                    logger.info(
                                        f'M250情报: {m5dict[str(now_date)]}, 最小交易日: {min250Sale}, M250总和: {total250}')
                                    print(
                                        f'M250情报: {m5dict[str(now_date)]}, 最小交易日: {min250Sale}, M250总和: {total250}')

                        # SminVal最低值
                        elif 'SminVal' in itemKeys:
                            try:
                                sminValList = list(item['SminVal']) if item['SminVal'] else []
                                print(f'mMinValueDict: {mMinValueDict}, sminValList: {sminValList}')
                                if len(mMinValueDict) > 0:
                                    sortReslt = await self.stockMinOfSale(mMinValueDict, 1)
                                    print(f'sortReslt: {sortReslt}')
                                    # 不是M5, 跳过下面的处理
                                    if sortReslt[0] != 'M5':
                                        continue
                                    # sminValList = mMinValueDict[sortReslt[0]]
                                    if (len(sminValList) == 0):
                                        sminValList = mMinValueDict[sortReslt[0]]
                                    else:
                                        if float(sminValList[1]) > float(sortReslt[1]):
                                            sminValList = mMinValueDict[sortReslt[0]]
                            except Exception as e:
                                print(f'SminVal: {str(e)}')

                        # N个交易日保存
                        elif 'WhichSale' in itemKeys and len(sminValList) > 0:
                            WhichSale = []
                            WhichSale.extend([sale for sale in m5dict.keys()])
                            WhichSale.extend([sale for sale in m10dict.keys()])
                            WhichSale.extend([sale for sale in m20dict.keys()])
                            WhichSale.extend([sale for sale in m60dict.keys()])
                            sort_data = await self.sort_sale_desc(WhichSale)
                            index = -1
                            try:
                                print(f'sort_data: {sort_data}')
                                index = sort_data.index(sminValList[0])
                            except Exception as e:
                                print(f'ERROR: {str(e)}')
                            whichSaleList = [f'第{index}个交易日']
                            print(f'whichSaleList: {whichSaleList}')

                    # 均线状态判定
                    reportContent = await self.MStatus(m5dict[str(now_date)])
                    # 将M5信息保存
                    await self.writerJsonDict(m5dict, 'M5', w)
                    # 将M10信息保存
                    await self.writerJsonDict(m10dict, 'M10', w)
                    # 将M20信息保存
                    await self.writerJsonDict(m20dict, 'M20', w)
                    # 将M60信息保存
                    await self.writerJsonDict(m60dict, 'M60', w)
                    # 将M120信息保存
                    await self.writerJsonDict(m120dict, 'M120', w)
                    # 将M250信息保存
                    await self.writerJsonDict(m250dict, 'M250', w)
                    # 最低值保存
                    await self.writerJsonList(sminValList, 'SminVal', w)
                    # N个交易日保存
                    await self.writerJsonList(whichSaleList, 'WhichSale', w)
                    # 投资报告内容
                    await self.writerJsonList(reportContent, 'ReportContent', w)

                    reportDict[stockInfoDict['股票代码']] = reportContent
                except Exception as e:
                    logger.error(f"保存Json文件{stockJsonFileName}失败: {e}\n")

    # Json文件保存
    async def writerJsonList(self, mList, key, w):
        json_data = json.dumps({key: mList}, ensure_ascii=False) + '\n'
        w.write(json_data)

    # Json文件保存
    async def writerJsonDict(self, mdict, key, w):
        if mdict != None and len(mdict) > 1:
            mdict = {key: mdict[key] for key in sorted(mdict.keys())}

        json_data = json.dumps({key: mdict}, ensure_ascii=False) + '\n'
        w.write(json_data)

    # 行业板块名称保存至Json文件
    async def write_hybk_json(self, result: dict = {}):
        # hybk.json文件
        self.gridistJsonFile = f'{hybkJsonPath}hybk.json'
        try:
            with open(self.gridistJsonFile, 'w', encoding='utf-8') as w:
                json_data = json.dumps(result, ensure_ascii=False) + '\n'
                w.write(json_data)
        except (FileNotFoundError, json.JSONDecodeError) as ex:
            self.logger.info(f'{self.gridistJsonFile} 写入失败: {str(ex)}')

    # 均线状态判定
    async def MStatus(self, mdict):
        reportContent = []
        try:
            if mdict:
                # 收盘价格
                m = await self.str_to_float(mdict[1])
                # m5
                m5 = await self.str_to_float(mdict[8])
                # m10
                m10 = await self.str_to_float(mdict[9])
                # m20
                m20 = await self.str_to_float(mdict[10])
                # 最高价
                higherM = await self.str_to_float(mdict[5])
                print(f'm: {m}, m5: {m5}, m10: {m10}, m20: {m20}, higherM: {higherM}')
                # 三均线小于m时
                if m > max(m5, m10, m20):
                    if 0.3 > max(abs(m5 - m10), abs(m10 - m20), abs(m5 - m20)):
                        content = '5日均线、10日均线和20日均线呈互相缠绕形状。'
                        reportContent.append(content)
                        print(content)

                # 当日最高价格 - 收盘价 / 收盘价 保留三位小数 且大于 0.04 的情况
                zhangfuM = round((higherM - m) / m, 3)
                if zhangfuM > 0.04:
                    content = f"{mdict[0]}交易日涨幅为{zhangfuM * 100}%，值得关注和投资。"
                    reportContent.append(content)
                    print(content)

                return reportContent
        except Exception as e:
            print(f"MStatus ERROR: {str(e)}")
            return reportContent

    # str转float
    async def str_to_float(self, str) -> float:
        result = 0
        try:
            result = float(str)
        except Exception as e:
            pass
        return result

    # 交易日期排序
    async def sort_sale_desc(self, data_list):
        """
            对日期列表进行降序排序（支持字符串和datetime对象混合）
            参数：
                date_list: 包含日期字符串（YYYY-MM-DD格式）或datetime对象的列表
            返回：
                排序后的新列表（从最新到最旧）
            """

        def convert_to_datetime(d):
            return d if isinstance(d, datetime) else datetime.datetime.strptime(d, "%Y-%m-%d")

        sorted_data = sorted([convert_to_datetime(d) for d in data_list], reverse=True)
        return [datetime.datetime(d).strftime("%Y-%m-%d") if isinstance(d, datetime) else d for d in sorted_data]

    # 最低值及交易日取得
    async def stockMinOfSale(self, mdict, indexNo):
        # 获取交易日最低值
        mdictMinSaleValue = min(float(data[indexNo]) for data in mdict.values())

        # 获取对应交易日
        min_date = min(
            (date for date, data in mdict.items() if float(data[indexNo]) == mdictMinSaleValue),
            key=lambda x: mdict[x][0]
        )
        return [min_date, mdictMinSaleValue]

    # 股价区间判定
    async def level_f2(self, sortF2):
        result = {}
        for _, row in sortF2.iterrows():
            f2 = float(row["F2"])
            if f2 > 0.0 and f2 <= 5.0:
                result['0-5'] = await self.editF12('0-5', result, row)
            elif f2 > 5.0 and f2 <= 10.0:
                result['5-10'] = await self.editF12('5-10', result, row)
            elif f2 > 10.0 and f2 <= 15.0:
                result['10-15'] = await self.editF12('10-15', result, row)
            elif f2 > 15.0 and f2 <= 20.0:
                result['15-20'] = await self.editF12('15-20', result, row)
            elif f2 > 20.0 and f2 <= 25.0:
                result['20-25'] = await self.editF12('20-25', result, row)
            elif f2 > 25.0 and f2 <= 30.0:
                result['25-30'] = await self.editF12('25-30', result, row)
            elif f2 > 30.0 and f2 <= 40.0:
                result['30-40'] = await self.editF12('30-40', result, row)
            elif f2 > 40.0 and f2 <= 50.0:
                result['40-50'] = await self.editF12('40-50', result, row)
            elif f2 > 50.0 and f2 <= 60.0:
                result['50-60'] = await self.editF12('50-60', result, row)
            elif f2 > 60.0 and f2 <= 70.0:
                result['60-70'] = await self.editF12('60-70', result, row)
            elif f2 > 70.0 and f2 <= 80.0:
                result['70-80'] = await self.editF12('70-80', result, row)
            elif f2 > 80.0 and f2 <= 90.0:
                result['80-90'] = await self.editF12('80-90', result, row)
            elif f2 > 90.0 and f2 <= 100.0:
                result['90-100'] = await self.editF12('90-100', result, row)
            elif f2 > 100.0 and f2 <= 200.0:
                result['100-200'] = await self.editF12('100-200', result, row)
            elif f2 > 200.0 and f2 <= 300.0:
                result['200-300'] = await self.editF12('200-300', result, row)
            elif f2 > 300.0 and f2 <= 400.0:
                result['300-400'] = await self.editF12('300-400', result, row)
            elif f2 > 400.0 and f2 <= 500.0:
                result['400-500'] = await self.editF12('400-500', result, row)
            elif f2 > 500.0 and f2 <= 600.0:
                result['500-600'] = await self.editF12('500-600', result, row)
            elif f2 > 600.0 and f2 <= 700.0:
                result['600-700'] = await self.editF12('600-700', result, row)
            elif f2 > 700.0 and f2 <= 800.0:
                result['700-800'] = await self.editF12('700-800', result, row)
            elif f2 > 800.0 and f2 <= 900.0:
                result['800-900'] = await self.editF12('800-900', result, row)
            elif f2 > 900.0 and f2 <= 1000.0:
                result['900-1000'] = await self.editF12('900-1000', result, row)
            elif f2 > 1000.0 and f2 <= 1500.0:
                result['1000-1500'] = await self.editF12('1000-1500', result, row)
            elif f2 > 1500.0 and f2 <= 2000.0:
                result['1500-2000'] = await self.editF12('1500-2000', result, row)
            elif f2 > 2000.0:
                result['2000UP'] = await self.editF12('2000UP', result, row)

        return result

    # 以区间归纳股票代码
    async def editF12(self, key, result, row):
        if key in result.keys():
            return result[key] + ',' + row["F12"]
        else:
            return row["F12"]

    # 表字段名获取
    def _row_to_header(self, row) -> list:
        """表字段名"""
        colums = [c.name for c in row.__table__.columns]
        logger.info(f'表名字段：{colums}')
        return colums

    def _row_to_list(self, row) -> list:
        """list"""
        return [getattr(row, c.name) for c in row.__table__.columns]

    def _row_to_dict(self, row) -> Dict:
        """ORM对象转字典"""
        return {c.name: getattr(row, c.name) for c in row.__table__.columns}

async def main():
    repo = WLWRepository("root:Lian+2040@192.168.1.13:3306/taobao")
    # urls = await repo.get_urls('2')
    # urls[0].pop('id')
    # await repo.insert_product(urls[0])
    # print(urls[0])
    # await repo.update_status(urls[0]['id'], '2')

if __name__ == '__main__':
    asyncio.run(main())

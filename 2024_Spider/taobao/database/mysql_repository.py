# _*_ coding: utf-8 _*_
# @Time : 2025/8/13 星期三 16:37
# @Author : 韦丽
# @Version: V 1.0
# @File : mysql_repository.py
# @desc : MySQL option
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, update, delete, exists
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Optional
from .Mymodels import ProductCollectTable, ProductHistoryTable, SchedulerTable
import logging

class MySQLRepository:
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

    async def get_product_exists(self, paraStatus) -> int:
        """获取待处理的URL列表"""
        async with self.async_session() as session:
            try:
                result = await session.scalar(
                    select(
                        exists().where(
                            ProductCollectTable.status.in_(paraStatus)
                        )
                    )
                )
                return result
            except Exception as e:
                logging.error(f"商品采集表L_exists失败: {str(e)}")
                raise

    async def get_product_list(self, paraStatus, crawl):
        """获取待处理的URL列表"""
        async with self.async_session() as session:
            async with session.begin():  # 使用事务上下文管理器
                try:
                    result = await session.execute(
                        select(ProductCollectTable)
                        .where(ProductCollectTable.status.in_(paraStatus))
                        .limit(100)
                        .with_for_update(skip_locked=True) # 跳过已被锁定的行
                    )
                    product_list = [self._row_to_dict(row) for row in result.scalars()]

                    # 统计浏览器打开的窗口次数
                    browserTotal = 0
                    success_ids = []
                    failed_updates = []

                    # 数据采集
                    for product in product_list:
                        print(f'正在处理: {product["product_url"]}')
                        # 窗口
                        browserTotal += 1

                        try:
                            # 代理IP取得
                            # proxy = await proxy_manager.get_proxy()
                            # playwright 淘宝活动数据采集
                            if (await crawl.tpa_exec(product['product_url'], None)):
                                success_ids.append(product['id'])
                        except Exception as ex:
                            print(f'活动数据采集失败： {str(ex)}')
                            failed_updates.append({
                                'id': product['id'],
                                'status': '1'
                            })

                        # 统计浏览器打开的窗口次数 = 100时
                        # if browserTotal == 10:
                        #     print(f'reboot : {browserTotal}')
                        #     await crawl.reboot()
                        #     browserTotal = 0

                    # 批量更新失败记录
                    if failed_updates:
                        await session.execute(
                            update(ProductCollectTable),
                            failed_updates
                        )

                    # 批量处理成功记录
                    if success_ids:
                        # 批量删除原记录
                        await session.execute(
                            delete(ProductCollectTable)
                            .where(ProductCollectTable.id.in_(success_ids))
                        )

                        # 批量插入任务履历表
                        history_data = [{
                            **{k: v for k, v in p.items() if k != 'id'},
                            'status': '2'
                        } for p in product_list if p['id'] in success_ids]

                        # history_data: [{'platform': '淘宝', 'product_type': '', 'product_id': '250814009', 'product_url': 'https://detail.tmall.com/item.htm?ali_refid=a3_430582_1006%3A1232930108%3AN%3AKV%2Fu6HT5hnIF5S%2F00x%2BYSQ%3D%3D%3A852f38a485c4eb92cecb42ce4eef118d&ali_trackid=162_852f38a485c4eb92cecb42ce4eef118d&id=595733677157&mi_id=nq5O6PNbc6XUDEJyaL5YWORylfiwnCdNXej3XsZTI8XVaz_eHsH9Efd0Xtt_p5EMWkVR-aPoi2ZBEgk_xm86EtOtABbuQIF4iNjKWqXa4QE&mm_sceneid=7_0_450650167_0&priceTId=215041c017550393941591411e1371&skuId=4566066668610&spm=a21n57.1.hoverItem.1&utparam=%7B%22aplus_abtest%22%3A%226e18d7ad0d17624698dde0503577ce6a%22%7D&xxc=ad_ztc', 'status': '2', 'create_time': datetime.datetime(2025, 8, 13, 20, 21, 42), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814008', 'product_url': 'https://item.taobao.com/item.htm?ali_refid=a3_420434_1006%3A1120844747%3AN%3A2wPJAdhNUSw1l3HjVQ7h0JRxhEj1d6Rz%3Acf0563f6cbc0174dccc338aa68488396&ali_trackid=1_cf0563f6cbc0174dccc338aa68488396&id=595563083409&mi_id=0000J7mfPM_M7vjOkk4-mmyLQfqc3fMzaJBWlszcyki8FOw&mm_sceneid=1_0_110176333_0&priceTId=2150452417551718754506782e1c9e&skuId=4300189139208&spm=a21n57.1.hoverItem.1&utparam=%7B%22aplus_abtest%22%3A%229ce507475b63e2442f82eb7e3a179542%22%7D&xxc=ad_ztc', 'status': '2', 'create_time': datetime.datetime(2025, 8, 13, 20, 26, 46), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814007', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=923376253416&mi_id=0000SFY96peiwP8g17BnYmwYe_xZXjlUbsm99vRnFNqfgQ4&ns=1&priceTId=2150452417551718754506782e1c9e&skuId=5799893164668&spm=a21n57.1.hoverItem.13&utparam=%7B%22aplus_abtest%22%3A%2265dc7686cbcb56bc22c2c3b246f28f32%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 47, 42), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814001', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=568384314550&mi_id=0000q9ry4YHIAjOLT6cWxzl4MunC04BRYMlMUqs5XR2M8Uo&ns=1&priceTId=2150452417551718754506782e1c9e&skuId=3798203962050&spm=a21n57.1.hoverItem.36&utparam=%7B%22aplus_abtest%22%3A%226e95f7f00fb459bf4a8a446d57c1acfa%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 48, 16), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814002', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=574937922347&mi_id=_nEngL4dA9xFA1UrEvJc6lY46TrYQtNYPdZfTo6UFep6rZJAHbGbVC-Etee1nSwa6EpbH5xkBCsO0byHn1GCykxVxNWqXilY2BHrWhV9jkg&ns=1&priceTId=2150452417551721136233444e1c9e&skuId=4477821112457&spm=a21n57.1.hoverItem.17&utparam=%7B%22aplus_abtest%22%3A%2272d993ec99628dd4f9c7d71d5e2b65ff%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814003', 'product_url': 'https://detail.tmall.com/item.htm?ali_refid=a3_420434_1006%3A1316820001%3AH%3A089sl6cpAznrKKioK474vw%3D%3D%3A0ef207e99057446973f2acaba2613b77&ali_trackid=282_0ef207e99057446973f2acaba2613b77&id=811150604986&mi_id=JXK7V4PqOMcFImyD3PUEZTXYTbghtE-cZhnqsYaJ3zDfH4RfbYreU2eFPxPw_YRA_XscAK8FksGG-rO0M2umQe1_k9NuhLlsav4LSuuSLjY&mm_sceneid=1_0_1217370115_0&priceTId=2150452417551721524205679e1c9e&skuId=6064712662241&spm=a21n57.1.hoverItem.2&utparam=%7B%22aplus_abtest%22%3A%2290557614f25b34909f9fd13ebbc327bf%22%7D&xxc=ad_ztc', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814004', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=953215308764&mi_id=86N_r3_8skp9TNO3F6HHSN6TW6lN5YfTzlFXyBdkK3xASYJ5l-UU-1l6RO6_7f98f_7B-hJTWjD74TNOQATm_ldM8cvQJQxB5iUwx9AJZzw&ns=1&priceTId=2150452417551721524205679e1c9e&skuId=5871582625770&spm=a21n57.1.hoverItem.48&utparam=%7B%22aplus_abtest%22%3A%229ea476d53d5863a00c808a4e0641c186%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814005', 'product_url': 'https://detail.tmall.com/item.htm?abbucket=17&id=655775139334&mi_id=CCUcOfR_7yLDlkxMA5GKXp84xEH7GmJtY35U5Q2sALbty7r6s8VKKhChFBpxYv5l40AmMP7xIuQemL6UeRztzPV643958l9IWGAh5R1_zCY&ns=1&priceTId=2150452417551722079738415e1c9e&skuId=5817035829197&spm=a21n57.1.hoverItem.10&utparam=%7B%22aplus_abtest%22%3A%2285e8cce573d402cb2e9d1452d4a2f736%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814006', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=694844912726&mi_id=U3W18c-As3qoz7mZx_y65X10N_N8ohwUuXETWj7TH1H9wypxCGNqetIYGA4sdAhyUT9I1L58E-eh5QkLNVU4ckUR7qKxf2i34yPtLOk1gyY&ns=1&priceTId=2150452417551722079738415e1c9e&skuId=4932072660738&spm=a21n57.1.hoverItem.30&utparam=%7B%22aplus_abtest%22%3A%22041dd32dd57b6dd37973976128129baa%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814010', 'product_url': 'https://detail.tmall.com/item.htm?ali_refid=a3_420434_1006%3A1687741944%3AH%3A7PYLSMR2LMickarLHLhGfg%3D%3D%3A3e3fa589280dc09b90efe7801ab981fd&ali_trackid=282_3e3fa589280dc09b90efe7801ab981fd&id=760517023196&mi_id=qcbwEfqM1FfdPoKpWpmwdQBJPDU37gCNY74qmKe9s5L6zY9iQ9cJzdRuuvqan9XTSg530M_A_lshh08CMxvvvOxhko67j827CkQ2gTrxRm0&mm_sceneid=1_0_5429902547_0&priceTId=2150452417551723129156153e1c9e&skuId=5256056349199&spm=a21n57.1.hoverItem.2&utparam=%7B%22aplus_abtest%22%3A%22d9d55dec7b5ee21abc391a4490c7c7dc%22%7D&xxc=ad_ztc', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814011', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=962055770977&mi_id=gWQGleEX0oTRSO5G6cv6uA33PTuvakpB9MU8epILhfn5UkmUwLN4FjgtLk-QAtLUEVrYPE6Ii4l5naL9NTHiwlCRHiec2G9OhFtkJ3pI2m4&ns=1&priceTId=2150452417551723129156153e1c9e&skuId=6064136919654&spm=a21n57.1.hoverItem.17&utparam=%7B%22aplus_abtest%22%3A%22b3b26949da7fc4b4ce308807665289f0%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}]
                        await session.execute(
                            insert(ProductHistoryTable),
                            history_data
                        )

                except Exception as e:
                    logging.error(f"MySQL查询失败: {str(e)}")
                    # 事务会自动回滚
                    raise

    async def get_scheduler_exists(self, paraStatus) -> int:
        """获取待处理的URL列表"""
        async with self.async_session() as session:
            try:
                result = await session.scalar(
                    select(
                        exists().where(
                            SchedulerTable.status.in_(paraStatus)
                        )
                    )
                )
                return result
            except Exception as e:
                logging.error(f"任务表_exists失败: {str(e)}")
                raise

    async def get_scheduler_list(self, paraStatus, crawl):
        """获取待处理的URL列表"""
        async with self.async_session() as session:
            async with session.begin():  # 使用事务上下文管理器
                try:
                    result = await session.execute(
                        select(SchedulerTable)
                        .where(SchedulerTable.status.in_(paraStatus))
                        .limit(100)
                        .with_for_update(skip_locked=True) # 跳过已被锁定的行
                    )
                    scheduler_list = [self._row_to_dict(row) for row in result.scalars()]

                    # 统计浏览器打开的窗口次数
                    browserTotal = 0
                    success_ids = []
                    failed_updates = []

                    # 数据采集
                    for scheduler in scheduler_list:
                        print(f'正在处理: {scheduler["product_type_url"]}')
                        # 窗口
                        browserTotal += 1

                        try:
                            # 代理IP取得
                            # proxy = await proxy_manager.get_proxy()
                            # playwright 淘宝活动数据采集
                            if (await crawl.tpe_exec(scheduler['product_type_url'], None)):
                                success_ids.append(scheduler['id'])
                        except Exception as ex:
                            print(f'活动数据采集失败： {str(ex)}')
                            failed_updates.append({
                                'id': scheduler['id'],
                                'status': '1'
                            })

                        # 统计浏览器打开的窗口次数 = 100时
                        # if browserTotal == 10:
                        #     print(f'reboot : {browserTotal}')
                        #     await crawl.reboot()
                        #     browserTotal = 0

                    # 批量更新失败记录
                    if failed_updates:
                        await session.execute(
                            update(SchedulerTable),
                            failed_updates
                        )

                    # 批量处理成功记录
                    # if success_ids:
                    #     # 批量删除原记录
                    #     await session.execute(
                    #         delete(SchedulerTable)
                    #         .where(SchedulerTable.id.in_(success_ids))
                    #     )

                        # 批量插入任务履历表
                        # history_data = [{
                        #     **{k: v for k, v in p.items() if k != 'id'},
                        #     'status': '2'
                        # } for p in scheduler_list if p['id'] in success_ids]
                        #
                        # # history_data: [{'platform': '淘宝', 'product_type': '', 'product_id': '250814009', 'product_url': 'https://detail.tmall.com/item.htm?ali_refid=a3_430582_1006%3A1232930108%3AN%3AKV%2Fu6HT5hnIF5S%2F00x%2BYSQ%3D%3D%3A852f38a485c4eb92cecb42ce4eef118d&ali_trackid=162_852f38a485c4eb92cecb42ce4eef118d&id=595733677157&mi_id=nq5O6PNbc6XUDEJyaL5YWORylfiwnCdNXej3XsZTI8XVaz_eHsH9Efd0Xtt_p5EMWkVR-aPoi2ZBEgk_xm86EtOtABbuQIF4iNjKWqXa4QE&mm_sceneid=7_0_450650167_0&priceTId=215041c017550393941591411e1371&skuId=4566066668610&spm=a21n57.1.hoverItem.1&utparam=%7B%22aplus_abtest%22%3A%226e18d7ad0d17624698dde0503577ce6a%22%7D&xxc=ad_ztc', 'status': '2', 'create_time': datetime.datetime(2025, 8, 13, 20, 21, 42), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814008', 'product_url': 'https://item.taobao.com/item.htm?ali_refid=a3_420434_1006%3A1120844747%3AN%3A2wPJAdhNUSw1l3HjVQ7h0JRxhEj1d6Rz%3Acf0563f6cbc0174dccc338aa68488396&ali_trackid=1_cf0563f6cbc0174dccc338aa68488396&id=595563083409&mi_id=0000J7mfPM_M7vjOkk4-mmyLQfqc3fMzaJBWlszcyki8FOw&mm_sceneid=1_0_110176333_0&priceTId=2150452417551718754506782e1c9e&skuId=4300189139208&spm=a21n57.1.hoverItem.1&utparam=%7B%22aplus_abtest%22%3A%229ce507475b63e2442f82eb7e3a179542%22%7D&xxc=ad_ztc', 'status': '2', 'create_time': datetime.datetime(2025, 8, 13, 20, 26, 46), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814007', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=923376253416&mi_id=0000SFY96peiwP8g17BnYmwYe_xZXjlUbsm99vRnFNqfgQ4&ns=1&priceTId=2150452417551718754506782e1c9e&skuId=5799893164668&spm=a21n57.1.hoverItem.13&utparam=%7B%22aplus_abtest%22%3A%2265dc7686cbcb56bc22c2c3b246f28f32%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 47, 42), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814001', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=568384314550&mi_id=0000q9ry4YHIAjOLT6cWxzl4MunC04BRYMlMUqs5XR2M8Uo&ns=1&priceTId=2150452417551718754506782e1c9e&skuId=3798203962050&spm=a21n57.1.hoverItem.36&utparam=%7B%22aplus_abtest%22%3A%226e95f7f00fb459bf4a8a446d57c1acfa%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 48, 16), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814002', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=574937922347&mi_id=_nEngL4dA9xFA1UrEvJc6lY46TrYQtNYPdZfTo6UFep6rZJAHbGbVC-Etee1nSwa6EpbH5xkBCsO0byHn1GCykxVxNWqXilY2BHrWhV9jkg&ns=1&priceTId=2150452417551721136233444e1c9e&skuId=4477821112457&spm=a21n57.1.hoverItem.17&utparam=%7B%22aplus_abtest%22%3A%2272d993ec99628dd4f9c7d71d5e2b65ff%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814003', 'product_url': 'https://detail.tmall.com/item.htm?ali_refid=a3_420434_1006%3A1316820001%3AH%3A089sl6cpAznrKKioK474vw%3D%3D%3A0ef207e99057446973f2acaba2613b77&ali_trackid=282_0ef207e99057446973f2acaba2613b77&id=811150604986&mi_id=JXK7V4PqOMcFImyD3PUEZTXYTbghtE-cZhnqsYaJ3zDfH4RfbYreU2eFPxPw_YRA_XscAK8FksGG-rO0M2umQe1_k9NuhLlsav4LSuuSLjY&mm_sceneid=1_0_1217370115_0&priceTId=2150452417551721524205679e1c9e&skuId=6064712662241&spm=a21n57.1.hoverItem.2&utparam=%7B%22aplus_abtest%22%3A%2290557614f25b34909f9fd13ebbc327bf%22%7D&xxc=ad_ztc', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814004', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=953215308764&mi_id=86N_r3_8skp9TNO3F6HHSN6TW6lN5YfTzlFXyBdkK3xASYJ5l-UU-1l6RO6_7f98f_7B-hJTWjD74TNOQATm_ldM8cvQJQxB5iUwx9AJZzw&ns=1&priceTId=2150452417551721524205679e1c9e&skuId=5871582625770&spm=a21n57.1.hoverItem.48&utparam=%7B%22aplus_abtest%22%3A%229ea476d53d5863a00c808a4e0641c186%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814005', 'product_url': 'https://detail.tmall.com/item.htm?abbucket=17&id=655775139334&mi_id=CCUcOfR_7yLDlkxMA5GKXp84xEH7GmJtY35U5Q2sALbty7r6s8VKKhChFBpxYv5l40AmMP7xIuQemL6UeRztzPV643958l9IWGAh5R1_zCY&ns=1&priceTId=2150452417551722079738415e1c9e&skuId=5817035829197&spm=a21n57.1.hoverItem.10&utparam=%7B%22aplus_abtest%22%3A%2285e8cce573d402cb2e9d1452d4a2f736%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814006', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=694844912726&mi_id=U3W18c-As3qoz7mZx_y65X10N_N8ohwUuXETWj7TH1H9wypxCGNqetIYGA4sdAhyUT9I1L58E-eh5QkLNVU4ckUR7qKxf2i34yPtLOk1gyY&ns=1&priceTId=2150452417551722079738415e1c9e&skuId=4932072660738&spm=a21n57.1.hoverItem.30&utparam=%7B%22aplus_abtest%22%3A%22041dd32dd57b6dd37973976128129baa%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814010', 'product_url': 'https://detail.tmall.com/item.htm?ali_refid=a3_420434_1006%3A1687741944%3AH%3A7PYLSMR2LMickarLHLhGfg%3D%3D%3A3e3fa589280dc09b90efe7801ab981fd&ali_trackid=282_3e3fa589280dc09b90efe7801ab981fd&id=760517023196&mi_id=qcbwEfqM1FfdPoKpWpmwdQBJPDU37gCNY74qmKe9s5L6zY9iQ9cJzdRuuvqan9XTSg530M_A_lshh08CMxvvvOxhko67j827CkQ2gTrxRm0&mm_sceneid=1_0_5429902547_0&priceTId=2150452417551723129156153e1c9e&skuId=5256056349199&spm=a21n57.1.hoverItem.2&utparam=%7B%22aplus_abtest%22%3A%22d9d55dec7b5ee21abc391a4490c7c7dc%22%7D&xxc=ad_ztc', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}, {'platform': '淘宝', 'product_type': '', 'product_id': '250814011', 'product_url': 'https://item.taobao.com/item.htm?abbucket=17&id=962055770977&mi_id=gWQGleEX0oTRSO5G6cv6uA33PTuvakpB9MU8epILhfn5UkmUwLN4FjgtLk-QAtLUEVrYPE6Ii4l5naL9NTHiwlCRHiec2G9OhFtkJ3pI2m4&ns=1&priceTId=2150452417551723129156153e1c9e&skuId=6064136919654&spm=a21n57.1.hoverItem.17&utparam=%7B%22aplus_abtest%22%3A%22b3b26949da7fc4b4ce308807665289f0%22%7D&xxc=taobaoSearch', 'status': '2', 'create_time': datetime.datetime(2025, 8, 14, 19, 52, 25), 'update_time': datetime.datetime(2025, 8, 14, 23, 19, 1)}]
                        # await session.execute(
                        #     insert(ProductHistoryTable),
                        #     history_data
                        # )

                except Exception as e:
                    logging.error(f"MySQL查询失败: {str(e)}")
                    # 事务会自动回滚
                    raise

    async def update_status(self, url_id: int, status: str) -> bool:
        """更新URL处理状态"""
        async with self.async_session() as session:
            try:
                await session.execute(
                    update(ProductCollectTable)
                    .where(ProductCollectTable.id == url_id)
                    .values(status=status)
                )
                print(f'Where id = {url_id} And status = {status}')
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logging.error(f"MySQL更新失败: {str(e)}")
                return False

    async def delete_id(self, url_id: int) -> bool:
        """删除数据"""
        async with self.async_session() as session:
            try:
                # 使用 delete() 函数创建删除语句，并在其上调用 where()
                print(f'ProductCollectTable.id: {url_id}')
                await session.execute(
                    delete(ProductCollectTable).where(ProductCollectTable.id == url_id)
                )
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logging.error(f"MySQL删除失败: {str(e)}")
                return False

    async def insert_product(self, data: dict) -> bool:
        """插入URL处理状态"""
        async with self.async_session() as session:
            try:
                stmt = insert(ProductHistoryTable).values(data)
                # 存在则更新非主键字段
                update_stmt = stmt.on_duplicate_key_update(
                    product_url=stmt.inserted.product_url,
                    status=stmt.inserted.status
                )
                await session.execute(update_stmt)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logging.error(f"MySQL插入失败: {str(e)}")
                return False

    def _row_to_dict(self, row) -> Dict:
        """ORM对象转字典"""
        return {c.name: getattr(row, c.name) for c in row.__table__.columns}

async def main():
    repo = MySQLRepository("root:Lian+2040@192.168.1.13:3306/taobao")
    urls = await repo.get_urls('2')
    urls[0].pop('id')
    await repo.insert_product(urls[0])
    print(urls[0])
    # await repo.update_status(urls[0]['id'], '2')

if __name__ == '__main__':
    asyncio.run(main())

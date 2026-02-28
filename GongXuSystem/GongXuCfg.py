# _*_ coding: utf-8 _*_
# @Time : 2025/5/22 0022 21:30
# @Author : 韦丽
# @Version: V 1.0
# @File : StockCfg.py
# @desc : 工序管理系统配置文件读取
import configparser
import json
import os


class GongXuCfg:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('_internal/config/config.ini', encoding='utf-8')
        self.initValues()

    def initValues(self):
        # 数据库配置数据
        # 数据库IP地址
        self.host = self.config.get('database', 'Host')
        # 数据库端口
        self.port = self.config.get('database', 'Port')
        # 数据库登录用户
        self.user = self.config.get('database', 'User')
        # 数据库登录密码
        self.password = self.config.get('database', 'Password')
        # 数据库名称_ODBC配置名称
        self.dbname = self.config.get('database', 'Dbname')

        # 计算时的基础值
        # 车种
        self.machine_C_key = json.loads(self.config.get('计算', 'machine_C_key'))
        # 动作描述
        self.action_C_key = json.loads(self.config.get('计算', 'action_C_key'))
        # 级别
        self.level_C_key = json.loads(self.config.get('计算', 'level_C_key'))
        # 长度范围
        self.length_range_C_key = json.loads(self.config.get('计算', 'length_range_C_key'))

        # 下拉框数据
        # 车种
        self.machine_key = json.loads(self.config.get('下拉框', 'machine_key'))
        # 动作描述
        self.action_key = json.loads(self.config.get('下拉框', 'action_key'))
        # 长度
        self.length_key = json.loads(self.config.get('下拉框', 'length_key'))
        # 级别
        self.level_key = json.loads(self.config.get('下拉框', 'level_key'))
        # 频率
        self.frequency_key = json.loads(self.config.get('下拉框', 'frequency_key'))
        # 表格标题
        self.gongXuTable_title = json.loads(self.config.get('表格标题', 'gongXuTable_title'))
        # 系统标题
        self.window_title = json.loads(self.config.get('系统标题', 'window_title'))

        # 按钮名称
        # 检索
        self.search_button = json.loads(self.config.get('按钮名称', 'search_button'))
        # 引用
        self.template_button = json.loads(self.config.get('按钮名称', 'template_button'))
        # 导出
        self.import_button = json.loads(self.config.get('按钮名称', 'import_button'))
        # 展开
        self.expand_button = json.loads(self.config.get('按钮名称', 'expand_button'))
        # 收缩
        self.shrink_button = json.loads(self.config.get('按钮名称', 'shrink_button'))
        # 删除
        self.delete_button = json.loads(self.config.get('按钮名称', 'delete_button'))
        # 添加
        self.rowAdd_button = json.loads(self.config.get('按钮名称', 'rowAdd_button'))

        # 系统Log出力
        # Log文件夹
        self.current_dir = json.loads(self.config.get('Logger', 'current_dir'))
        # Log文件
        self.current_file = json.loads(self.config.get('Logger', 'current_file'))
        # Log文件encode
        self.current_encode = json.loads(self.config.get('Logger', 'current_encode'))

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   webview.py
@Time    :   2023/11/29 10:38:24
@Author  :   yangff 
@Version :   1.0
@微信公众号:  学点编程吧
'''

# 第21章简单浏览器--浏览页面

from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView

class WebView(QWebEngineView):
    '''
    新的页面
    '''
    def __init__(self):
        '''
        一些初始设置
        '''
        super().__init__()
        self.zoom = 1.0 # 缩放因子
        setting = self.page().profile().settings() # 浏览器设置
        setting.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True) # 可以支持Flash，默认关闭
        setting.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)
        setting.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled,
                                         True)  # 启用PDF查看器‌:ml-citation{ref="2" data="citationList"}

    def contextMenuEvent(self, event):
        event.ignore()  # 阻止默认右键菜单

    def getZoom(self):
        """
        返回缩放因子
        """
        return self.zoom

    def setZoom(self, p):
        """
        设置缩放因子
        """
        self.zoom = p

# _*_ coding: utf-8 _*_
# @Time : 2025/7/13 星期日 17:26
# @Author : 韦丽
# @Version: V 1.0
# @File : WebEngineViewEx.py
# @desc :
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView


class WebEngineView(QWebEngineView):
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
        setting.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled,
                                         True)  # 启用PDF查看器‌:ml-citation{ref="2" data="citationList"}

        # 指定WebEngine是否会尝试预取DNS条目以加快浏览速度，默认为关闭。
        # 安装事件过滤器
        self.installEventFilter(self)
        self.page().childEvent = lambda e: self._handle_child_event(e)
        self.page().loadFinished.connect(self._inject_anti_zoom)

    def _handle_child_event(self, event):
        if event.type() == QEvent.Type.ChildAdded:
            child = event.child()
            if child.isWidgetType():
                child.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            return True  # 阻断CTRL+滚轮事件
        return super().eventFilter(obj, event)

    def _inject_anti_zoom(self):
        js = """
                document.addEventListener('wheel', e => {
                    if (e.ctrlKey) e.preventDefault()
                }, { passive: false })
                """
        self.page().runJavaScript(js)

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

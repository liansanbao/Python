import configparser
import datetime
import multiprocessing
import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *  # 从 PyQt6 中导入所需的类
from PyQt6.QtGui import *

from WLW.StockBase import WaringStockServer, PlateFundServer
from WLW.Tools.LoggingEx import logger
from WLW.Ui_WLW import Ui_WLW
from WLW.action import StockInfoAction, WaringStockAction, IncreaseFiveAction, PlateFundAction, MenuAction, \
    NoticesAction
from WLW.model import DataOpreationModel, ChinaHolidaysModel

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

# 获取上一级目录
parent_dir = os.path.dirname(dir_path)

parent_dir = parent_dir.replace('\\', '/')

class UIWLW(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)

class LWLW():
    def __init__(self, passKey):
        self.__mainWindow = None
        self.__mainform = None
        # 读取配置文件
        self.config = configparser.ConfigParser()
        self.config.read('_internal/config/config.ini', 'utf-8')  # 确保config.ini文件存在
        # 获取系统标题
        self.window_title = self.config.get('系统标题', 'window_title', fallback='A股主流资金')
        # 获取系统标题
        self.myself = self.config.get('投资', 'myself', fallback='')
        # 中国法定节假日数据同步
        self.china_holidays()
        # 风险个股数据同步
        self.stock_info_question()
        # 登录用户
        self.passKey = passKey
        # exe文件夹
        self.parentPath = parent_dir

    # 风险个股数据同步
    def stock_info_question(self):
        opreationType = 'STOCK_INFO_QUESTION'
        yearMonth = datetime.datetime.today().strftime('%Y%m')
        # 交易日期
        yearMonthDom = str(DataOpreationModel.getDataInterval(opreationType))
        if yearMonthDom == yearMonth:
            return

        # 风险个股数据采集
        data_list = WaringStockServer.exec()
        if data_list and len(data_list) > 0:
            WaringStockServer.insertServere(data_list)
            ymd = datetime.datetime.today().strftime('%Y-%m-%d')
            ymdhms = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            DataOpreationModel.insert('', [(ymd, yearMonth, opreationType, ymdhms, ymdhms)])

    # 中国法定节假日数据同步
    def china_holidays(self):
        opreationType = 'China_Holidays'
        year = int(datetime.datetime.today().strftime('%Y'))
        # 交易日期
        opreationChinaCount = DataOpreationModel.getDataInterval(opreationType)
        if opreationChinaCount == year:
            return

        # 中国节假日数据采集
        data_list = ChinaHolidaysModel.exec(year)
        if data_list:
            ChinaHolidaysModel.insert(year, data_list)
            ymd = datetime.datetime.today().strftime('%Y-%m-%d')
            ymdhms = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            DataOpreationModel.insert('', [(ymd, year, opreationType, ymdhms, ymdhms)])

    def __init_mainWindow(self):
        self.__mainWindow = UIWLW()
        self.__mainform = Ui_WLW()
        self.__mainform.setupUi(self.__mainWindow)

    # 画面设定
    def settingContent(self):
        # 窗体标题
        icon = QIcon()
        icon.addPixmap(QPixmap("_internal/image/wlw.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.__mainWindow.setWindowIcon(icon)
        self.__mainWindow.setWindowTitle(self.window_title)
        # 窗体固定大小， 最大化无效
        self.__mainWindow.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);
        # 关闭窗口右下角拖动按钮
        self.__mainWindow.setStatusBar(QStatusBar().setSizeGripEnabled(False))
        # 状态栏设定

        # 初期化
        self.initContent()
        # 事件绑定
        self.actionSetting()
        # 数据处理
        self.editDataTable()

        # 新增关闭事件处理
        def handle_close_event():
            # 主流板块动态数据今日之前的删除
            # PlateFundServer.deleteType()
            # 删除 PDF/html/png文件
            StockInfoAction.deleteFile()

        # 绑定三种关闭方式
        self.__mainWindow.closeEvent = lambda e: handle_close_event()  # 点击关闭按钮

    # 初期化
    def initContent(self):
        # 检索按钮Icon设定
        icon1 = QIcon()
        icon1.addPixmap(QPixmap("_internal/image/award.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.__mainform.stockSubmit.setIcon(icon1)
        # self.__mainform.master_stockSubmit.setIcon(icon1)
        self.__mainform.plateFundSubmit.setIcon(icon1)
        self.__mainform.lncrease_stockSubmit.setIcon(icon1)
        self.__mainform.waring_stockSubmit.setIcon(icon1)
        self.__mainform.notice_stockSubmit.setIcon(icon1)

        # 分类显示按钮Icon设定
        icon = QIcon()
        icon.addPixmap(QPixmap("_internal/image/outFile.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.__mainform.stockDialog.setIcon(icon)
        # self.__mainform.showMainCapitalDialog.setIcon(icon)

        # 消除按钮Icon设定
        clearIcon = QIcon()
        clearIcon.addPixmap(QPixmap("_internal/image/del.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.__mainform.stockClear.setIcon(clearIcon)
        # self.__mainform.master_stockClear.setIcon(clearIcon)
        self.__mainform.plateFundClear.setIcon(clearIcon)
        self.__mainform.lncrease_stockClear.setIcon(clearIcon)
        self.__mainform.waring_stockClear.setIcon(clearIcon)
        self.__mainform.notice_stockClear.setIcon(clearIcon)

        # 投资按钮Icon设定
        touziIcon = QIcon()
        touziIcon.addPixmap(QPixmap("_internal/image/notice.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.__mainform.notice_myself.setIcon(touziIcon)

        # 访问key设置
        self.__mainform.passKey = self.passKey
        # 涨停板Tab
        StockInfoAction.stockInfoInitContent(self, self.__mainform)
        # 主流资金Tab
        # MainCapitalAction.mainCapitalInitContent(self, self.__mainform)
        # 板块资金Tab
        PlateFundAction.plateFundInitContent(self, self.__mainform)
        # 涨幅(5%)以上Tab
        IncreaseFiveAction.increaseFiveInitContent(self, self.__mainform)
        # 风险个股Tab
        WaringStockAction.waringStockInitContent(self, self.__mainform)
        # 公告
        NoticesAction.noticesInitContent(self, self.__mainform)

    # 事件绑定
    def actionSetting(self):
        # 菜单按钮(事件绑定)
        MenuAction.menuActionSetting(self, self.__mainform)
        # 涨停板Tab(事件绑定)
        StockInfoAction.stockInfoActionSetting(self, self.__mainform)
        # 主力资金Tab(事件绑定)
        # MainCapitalAction.mainCapitalActionSetting(self, self.__mainform)
        # 板块资金Tab(事件绑定)
        PlateFundAction.plateFundActionSetting(self, self.__mainform)
        # 涨幅(5%)以上Tab
        IncreaseFiveAction.increaseFiveActionSetting(self, self.__mainform)
        # 风险个股Tab(事件绑定)
        WaringStockAction.waringStockActionSetting(self, self.__mainform)
        # 公告
        NoticesAction.noticesActionSetting(self, self.__mainform)

    # 数据处理
    def editDataTable(self):
        # 涨停板Tab(数据处理)
        StockInfoAction.editStockTable(self, self.__mainform)
        # 主力资金Tab(数据处理)
        # MainCapitalAction.editMainCapitalTable(self, self.__mainform)
        # 板块资金Tab
        PlateFundAction.editPlateFundTable(self, self.__mainform)
        # 涨幅(5%)以上Tab
        IncreaseFiveAction.editIncreaseFiveTable(self, self.__mainform)
        # 风险个股(数据处理)
        WaringStockAction.editWaringStockTable(self, self.__mainform)
        # 公告数据
        NoticesAction.editNoticeTable(self, self.__mainform)

    # 主处理
    def run(self):
        try:
            # app = QApplication(sys.argv)
            logger.info('应用程序启动了......')
            self.__init_mainWindow()
            self.settingContent()
            self.__mainWindow.show()
            # sys.exit(app.exec_())
        except Exception as e:
            logger.error(f'主程序出错误了：{e}')
            raise e

if __name__ == '__main__':
    try:
        # windows打包必须，否则无线重复启动，linux上无须
        multiprocessing.freeze_support()
        qApp = LWLW()
        qApp.run()
    except Exception as ex:
        logger.error(f'主程序出错误了：{ex}')








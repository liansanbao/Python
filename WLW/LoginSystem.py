# _*_ coding: utf-8 _*_
# @Time : 2025/7/19 星期六 12:55
# @Author : 韦丽
# @Version: V 1.0
# @File : LoginSystem.py
# @desc : 系统用户登录、注册、密码找回等等
import json
import multiprocessing
import os
import re
import sys
from pathlib import Path

import requests
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtNetwork import QNetworkInterface
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QMessageBox, QHBoxLayout, QFormLayout, QCheckBox)

from WLW.ShowWLW import LWLW
from WLW.UpdateWlw import InstallerWindow
from WLW.model import UserMemoryModel

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = Path(str(os.path.dirname(script_path)))

dir_parent_path = dir_path.parent.parent  # 连续回退两级

BASE_URL = "https://w7wp557v37c1.xiaomiqiu.com/wlw"

# 按钮样式美化
btn_StyleSheet = """
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-size: 12px;
                    border: none;
                    icon-size: 16px;
                }
                QPushButton:hover {
                    background-color: #0b7dda;
                }
                QPushButton:pressed {
                    background-color: #0a69b7;
                }
                """

def get_mac_address():
    for interface in QNetworkInterface.allInterfaces():
        # 过滤有效物理网卡
        if (interface.flags() & QNetworkInterface.InterfaceFlag.IsUp and
                interface.flags() & QNetworkInterface.InterfaceFlag.IsRunning and
                not interface.flags() & QNetworkInterface.InterfaceFlag.IsLoopBack):
            return interface.hardwareAddress()
    return ""

# 密码找回--关键信息输入画面
class InputInfoPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.macAddress = get_mac_address()

    def initUI(self):
        # 主布局改为水平布局
        main_layout = QHBoxLayout()

        # 左侧图片区域
        image_label = QLabel()
        pixmap = QPixmap("_internal/image/china_cow.jpg")  # 替换为实际图片路径
        image_label.setPixmap(pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(image_label)

        # 右侧表单区域
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(10, 20, 10, 20)

        # 创建表单项目
        self.username = QLineEdit()
        self.alipay = QLineEdit()
        self.email = QLineEdit()
        # 使用QFormLayout保持标签和输入框的对齐
        form = QFormLayout()
        form.addRow("用户名:", self.username)
        form.addRow("支付宝账号:", self.alipay)
        form.addRow("注册邮箱:", self.email)
        # 按钮组
        submit_btn = QPushButton(" 提交验证")
        tijiao_icon = QIcon()
        tijiao_icon.addPixmap(QPixmap("_internal/image/tijiao.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        submit_btn.setIcon(tijiao_icon)
        submit_btn.setIconSize(QSize(16, 16))
        submit_btn.setFixedHeight(24)
        submit_btn.setStyleSheet(btn_StyleSheet)
        submit_btn.clicked.connect(self.verify_info)
        return_btn = QPushButton(" 返回")
        return_icon = QIcon()
        return_icon.addPixmap(QPixmap("_internal/image/return.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        return_btn.setIcon(return_icon)
        return_btn.setIconSize(QSize(16, 16))
        return_btn.setFixedHeight(24)
        return_btn.setStyleSheet(btn_StyleSheet)
        return_btn.clicked.connect(self.return_action)

        # 添加控件到表单布局
        form_layout.addLayout(form)
        form_layout.addWidget(submit_btn)
        form_layout.addWidget(return_btn)
        form_layout.addStretch()  # 添加弹性空间

        main_layout.addWidget(form_widget)
        self.setLayout(main_layout)
        self.setFixedSize(400, 200)  # 调整窗口大小
        self.setWindowTitle("密码找回")
        # 窗体标题
        icon = QIcon()
        icon.addPixmap(QPixmap("_internal/image/wlw.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        # 窗体固定大小， 最大化无效
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);

    def return_action(self):
        self.login = LoginWindow()
        self.login.show()
        self.hide()

    def verify_info(self):
        # 提交数据到服务器
        try:
            username = self.username.text()
            alipy = self.alipay.text()
            email = self.email.text()
            if not all([username, alipy, email]):
                QMessageBox.warning(self, '警告', '所有字段都必须填写')
                return
            data = {
                "username": username,
                "alipy": alipy,
                "email": email,
                "macAddress": self.macAddress
            }
            response = requests.post(f"{BASE_URL}?table_key=findpass", data=data, timeout=30)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                for name in json_data:
                    data = dict(name)

                if data['ok'] == '1':
                    self.aas = VerifyCodePage(data['key'], data['username'], email)
                    self.aas.show()
                    self.hide()
                elif data['ok'] == '0':
                    QMessageBox.warning(self, "账号不存在", "输入信息重新输入")
                    pass
            # 服务器端错误 301、400、401、404、500、502、503
            else:
                QMessageBox.warning(self, '错误', f'信息验证失败, 稍后再试。')
        except Exception as e:
            QMessageBox.critical(self, '异常', f'信息验证异常了: {str(e)}')

# 密码找回--输入验证码画面
class VerifyCodePage(QWidget):
    def __init__(self, key, username, email):
        super().__init__()
        self.initUI()
        self.key = key
        self.username = username
        self.email = email

    def initUI(self):
        # 主布局改为水平布局
        main_layout = QHBoxLayout()

        # 左侧图片区域
        image_label = QLabel()
        pixmap = QPixmap("_internal/image/china_cow.jpg")  # 替换为实际图片路径
        image_label.setPixmap(pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(image_label)

        # 右侧表单区域
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(10, 20, 10, 20)

        self.code_input = QLineEdit()
        verify_btn = QPushButton(" 验证")
        tijiao_icon = QIcon()
        tijiao_icon.addPixmap(QPixmap("_internal/image/tijiao.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        verify_btn.setIcon(tijiao_icon)
        verify_btn.setIconSize(QSize(16, 16))
        verify_btn.setFixedHeight(24)
        verify_btn.setStyleSheet(btn_StyleSheet)
        verify_btn.clicked.connect(self.verify_code)

        # 添加控件到表单布局
        form_layout.addWidget(QLabel("请输入来自邮箱验证码:"))
        form_layout.addWidget(self.code_input)
        form_layout.addWidget(verify_btn)
        form_layout.addStretch()

        main_layout.addWidget(form_widget)
        self.setLayout(main_layout)
        self.setFixedSize(400, 200)  # 调整窗口大小
        self.setWindowTitle("验证码确认")
        # 窗体标题
        icon = QIcon()
        icon.addPixmap(QPixmap("_internal/image/wlw.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        # 窗体固定大小， 最大化无效
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);

    def verify_code(self):
        # 提交数据到服务器
        try:
            response = requests.post(f"{BASE_URL}?table_key=verify_code",
                                     data={"emailCode": self.code_input.text(), "email": self.email}, timeout=30)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                for name in json_data:
                    data = dict(name)

                if data['ok'] == '1':
                    self.rest = ResetPasswordPage(self.key, self.username)
                    self.rest.show()
                    self.hide()
                elif data['ok'] == '0':
                    QMessageBox.warning(self, "验证码", "输入验证码错误，重新输入。")

            # 服务器端错误 301、400、401、404、500、502、503
            else:
                QMessageBox.warning(self, '错误', f'验证码验证失败, 稍后再试。')
        except Exception as e:
            QMessageBox.critical(self, '异常', f'验证码验证异常了: {str(e)}')

# 密码找回--输入密码
class ResetPasswordPage(QWidget):
    def __init__(self, key, username):
        super().__init__()
        self.initUI()
        self.key = key
        self.username = username
        self.macAddress = get_mac_address()

    def initUI(self):
        # 主布局改为水平布局
        main_layout = QHBoxLayout()

        # 左侧图片区域
        image_label = QLabel()
        pixmap = QPixmap("_internal/image/china_cow.jpg")  # 替换为实际图片路径
        image_label.setPixmap(pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(image_label)

        # 右侧表单区域
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(10, 20, 10, 20)

        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form.addRow("新密码:", self.new_password)
        form.addRow("确认密码:", self.confirm_password)

        submit_btn = QPushButton(" 提交")
        tijiao_icon = QIcon()
        tijiao_icon.addPixmap(QPixmap("_internal/image/tijiao.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        submit_btn.setIcon(tijiao_icon)
        submit_btn.setIconSize(QSize(16, 16))
        submit_btn.setFixedHeight(24)
        submit_btn.setStyleSheet(btn_StyleSheet)
        submit_btn.clicked.connect(self.reset_password)

        # 添加控件到表单布局
        form_layout.addLayout(form)
        form_layout.addWidget(submit_btn)
        form_layout.addStretch()

        main_layout.addWidget(form_widget, stretch=2)
        self.setLayout(main_layout)
        self.setFixedSize(400, 200)  # 调整窗口大小
        self.setWindowTitle("密码修改")
        # 窗体标题
        icon = QIcon()
        icon.addPixmap(QPixmap("_internal/image/wlw.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        # 窗体固定大小， 最大化无效
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);

    def reset_password(self):
        # 提交数据到服务器
        try:
            if not all([self.new_password.text(), self.confirm_password.text()]):
                QMessageBox.warning(self, '警告', '所有字段都必须填写')
                return

            if self.new_password.text() != self.confirm_password.text():
                QMessageBox.warning(self, "错误", "两次密码不一致")
                return

            response = requests.post(f"{BASE_URL}?table_key=reset_password",
                                     data={
                                         "key": self.key,
                                         "password": self.new_password.text()}, timeout=30)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                for name in json_data:
                    data = dict(name)

                if data['ok'] == '1':
                    UserMemoryModel.insert(
                        [(self.username, self.new_password.text(), self.macAddress, 'CheckState.Unchecked')])
                    QMessageBox.information(self, "成功", "密码重置成功")
                    self.login = LoginWindow()
                    self.login.show()
                    self.hide()
            # 服务器端错误 301、400、401、404、500、502、503
            else:
                QMessageBox.warning(self, '错误', f'密码修改失败, 稍后再试。')

        except Exception as e:
            QMessageBox.critical(self, '异常', f'密码修改异常了: {str(e)}')

# 登录
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # MacAddress获取
        self.macAddress = get_mac_address()
        # 用户记忆数据获取
        self.userMemoryData = UserMemoryModel.getDataInterval(self.macAddress)
        self.setWindowTitle("登录")
        # 窗体标题
        icon = QIcon()
        icon.addPixmap(QPixmap("_internal/image/wlw.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        self.setFixedSize(400, 230)

        # 主控件使用水平布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 左侧图片区域
        image_label = QLabel()
        pixmap = QPixmap("_internal/image/china_cow.jpg")  # 替换为实际图片路径
        image_label.setPixmap(pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(image_label)

        # 右侧
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(10, 20, 10, 20)

        # 用户名输入
        self.username_label = QLabel("用户名:")
        self.username_input = QLineEdit()
        if self.userMemoryData:
            self.username_input.setText(self.userMemoryData['username'])
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)

        # 密码输入
        self.password_label = QLabel("密码:")
        self.password_input = QLineEdit()
        if self.userMemoryData:
            self.password_input.setText(self.userMemoryData['password'])
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_input)

        # 记住密码复选框
        self.remember_check = QCheckBox("记住密码")
        if self.userMemoryData:
            self.remember_check.setChecked(True)
        form_layout.addWidget(self.remember_check)

        # 按钮组
        button_layout = QHBoxLayout()
        login_icon = QIcon()
        login_icon.addPixmap(QPixmap("_internal/image/login.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.login_btn = QPushButton(" 登录")
        self.login_btn.setIcon(login_icon)
        self.login_btn.setIconSize(QSize(16, 16))
        self.login_btn.setFixedHeight(24)
        self.login_btn.setStyleSheet(btn_StyleSheet)
        self.login_btn.clicked.connect(self.attempt_login)
        register_icon = QIcon()
        register_icon.addPixmap(QPixmap("_internal/image/register.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.register_btn = QPushButton(" 注册")
        self.register_btn.setIcon(register_icon)
        self.register_btn.setIconSize(QSize(16, 16))
        self.register_btn.setFixedHeight(24)
        # 注册按钮样式美化
        self.register_btn.setStyleSheet(btn_StyleSheet)
        self.register_btn.clicked.connect(self.show_register)
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.register_btn)

        form_layout.addLayout(button_layout)
        findkey_icon = QIcon()
        findkey_icon.addPixmap(QPixmap("_internal/image/findkey.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.find_btn = QPushButton(" 密码找回")
        self.find_btn.setIcon(findkey_icon)
        self.find_btn.setIconSize(QSize(16, 16))
        self.find_btn.setFixedHeight(24)
        self.find_btn.setStyleSheet(btn_StyleSheet)
        self.find_btn.clicked.connect(self.find_user)
        form_layout.addWidget(self.find_btn)

        form_layout.addStretch()
        main_layout.addWidget(form_widget)

    def validate_password(self, password):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[\S]{8,16}$'
        return re.match(pattern, password)

    def attempt_login(self):
        # 提交数据到服务器
        try:
            username = self.username_input.text()
            password = self.password_input.text()

            if not all([username, password]):
                QMessageBox.warning(self, '警告', '请输入用户名和密码')
                return

            if not self.validate_password(password):
                QMessageBox.warning(self, '警告', '密码必须8-16位且包含大小写字母和数字')
                return

            # 这里替换为实际的后端验证逻辑
            response = requests.post(f"{BASE_URL}?table_key=wlw_login",
                                     data={
                                         "macAddress": self.macAddress,
                                         "username": username,
                                         "password": password}, timeout=30)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                for name in json_data:
                    data = dict(name)

                if data['ok'] == '1':
                    # 是否记忆用户名和密码
                    # 记忆数据没有，checkbox选中，插入数据
                    if str(self.remember_check.checkState()) == 'CheckState.Checked':
                        UserMemoryModel.insert([(username, password, self.macAddress, 'CheckState.Checked')])
                    # 记忆数据有，checkbox未选中，插入数据
                    elif str(self.remember_check.checkState()) == 'CheckState.Unchecked' and self.userMemoryData:
                        UserMemoryModel.insert(
                            [(username, password, self.macAddress, 'CheckState.Unchecked')])
                    passKey = '' if username != 'liansanbao' else 'WLW'
                    self.open_main_system(passKey)
                elif data['ok'] == '2':
                    QMessageBox.information(self, "失败", "密码输入错误，重新输入。")
                elif data['ok'] == '0':
                    QMessageBox.information(self, "失败", "登录用户不存在。")
            # 服务器端错误 301、400、401、404、500、502、503
            else:
                QMessageBox.warning(self, '错误', f'登录失败, 稍后再试。')
        except Exception as e:
            QMessageBox.critical(self, '异常', f'登录异常了: {str(e)}')

    def show_register(self):
        self.register_window = RegisterForm()
        self.register_window.show()
        self.hide()

    def find_user(self):
        self.findpassword = InputInfoPage()
        self.findpassword.show()
        self.hide()

    def open_main_system(self, passKey):
        try:
            # windows打包必须，否则无线重复启动，linux上无须
            multiprocessing.freeze_support()
            qApp = LWLW(passKey)
            qApp.run()
            # 关闭登录窗口
            self.hide()
        except Exception as ex:
            QMessageBox.critical(self, '异常', f'主程序出现异常了: {str(ex)}')

# 注册
class RegisterForm(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.macAddress = get_mac_address()

    def initUI(self):
        # 主布局改为水平布局
        main_layout = QHBoxLayout()

        # 左侧图片区域
        image_label = QLabel()
        pixmap = QPixmap("_internal/image/china_cow.jpg")  # 替换为实际图片路径
        image_label.setPixmap(pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(image_label)

        # 右侧表单区域
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(20, 20, 20, 20)

        # 创建控件
        self.username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        # 支付宝账号
        self.alipy_label = QLabel('支付宝账号:')
        self.alipy_input = QLineEdit()

        self.password_label = QLabel('密码(8-16位，含大小写字母和数字):')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # 添加密码可见切换按钮
        self.toggle_btn = QPushButton()
        self.toggle_btn.setFlat(True)  # 无边框
        icon = QIcon()
        icon.addPixmap(QPixmap("_internal/image/eye.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.toggle_btn.setIcon(icon)
        self.toggle_btn.setFixedHeight(24)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_password_visibility)

        # 密码输入框和按钮的水平布局
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_btn)

        self.email_label = QLabel('邮箱:')
        self.email_input = QLineEdit()
        self.phone_label = QLabel('手机号(11位):')
        self.phone_input = QLineEdit()
        self.submit_btn = QPushButton(' 注册')
        register_icon = QIcon()
        register_icon.addPixmap(QPixmap("_internal/image/register.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.submit_btn.setIcon(register_icon)
        self.submit_btn.setIconSize(QSize(16, 16))
        self.submit_btn.setFixedHeight(24)
        self.submit_btn.setStyleSheet(btn_StyleSheet)
        self.submit_btn.clicked.connect(self.validate_and_submit)
        self.login_btn = QPushButton(' 登录')
        login_icon = QIcon()
        login_icon.addPixmap(QPixmap("_internal/image/login.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.login_btn.setIcon(login_icon)
        self.login_btn.setIconSize(QSize(16, 16))
        self.login_btn.setFixedHeight(24)
        self.login_btn.setStyleSheet(btn_StyleSheet)
        self.login_btn.clicked.connect(self.login_and_submit)

        # 表单布局
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.alipy_label)
        form_layout.addWidget(self.alipy_input)
        form_layout.addWidget(self.password_label)
        form_layout.addLayout(password_layout)  # 使用水平布局
        form_layout.addWidget(self.email_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.phone_label)
        form_layout.addWidget(self.phone_input)
        form_layout.addWidget(self.submit_btn)
        form_layout.addWidget(self.login_btn)

        main_layout.addWidget(form_widget)
        self.setLayout(main_layout)

        # 窗体设置
        self.setWindowTitle('注册')
        icon = QIcon()
        icon.addPixmap(QPixmap("_internal/image/wlw.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        self.setFixedSize(700, 400)
        # 窗体固定大小， 最大化无效
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    # 其余方法保持不变...
    def validate_password(self, password):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[\S]{8,16}$'
        return re.match(pattern, password)

    def validate_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email)

    def validate_phone(self, phone):
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, phone)

    def login_and_submit(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.hide()

    def validate_and_submit(self):
        username = self.username_input.text().strip()
        alipy = self.alipy_input.text().strip()
        password = self.password_input.text()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()

        if not all([username, alipy, password, email, phone]):
            QMessageBox.warning(self, '警告', '所有字段都必须填写')
            return

        if not self.validate_password(password):
            QMessageBox.warning(self, '警告', '密码必须8-16位且包含大小写字母和数字')
            return

        if not self.validate_email(email):
            QMessageBox.warning(self, '警告', '邮箱格式不正确')
            return

        if not self.validate_phone(phone):
            QMessageBox.warning(self, '警告', '手机号格式不正确')
            return

        # 提交数据到服务器
        try:
            response = requests.post(
                f"{BASE_URL}?table_key=wlw_register",
                data={
                    'username': username,
                    'alipy':alipy,
                    'macAddress': self.macAddress,
                    'password': password,
                    'email': email,
                    'phone': phone
                },
                timeout=30
            )

            if response.status_code == 200:
                json_data = json.loads(response.text)
                for name in json_data:
                    data = dict(name)
                if data['ok'] == '0':
                    # 账号已注册
                    QMessageBox.information(self, '账号已注册', f' 用户名：{data["username"]}\n 支付宝账号：{data["alipy"]}\n mac地址： {data["macAddress"]}')
                elif data['ok'] == '1':
                    QMessageBox.information(self, '成功', '注册成功')
                self.login_window = LoginWindow()
                self.login_window.show()
                self.hide()
            # 服务器端错误 301、400、401、404、500、502、503
            else:
                QMessageBox.warning(self, '错误', f'注册失败, 稍后再试。')
        except Exception as e:
            QMessageBox.critical(self, '异常', f'注册异常了: {str(e)}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstallerWindow(dir_path.parent, dir_parent_path)
    if window.isUpdae():
        window.show()
    else:
        window = LoginWindow()
        window.show()
    sys.exit(app.exec())

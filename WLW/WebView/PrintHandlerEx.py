# _*_ coding: utf-8 _*_
# @Time : 2025/7/14 星期一 15:20
# @Author : 韦丽
# @Version: V 1.0
# @File : PrintHandlerEx.py
# @desc :
import os

from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
from PyQt6.QtGui import QPainter, QPageLayout, QPageSize, QImage
from PyQt6.QtCore import QMarginsF, Qt, QRectF
from pdf2image import convert_from_path

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

class PrintHandler:
    def __init__(self, target_widget):
        self.target = target_widget
        self.content_height = 0  # 记录内容总高度

    def load_pdf(self, file_path):
        # 隐藏控制台窗口（Windows/Linux均适用）
        os.environ["POPPLER_HIDE_WINDOW"] = "1"

        # print(f'dir_path: {dir_path}')

        """加载PDF并转换为图像"""
        self.pages = convert_from_path(file_path, dpi=300, poppler_path=f'{dir_path}/bin', fmt="png", thread_count=4, use_pdftocairo=True)

    def show_print_preview(self):
        if not hasattr(self, 'pages'):
            raise ValueError("请先调用load_pdf()加载PDF文件")
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)  # 设置为PDF输出
        page_size = QPageSize(QPageSize.PageSizeId.A4)
        layout = QPageLayout(
            page_size,
            QPageLayout.Orientation.Portrait,
            QMarginsF(10, 15, 10, 15),
            QPageLayout.Unit.Millimeter
        )
        printer.setPageLayout(layout)

        preview = QPrintPreviewDialog(printer, self.target)
        preview.setWindowTitle("预览")
        preview.setWindowFlags(preview.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint)
        preview.resize(1000, 800)

        preview.paintRequested.connect(self.render_content)
        preview.exec()

    def render_content(self, printer):
        # 设置打印机为高质量模式
        printer.setResolution(300)  # 设置DPI为300
        painter = QPainter(printer)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing |
                               QPainter.RenderHint.TextAntialiasing |
                               QPainter.RenderHint.SmoothPixmapTransform)

        # 获取页面尺寸和边距
        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        margin = 0  # 边距
        content_width = page_rect.width() - 2 * margin
        y_offset = margin  # 当前绘制位置的y坐标

        # 模拟多页内容 - 这里可以替换为你的实际内容
        for i in range(len(self.pages)):  # 生成5页内容
            # 使用原始DPI转换图像
            img = self.pages[i].convert('RGBA')
            qimage = QImage(img.tobytes(), img.width, img.height, QImage.Format.Format_RGBA8888)

            # 计算保持原始分辨率的缩放比例
            scale_factor = min(
                content_width / qimage.width(),
                (page_rect.height() - 2 * margin) / qimage.height()
            )
            target_width = int(qimage.width() * scale_factor)
            target_height = int(qimage.height() * scale_factor)

            # 将浮点参数显式转换为整数
            scaled_img = qimage.scaled(
                target_width,  # 宽度转整型
                target_height,  # 高度转整型
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # 换页判断
            if y_offset + scaled_img.height() > page_rect.height() - margin:
                printer.newPage()
                y_offset = margin

            painter.drawImage(
                QRectF(
                    margin + (content_width - scaled_img.width()) / 2,  # 水平居中
                    y_offset,
                    scaled_img.width(),
                    scaled_img.height()
                ),
                scaled_img
            )
            y_offset += scaled_img.height() + 20

        painter.end()

    def print_directly(self):
        """直接打印PDF内容"""
        if not hasattr(self, 'pages'):
            raise ValueError("请先调用load_pdf()加载PDF文件")

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

        # 弹出打印对话框让用户选择打印机和设置
        print_dialog = QPrintDialog(printer, self.target)
        if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.render_content(printer)  # 复用已有的渲染逻辑
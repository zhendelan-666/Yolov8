import json
import os
import sys
import pandas as pd
from PyQt6 import uic
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QStackedWidget, QFileDialog, QMessageBox,
)
from Information import Ui_Form as Information
from Enter import Ui_Form as Enter
from History import Ui_Form as History
from Home import Ui_Form as Home
from Detect import Ui_Form as Detect
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("基于Yolov8的检测系统")
        self.setGeometry(100, 100, 800, 600)
        self.data_file = 'outbound_cargo_info.csv'  # 定义CSV文件路径

        # 创建一个QStackedWidget作为中心控件
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 创建并添加Home页面
        self.home_page = QWidget()
        Home().setupUi(self.home_page)
        self.stacked_widget.addWidget(self.home_page)

        # 创建并添加Enter页面
        self.enter_page = QWidget()
        Enter().setupUi(self.enter_page)
        self.stacked_widget.addWidget(self.enter_page)

        # 创建并添加Information页面
        self.info_page = QWidget()
        Information().setupUi(self.info_page)
        self.stacked_widget.addWidget(self.info_page)

        # 创建并添加History页面
        self.history_page = QWidget()
        History().setupUi(self.history_page)
        self.stacked_widget.addWidget(self.history_page)

        # 创建并添加Detect页面
        self.detect_page = QWidget()
        Detect().setupUi(self.detect_page)
        self.stacked_widget.addWidget(self.detect_page)

        self.update_info_button_status()
        self.connect_return_button()

        # 连接按钮到切换函数
        # Home页面
        self.home_page.findChild(QPushButton, "pushButton").clicked.connect(self.switch_to_enter)
        self.home_page.findChild(QPushButton, "pushButton_2").clicked.connect(self.switch_to_information)
        self.home_page.findChild(QPushButton, "pushButton_3").clicked.connect(self.switch_to_detect)
        self.home_page.findChild(QPushButton, "pushButton_4").clicked.connect(self.switch_to_history)
        #Enter界面
        self.enter_page.findChild(QPushButton, "pushButton_2").clicked.connect(self.choose_the_file)


        # 每个页面有一个按钮用于返回Home页面
        self.enter_page.findChild(QPushButton, "pushButton").clicked.connect(self.switch_to_home)
        self.history_page.findChild(QPushButton, "pushButton_3").clicked.connect(self.switch_to_home)
        self.info_page.findChild(QPushButton, "pushButton_2").clicked.connect(self.switch_to_home)
        self.detect_page.findChild(QPushButton, "pushButton").clicked.connect(self.switch_to_home)


    def switch_to_enter(self):
        self.stacked_widget.setCurrentIndex(1)
    def switch_to_information(self):
        self.stacked_widget.setCurrentIndex(2)
    def switch_to_detect(self):
         self.stacked_widget.setCurrentIndex(4)
    def switch_to_history(self):
        self.stacked_widget.setCurrentIndex(3)

    def connect_return_button(self):
        return_button = self.info_page.findChild(QPushButton, "pushButton_2")
        if return_button:
            return_button.clicked.connect(self.switch_to_home)
        else:
            print("Warning: Could not find return button in Information page")

    def choose_the_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择出仓货物信息文件", "", "Excel Files (*.xls *.xlsx)")
        if file_path:
            try:
                # 读取Excel文件
                df = pd.read_excel(file_path)
                # 验证文件是否包含日期和出仓货物清单
                if '日期' not in df.columns or '出仓货物清单' not in df.columns:
                    raise ValueError("文件格式不正确，请确保文件包含'日期'和'出仓货物清单'列")
                # 保存为CSV文件
                df.to_csv(self.data_file, index=False, encoding='utf-8')
                QMessageBox.information(self, "导入成功", "出仓货物信息已成功导入并保存")
                self.update_info_button_status()
                self.switch_to_information()
                self.show_imported_info()
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"导入文件时出错: {str(e)}")

    def load_existing_data(self):
        if os.path.exists(self.data_file):
            return pd.read_csv(self.data_file)
        return None

    def update_info_button_status(self):
        info_button = self.home_page.findChild(QPushButton, "pushButton_2")
        if os.path.exists(self.data_file):
            info_button.setEnabled(True)
        else:
            info_button.setEnabled(False)

    def show_imported_info(self):
        data = self.load_existing_data()
        if data is not None:
            # 查找 info_layout
            info_layout = self.info_page.findChild(QVBoxLayout, "info_layout")

            if info_layout is None:
                # 如果找不到 info_layout，尝试在整个页面中查找
                info_layout = self.info_page.findChild(QVBoxLayout)

            if info_layout is None:
                # 如果仍然找不到，创建一个新的 layout
                info_layout = QVBoxLayout()
                self.info_page.setLayout(info_layout)

            # 清空之前的信息显示，但保留返回按钮
            while info_layout.count():
                item = info_layout.takeAt(0)
                widget = item.widget()
                if widget and widget.objectName() != "pushButton_2":
                    widget.deleteLater()

            # 添加信息到页面
            for _, row in data.iterrows():
                date_label = QLabel(f"日期: {row['日期']}")
                items_label = QLabel(f"出仓货物清单: {row['出仓货物清单']}")
                info_layout.addWidget(date_label)
                info_layout.addWidget(items_label)

            # 确保返回按钮在最后
            return_button = self.info_page.findChild(QPushButton, "pushButton_2")
            if return_button:
                info_layout.addWidget(return_button)

            # 重新连接返回按钮
            self.connect_return_button()
        else:
            QMessageBox.warning(self, "信息", "尚未导入任何出仓货物信息。")
    def switch_to_home(self):
        self.stacked_widget.setCurrentIndex(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
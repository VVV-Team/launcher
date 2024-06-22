from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings, QUrl, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QFileDialog,
    QFrame, QGridLayout, QMessageBox,
    QStyleFactory, QTabWidget,
    QSpinBox, QCheckBox, QStyle, QStyleOption,
    QGraphicsDropShadowEffect, QListWidget, QInputDialog
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPainter, QPen, QLinearGradient, QPalette

from minecraft_launcher_lib.utils import get_minecraft_directory, get_version_list, get_installed_versions
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.command import get_minecraft_command

from random_username.generate import generate_username
from uuid import uuid1
from sys import argv, exit
import os

from constants import *
from widgets import RoundedWidget, RoundedButton, InstallDirectoryWidget, MemorySettingsWidget, GraphicsSettingsWidget, TabWidget, ModManagerTab
from threads import LaunchThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bedrock Launcher")
        self.setMinimumSize(500, 450)
        self.setWindowFlags(
            Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        )
        self.setStyleSheet(f"""
            font-family: Arial;
            background-color: {MAIN_COLOR};
        """)

        # --- Set Icon ---
        # Че за бред?
        #self.setWindowIcon(QIcon("C:/Users/User/Desktop/Bedrock Launcher/V3 new/1.ico"))

        # --- Central Widget ---
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # --- Main Layout ---
        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # --- Logo ---
        self.logo_label = QLabel(self.centralwidget)
        self.logo_label.setAlignment(Qt.AlignCenter)
        #pixmap = QPixmap("C:/Users/User/Desktop/Bedrock Launcher/V3 new/121banner.png")  # Replace with your logo path
        #self.logo_label.setPixmap(pixmap.scaledToWidth(800))  # Adjust width as needed
        self.main_layout.addWidget(self.logo_label)

        # --- Title Label ---
        self.title_label = QLabel(
            "Bedrock Launcher", self.centralwidget
        )
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 24px; font-weight: bold;"
        )
        self.main_layout.addWidget(self.title_label)

        # --- Tab Widget ---
        self.tab_widget = TabWidget(self.centralwidget)
        self.main_layout.addWidget(self.tab_widget)

        # --- Settings ---
        self.settings = QSettings(
            "MyCompany", "Bedrock Launcher"
        )
        self.install_directory = self.settings.value(
            "install_directory", get_minecraft_directory()
        )

        # --- Create Tabs ---
        self.create_launch_tab()
        self.create_memory_tab()
        self.create_graphics_tab()
        self.create_mod_manager_tab()

        # --- Launch Thread ---
        self.launch_thread = LaunchThread(self)
        self.launch_thread.state_update_signal.connect(
            self.state_update
        )
        self.launch_thread.progress_update_signal.connect(
            self.update_progress_label
        )

        self.update_installed_versions(
            self.install_directory_widget.install_directory
        )  # Передаем текущую директорию

    def create_launch_tab(self):
        self.launch_tab = QWidget()
        self.launch_tab_layout = QVBoxLayout(
            self.launch_tab
        )
        self.launch_tab_layout.setContentsMargins(
            15, 15, 15, 15
        )
        self.launch_tab_layout.setSpacing(15)

        # --- Install Directory ---
        self.install_directory_widget = InstallDirectoryWidget(
            self
        )
        self.launch_tab_layout.addWidget(
            self.install_directory_widget
        )
        self.install_directory_widget.install_directory = (
            self.install_directory
        )
        self.install_directory_widget.directory_changed.connect(
            self.update_installed_versions
        )

        # --- Username Input ---
        self.username_layout = QHBoxLayout()
        self.username_label = QLabel(
            "Username:", self.launch_tab
        )
        self.username_label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 12px; font-weight: bold;"
        )
        self.username_layout.addWidget(
            self.username_label
        )

        self.username = QLineEdit(self.launch_tab)
        self.username.setPlaceholderText(
            "Enter your username"
        )
        self.username.setStyleSheet(f"""
            color: {TEXT_COLOR}; 
            border: 1px solid {ACCENT_COLOR}; 
            border-radius: 5px; 
            padding: 5px;
            background-color: {MAIN_COLOR};
        """)
        self.username.setText(
            self.settings.value("username", "")
        )
        self.username_layout.addWidget(self.username)
        self.launch_tab_layout.addLayout(
            self.username_layout
        )

        # --- Installed Versions ---
        self.installed_versions_label = QLabel(
            "Installed Versions:", self.launch_tab
        )
        self.installed_versions_label.setAlignment(
            Qt.AlignCenter
        )
        self.installed_versions_label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 14px; font-weight: bold;"
        )
        self.launch_tab_layout.addWidget(
            self.installed_versions_label
        )

        self.installed_versions_combobox = QComboBox(
            self.launch_tab
        )
        self.installed_versions_combobox.setStyleSheet(f"""
            color: {TEXT_COLOR}; 
            border: 1px solid {ACCENT_COLOR}; 
            border-radius: 5px; 
            padding: 5px;
            background-color: {MAIN_COLOR};
        """)
        self.launch_tab_layout.addWidget(
            self.installed_versions_combobox
        )

        # --- Version Select ---
        self.version_select = QComboBox(self.launch_tab)
        self.version_select.setStyleSheet(f"""
            color: {TEXT_COLOR}; 
            border: 1px solid {ACCENT_COLOR}; 
            border-radius: 5px; 
            padding: 5px;
            background-color: {MAIN_COLOR};
        """)
        for version in get_version_list():
            self.version_select.addItem(version["id"])
        self.version_select.setCurrentText(
            self.settings.value(
                "version", self.version_select.itemText(0)
            )
        )
        self.launch_tab_layout.addWidget(
            self.version_select
        )

        # --- Progress Label ---
        self.progress_label = QLabel(self.launch_tab)
        self.progress_label.setText("")
        self.progress_label.setVisible(False)
        self.progress_label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 12px; font-weight: bold;"
        )
        self.launch_tab_layout.addWidget(
            self.progress_label
        )

        # --- Launch Button ---
        self.launch_button = RoundedButton(
            "Launch Client", self.launch_tab
        )
        self.launch_button.clicked.connect(
            self.launch_game
        )
        self.launch_tab_layout.addWidget(
            self.launch_button
        )

        self.tab_widget.addTab(self.launch_tab, "Launch")

    def create_memory_tab(self):
        self.memory_tab = QWidget()
        self.memory_tab_layout = QVBoxLayout(
            self.memory_tab
        )
        self.memory_tab_layout.setContentsMargins(
            15, 15, 15, 15
        )
        self.memory_tab_layout.setSpacing(15)

        self.memory_settings_widget = MemorySettingsWidget(
            self
        )
        self.memory_tab_layout.addWidget(
            self.memory_settings_widget
        )

        self.tab_widget.addTab(self.memory_tab, "Memory")

    def create_graphics_tab(self):
        self.graphics_tab = QWidget()
        self.graphics_tab_layout = QVBoxLayout(
            self.graphics_tab
        )
        self.graphics_tab_layout.setContentsMargins(
            15, 15, 15, 15
        )
        self.graphics_tab_layout.setSpacing(15)

        self.graphics_settings_widget = GraphicsSettingsWidget(
            self
        )
        self.graphics_tab_layout.addWidget(
            self.graphics_settings_widget
        )

        self.tab_widget.addTab(
            self.graphics_tab, "Graphics"
        )

    def create_mod_manager_tab(self):
        self.mod_manager_tab = ModManagerTab(
            self.install_directory
        )
        self.tab_widget.addTab(
            self.mod_manager_tab, "Mod Manager"
        )

    def state_update(self, value):
        self.launch_button.setDisabled(value)
        self.progress_label.setVisible(value)

    def launch_game(self):
        version_id = self.get_minecraft_version()
        username = self.username.text()
        memory_mb = (
            self.memory_settings_widget.memory_spinbox.value()
        )
        self.launch_thread.launch_setup_signal.emit(
            version_id, username, memory_mb
        )
        self.launch_thread.start()

    def get_minecraft_version(self):
        return self.version_select.currentText()

    def update_progress_label(
        self, progress, progress_max, status
    ):
        self.progress_label.setText(
            f"{status} ({progress}/{progress_max})"
        )

    def update_installed_versions(self, directory=None):
        if directory is None:
            directory = (
                self.install_directory_widget.install_directory
            )
        self.launch_thread.wait()  # Ждем завершения потока перед обновлением версий
        self.update_installed_versions_combobox(
            directory
        )

    def update_installed_versions_combobox(self, directory):
        self.installed_versions_combobox.clear()
        for version in get_installed_versions(directory):
            self.installed_versions_combobox.addItem(
                f"{version['id']} (installed)"
            )

        self.installed_versions_combobox.currentIndexChanged.connect(
            self.update_version_select
        )

    def update_version_select(self, index):
        selected_version = (
            self.installed_versions_combobox.itemText(index)
        )
        selected_version = selected_version.split(" (")[
            0
        ]  # Удаляем " (installed)"
        self.version_select.setCurrentText(
            selected_version
        )

    def paintEvent(self, event):
        # Рисуем градиент на фоне
        painter = QPainter(self)
        gradient = QLinearGradient(
            self.rect().topLeft(), self.rect().bottomLeft()
        )
        gradient.setColorAt(
            0.0, QColor("#2c3e50")
        )  # Первый цвет градиента
        gradient.setColorAt(
            1.0, QColor("#4ca1af")
        )  # Второй цвет градиента
        painter.fillRect(self.rect(), gradient)

if __name__ == "__main__":
    app = QApplication(argv)
    app.setStyle(QStyleFactory.create("Fusion"))

    # Применяем темную палитру к QApplication
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(MAIN_COLOR))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(ACCENT_COLOR))
    palette.setColor(QPalette.AlternateBase, QColor(MAIN_COLOR))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(ACCENT_COLOR))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(BLUE))
    palette.setColor(QPalette.Highlight, QColor(BLUE))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    exit(app.exec_())
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

import random
import string
from uuid import uuid1
from sys import argv, exit
import os
import requests

from constants import *
from widgets import RoundedWidget, RoundedButton, InstallDirectoryWidget, MemorySettingsWidget, GraphicsSettingsWidget, TabWidget, ModManagerTab
from threads import LaunchThread

def generate_username(length=12):
    """Генерирует случайное имя пользователя."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_forge_versions():
    url = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        versions = data.get('promos', {})
        return versions
    else:
        print("Failed to retrieve Forge versions")
        return None

def get_fabric_versions():
    url = "https://meta.fabricmc.net/v2/versions/loader"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        versions = [entry['version'] for entry in data]
        return versions
    else:
        print("Failed to retrieve Fabric versions")
        return None

def get_forge_download_link(mc_version):
    url = "https://files.minecraftforge.net/maven/net/minecraftforge/forge/promotions_slim.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        versions = data.get('promos', {})
        for version, build in versions.items():
            if version.startswith(mc_version + "-"):
                return f"https://files.minecraftforge.net/maven/net/minecraftforge/forge/{version}/forge-{version}-installer.jar"
    else:
        print("Failed to retrieve Forge download link")
        return None

def get_fabric_download_link(mc_version):
    url = "https://meta.fabricmc.net/v2/versions/loader"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for entry in data:
            if entry['loader']['version'] == mc_version:
                return entry['loader']['build']
    else:
        print("Failed to retrieve Fabric download link")
        return None

def download_file(url, path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Downloaded {path}")
    else:
        print(f"Failed to download {url}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(LAUNCHER_NAME)
        self.setMinimumSize(500, 750)
        self.setWindowFlags(
            Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        )
        self.setStyleSheet(f"""
            font-family: Arial;
            background-color: {MAIN_COLOR};
        """)

        # --- Set Icon ---
        self.setWindowIcon(QIcon("../images/favicon.ico"))

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
        pixmap = QPixmap("../images/banner.png")
        self.logo_label.setPixmap(pixmap.scaledToWidth(1024)) 
        self.main_layout.addWidget(self.logo_label)

        # --- Title Label ---
        self.title_label = QLabel(
            LAUNCHER_NAME, self.centralwidget
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
            COMPANY_NAME, LAUNCHER_NAME
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
        ) 

        self.forge_versions = {}
        self.fabric_versions = {}
        self.update_available_versions()

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

        # --- Version Type Select ---
        self.version_type_select = QComboBox(self.launch_tab)
        self.version_type_select.setStyleSheet(f"""
            color: {TEXT_COLOR}; 
            border: 1px solid {ACCENT_COLOR}; 
            border-radius: 5px; 
            padding: 5px;
            background-color: {MAIN_COLOR};
        """)
        self.version_type_select.addItems(["Vanilla", "Forge", "Fabric"])
        self.version_type_select.currentIndexChanged.connect(self.update_version_select)
        self.launch_tab_layout.addWidget(self.version_type_select)

        # --- Version Select ---
        self.version_select = QComboBox(self.launch_tab)
        self.version_select.setStyleSheet(f"""
            color: {TEXT_COLOR}; 
            border: 1px solid {ACCENT_COLOR}; 
            border-radius: 5px; 
            padding: 5px;
            background-color: {MAIN_COLOR};
        """)
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
        version_type = self.version_type_select.currentText()
        version_id = self.get_minecraft_version().replace("(installed) ", '')
        username = self.username.text()
        memory_mb = (
            self.memory_settings_widget.memory_spinbox.value()
        )

        if version_type == "Forge":
            forge_link = get_forge_download_link(version_id)
            if forge_link:
                download_file(forge_link, os.path.join(self.install_directory, f"forge-{version_id}-installer.jar"))
        elif version_type == "Fabric":
            fabric_link = get_fabric_download_link(version_id)
            if fabric_link:
                download_file(fabric_link, os.path.join(self.install_directory, f"fabric-loader-{version_id}.jar"))

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
        self.launch_thread.wait() 
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

    def update_version_select(self, index=None):
        self.version_select.clear()

        version_type = self.version_type_select.currentText()
        installed_versions_list = get_installed_versions(self.install_directory_widget.install_directory)
        if version_type == "Vanilla":
            for version in get_version_list():    
                version_id = version["id"]
                if version in installed_versions_list:
                    version_id = f"(installed) {version_id}"
                self.version_select.addItem(version_id)
        elif version_type == "Forge":
            for version_id in self.forge_versions.keys(): 
                if version_id in installed_versions_list:
                    version_id = f"(installed) {version_id}"
                self.version_select.addItem(version_id)
        elif version_type == "Fabric":
            for version_id in self.fabric_versions: 
                if version_id in installed_versions_list:
                    version_id = f"(installed) {version_id}"
                self.version_select.addItem(version_id)


        self.version_select.setCurrentIndex(0)

    def update_available_versions(self):
        self.forge_versions = get_forge_versions()
        self.fabric_versions = get_fabric_versions()
        self.update_version_select()

    def paintEvent(self, event):
        # Рисуем градиент на фоне
        painter = QPainter(self)
        gradient = QLinearGradient(
            self.rect().topLeft(), self.rect().bottomLeft()
        )
        gradient.setColorAt(
            0.0, QColor("#2c3e50")
        ) 
        gradient.setColorAt(
            1.0, QColor("#4ca1af")
        ) 
        painter.fillRect(self.rect(), gradient)
        painter.end()

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
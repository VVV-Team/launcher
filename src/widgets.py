from PyQt5.QtWidgets import (
    QWidget, QLabel, QComboBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog,
    QMessageBox, QTabWidget,
    QSpinBox, QCheckBox,
    QGraphicsDropShadowEffect, QListWidget, QInputDialog
)
from PyQt5.QtCore import pyqtSignal, QSettings, Qt
from PyQt5.QtGui import QColor

from minecraft_launcher_lib.utils import get_minecraft_directory
import os

from constants import *

class RoundedWidget(QWidget):
    def __init__(self, parent=None):
        super(RoundedWidget, self).__init__(parent)
        self.setStyleSheet(f'''
            background-color: {MAIN_COLOR};
            border-radius: 15px;
            padding: 10px;
        ''')

        # Создаем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(DARK_GRAY))

        # Применяем тень к виджету
        self.setGraphicsEffect(shadow)

class RoundedButton(QPushButton):
    def __init__(self, text, parent=None):
        super(RoundedButton, self).__init__(text, parent)
        self.setStyleSheet(f'''
            background-color: {ACCENT_COLOR};
            color: {TEXT_COLOR};
            border-radius: 15px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            border: none;
        ''')

        # Создаем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(DARK_GRAY))

        # Применяем тень к виджету
        self.setGraphicsEffect(shadow)

    def enterEvent(self, event):
        self.setStyleSheet(f'''
            background-color: #5e667b;
            color: {TEXT_COLOR};
            border-radius: 15px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            border: none;
        ''')

    def leaveEvent(self, event):
        self.setStyleSheet(f'''
            background-color: {ACCENT_COLOR};
            color: {TEXT_COLOR};
            border-radius: 15px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            border: none;
        ''')

class InstallDirectoryWidget(QWidget):
    directory_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super(InstallDirectoryWidget, self).__init__(parent)
        self.settings = QSettings(COMPANY_NAME, LAUNCHER_NAME)
        self.install_label = QLabel("Select installation directory:", self)
        self.install_label.setAlignment(Qt.AlignCenter)
        self.install_label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 12px; font-weight: bold;"
        )

        self.install_button = RoundedButton("Browse...", self)
        self.install_button.clicked.connect(self.select_folder)

        self.install_directory = self.settings.value(
            "install_directory", get_minecraft_directory()
        )

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.install_label)
        self.layout.addWidget(self.install_button)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

    def select_folder(self):
        selected_directory = QFileDialog.getExistingDirectory(
            self, "Select Folder"
        )
        if selected_directory:
            self.install_directory = selected_directory
            self.settings.setValue(
                "install_directory", self.install_directory
            )
            self.directory_changed.emit(
                self.install_directory
            )  # Отправляем сигнал с новой директорией

class MemorySettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(MemorySettingsWidget, self).__init__(parent)
        self.settings = QSettings(COMPANY_NAME, LAUNCHER_NAME)

        self.memory_label = QLabel("Allocate RAM (MB):", self)
        self.memory_label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 12px; font-weight: bold;"
        )

        self.memory_spinbox = QSpinBox(self)
        self.memory_spinbox.setMinimum(
            128
        )  # Minimal RAM
        self.memory_spinbox.setMaximum(
            8192
        )  # Maximum RAM (8GB)
        self.memory_spinbox.setValue(
            self.settings.value("memory", 2048)
        )  # Default RAM
        self.memory_spinbox.setStyleSheet(f"""
            color: {TEXT_COLOR}; 
            border: 1px solid {ACCENT_COLOR}; 
            border-radius: 5px; 
            padding: 5px;
            background-color: {MAIN_COLOR};
        """)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.memory_label)
        self.layout.addWidget(self.memory_spinbox)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

        self.memory_spinbox.valueChanged.connect(
            self.save_memory_settings
        )

    def save_memory_settings(self):
        self.settings.setValue(
            "memory", self.memory_spinbox.value()
        )

class GraphicsSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(GraphicsSettingsWidget, self).__init__(parent)
        self.settings = QSettings(COMPANY_NAME, LAUNCHER_NAME)

        self.quality_label = QLabel(
            "Graphics Quality:", self
        )
        self.quality_label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 12px; font-weight: bold;"
        )

        self.quality_combobox = QComboBox(self)
        self.quality_combobox.addItems(
            ["Fastest", "Fast", "Balanced", "Fancy", "Ultra"]
        )
        self.quality_combobox.setCurrentText(
            self.settings.value("quality", "Balanced")
        )
        self.quality_combobox.setStyleSheet(f"""
            color: {TEXT_COLOR}; 
            border: 1px solid {ACCENT_COLOR}; 
            border-radius: 5px; 
            padding: 5px;
            background-color: {MAIN_COLOR};
        """)

        self.quality_layout = QHBoxLayout()
        self.quality_layout.addWidget(self.quality_label)
        self.quality_layout.addWidget(self.quality_combobox)
        self.quality_layout.setSpacing(10)
        self.quality_layout.setContentsMargins(0, 0, 0, 0)

        self.performance_checkbox = QCheckBox(
            "Optimize for Performance", self
        )
        # Преобразуем значение из QSettings в булево
        self.performance_checkbox.setChecked(
            self.settings.value("performance", False) == "True"
        )
        self.performance_checkbox.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 12px;"
        )

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.quality_layout)
        self.layout.addWidget(self.performance_checkbox)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

        self.quality_combobox.currentIndexChanged.connect(
            self.save_quality_settings
        )
        self.performance_checkbox.stateChanged.connect(
            self.save_performance_settings
        )

    def save_quality_settings(self):
        self.settings.setValue(
            "quality", self.quality_combobox.currentText()
        )

    def save_performance_settings(self):
        self.settings.setValue(
            "performance",
            self.performance_checkbox.isChecked(),
        )


class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setDocumentMode(
            True
        )  # Включаем режим документа
        self.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: none;
                top: -1px; 
            }}
            QTabBar::tab {{
                background-color: {MAIN_COLOR};
                color: {TEXT_COLOR};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 10px 20px;
                margin-right: 2px;
                border: none;  /* Убираем рамку вокруг вкладки */
            }}
            QTabBar::tab:selected {{
                background-color: {ACCENT_COLOR};
            }}
            QTabWidget::tabBar {{
                border: none; 
            }}
        """
        )


class ModManagerTab(QWidget):
    def __init__(self, install_directory, parent=None):
        super().__init__(parent)
        self.install_directory = install_directory
        self.mods_folder = os.path.join(
            self.install_directory, "mods"
        )
        self.setLayout(QVBoxLayout())
        self.initUI()

    def initUI(self):
        self.mods_list = QListWidget(self)
        self.mods_list.setStyleSheet(f"""
            color: {TEXT_COLOR}; 
            border: 1px solid {ACCENT_COLOR}; 
            border-radius: 5px; 
            padding: 5px;
            background-color: {MAIN_COLOR};
        """)
        self.layout().addWidget(self.mods_list)
        self.update_mods_list()

        button_layout = QHBoxLayout()

        add_button = RoundedButton("Add Mod", self)
        add_button.clicked.connect(self.add_mod)
        button_layout.addWidget(add_button)

        create_profile_button = RoundedButton(
            "Create Profile", self
        )
        create_profile_button.clicked.connect(
            self.create_profile
        )
        button_layout.addWidget(create_profile_button)

        self.layout().addLayout(button_layout)

    def update_mods_list(self):
        self.mods_list.clear()
        if not os.path.exists(self.mods_folder):
            os.makedirs(self.mods_folder)
        for filename in os.listdir(self.mods_folder):
            if filename.endswith(".jar"):
                self.mods_list.addItem(filename)

    def add_mod(self):
        (
            filepath,
            _,
        ) = QFileDialog.getOpenFileName(
            self,
            "Select Mod File",
            "",
            "Mods Files (*.jar)",
        )
        if filepath:
            try:
                shutil.copy2(filepath, self.mods_folder)
                self.update_mods_list()
            except shutil.SameFileError:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "This mod is already installed.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to install mod: {e}",
                )

    def create_profile(self):
        (
            profile_name,
            ok,
        ) = QInputDialog.getText(
            self,
            "Create Profile",
            "Enter a profile name:",
        )
        if ok and profile_name:
            # Добавьте логику для создания профиля, например, сохранение списка модов в файл
            QMessageBox.information(
                self,
                "Profile Created",
                f"Profile '{profile_name}' created successfully.",
            )
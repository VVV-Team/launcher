from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings, QUrl, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QFileDialog,
    QFrame, QGridLayout, QMessageBox, QApplication,
    QStyleFactory, QTabWidget,
    QSpinBox, QCheckBox, QStyle, QStyleOption,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPainter, QPen
from PyQt5.QtCore import QSize

from minecraft_launcher_lib.utils import get_minecraft_directory, get_version_list, get_installed_versions
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.command import get_minecraft_command

from random_username.generate import generate_username
from uuid import uuid1
from subprocess import call
from sys import argv, exit
import winsound
import os
import shutil
import urllib.request
import zipfile

# --- Constants ---

MAIN_COLOR = "#282c34"  # Dark gray
ACCENT_COLOR = "#4c566a"  # Light gray
TEXT_COLOR = "#d8dee9"  # Light gray for text
DARK_GRAY = "#222222"  # Dark gray for shadows
LIGHT_GRAY = "#333333"  # Light gray for background
GREEN = "#46a65e"  # Green for buttons
RED = "#b45063"  # Red for errors
BLUE = "#61afef"  # Blue for active elements
BORDER_COLOR = "#4c566a"  # Border color
PROGRESS_BAR_COLOR = "#61afef"  # Blue for progress bar

# --- Widget Styles ---

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
    # Сигнал для оповещения о смене директории
    directory_changed = pyqtSignal(str)

    def __init__(self, parent=None, settings=None):
        super(InstallDirectoryWidget, self).__init__(parent)
        self.settings = settings

        self.install_label = QLabel("Select installation directory:", self)
        self.install_label.setAlignment(Qt.AlignCenter)
        self.install_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 12px; font-weight: bold;")

        self.install_button = RoundedButton('Browse...', self)
        self.install_button.clicked.connect(self.select_folder)

        self.install_directory = self.settings.value('install_directory', get_minecraft_directory())

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.install_label)
        self.layout.addWidget(self.install_button)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

    def select_folder(self):
        selected_directory = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if selected_directory:
            self.install_directory = selected_directory
            self.settings.setValue('install_directory', self.install_directory)
            self.directory_changed.emit(self.install_directory)  # Отправляем сигнал с новой директорией

class MemorySettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(MemorySettingsWidget, self).__init__(parent)
        self.settings = QSettings("MyCompany", "Bedrock Launcher")

        self.memory_label = QLabel("Allocate RAM (MB):", self)
        self.memory_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 12px; font-weight: bold;")

        self.memory_spinbox = QSpinBox(self)
        self.memory_spinbox.setMinimum(128)  # Minimal RAM
        self.memory_spinbox.setMaximum(8192)  # Maximum RAM (8GB)
        self.memory_spinbox.setValue(self.settings.value('memory', 2048))  # Default RAM
        self.memory_spinbox.setStyleSheet(f"color: {TEXT_COLOR}; border: 1px solid {ACCENT_COLOR}; border-radius: 5px; padding: 5px;")

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.memory_label)
        self.layout.addWidget(self.memory_spinbox)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

        self.memory_spinbox.valueChanged.connect(self.save_memory_settings)

    def save_memory_settings(self):
        self.settings.setValue('memory', self.memory_spinbox.value())

class GraphicsSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(GraphicsSettingsWidget, self).__init__(parent)
        self.settings = QSettings("MyCompany", "Bedrock Launcher")

        self.quality_label = QLabel("Graphics Quality:", self)
        self.quality_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 12px; font-weight: bold;")

        self.quality_combobox = QComboBox(self)
        self.quality_combobox.addItems(["Fastest", "Fast", "Balanced", "Fancy", "Ultra"])
        self.quality_combobox.setCurrentText(self.settings.value('quality', 'Balanced'))
        self.quality_combobox.setStyleSheet(f"color: {TEXT_COLOR}; border: 1px solid {ACCENT_COLOR}; border-radius: 5px; padding: 5px;")

        self.quality_layout = QHBoxLayout()
        self.quality_layout.addWidget(self.quality_label)
        self.quality_layout.addWidget(self.quality_combobox)
        self.quality_layout.setSpacing(10)
        self.quality_layout.setContentsMargins(0, 0, 0, 0)

        self.performance_checkbox = QCheckBox("Optimize for Performance", self)
        # Преобразуем значение из QSettings в булево
        self.performance_checkbox.setChecked(self.settings.value('performance', False) == 'True')
        self.performance_checkbox.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 12px;")

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.quality_layout)
        self.layout.addWidget(self.performance_checkbox)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

        self.quality_combobox.currentIndexChanged.connect(self.save_quality_settings)
        self.performance_checkbox.stateChanged.connect(self.save_performance_settings)

    def save_quality_settings(self):
        self.settings.setValue('quality', self.quality_combobox.currentText())

    def save_performance_settings(self):
        self.settings.setValue('performance', self.performance_checkbox.isChecked())

class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setStyleSheet(f"background-color: {MAIN_COLOR}; border: none;")

    def paintEvent(self, event):
        super(TabWidget, self).paintEvent(event)

        # Get the style painter
        painter = QPainter(self)
        painter.setPen(QPen(QColor(BORDER_COLOR), 2, Qt.SolidLine))

        # Draw lines between tabs
        for i in range(self.count() - 1):
            # Используем tabRect вместо rectForTab
            tab_rect = self.tabRect(i)
            line_x = tab_rect.right()
            line_y = tab_rect.top()
            line_height = tab_rect.height()
            painter.drawLine(line_x, line_y, line_x, line_y + line_height)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bedrock Launcher")
        self.setMinimumSize(500, 450)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet(f'''
            background-color: {MAIN_COLOR}; 
            font-family: Arial;
        ''')

        # --- Set Icon ---
        self.setWindowIcon(QIcon('C:/Users/User/Desktop/Bedrock Launcher/V3 new/1.ico'))

        # --- Central Widget ---
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # --- Main Layout ---
        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # --- Installed Versions ---
        self.installed_versions_label = QLabel("Installed Versions:", self.centralwidget)
        self.installed_versions_label.setAlignment(Qt.AlignCenter)
        self.installed_versions_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 14px; font-weight: bold;")
        self.main_layout.addWidget(self.installed_versions_label)

        self.installed_versions_combobox = QComboBox(self.centralwidget)
        self.installed_versions_combobox.setStyleSheet(f"color: {TEXT_COLOR}; border: 1px solid {ACCENT_COLOR}; border-radius: 5px; padding: 5px;")
        self.main_layout.addWidget(self.installed_versions_combobox)

        # --- Logo ---
        self.logo_label = QLabel(self.centralwidget)
        self.logo_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap('C:/Users/User/Desktop/Bedrock Launcher/V3 new/121banner.png')  # Replace with your logo path
        self.logo_label.setPixmap(pixmap.scaledToWidth(800))  # Adjust width as needed
        self.main_layout.addWidget(self.logo_label)

        # --- Title Label ---
        self.title_label = QLabel("Bedrock Launcher", self.centralwidget)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(self.title_label)

        # --- Tab Widget ---
        self.tab_widget = QTabWidget(self.centralwidget)
        self.tab_widget.setStyleSheet(f"background-color: {MAIN_COLOR}; border: none;")
        self.main_layout.addWidget(self.tab_widget)

        # --- Launch Tab ---
        self.launch_tab = QWidget()
        self.launch_tab_layout = QVBoxLayout(self.launch_tab)
        self.launch_tab_layout.setContentsMargins(15, 15, 15, 15)
        self.launch_tab_layout.setSpacing(15)

        # --- Settings ---
        self.settings = QSettings("MyCompany", "Bedrock Launcher")
        self.install_directory = self.settings.value('install_directory', get_minecraft_directory())

        # --- Install Directory ---
        self.install_directory_widget = InstallDirectoryWidget(self, self.settings)  # Передача settings
        self.launch_tab_layout.addWidget(self.install_directory_widget)
        self.install_directory_widget.install_directory = self.install_directory
        self.install_directory_widget.directory_changed.connect(self.update_installed_versions)

        # --- Username Input ---
        self.username_layout = QHBoxLayout()
        self.username_label = QLabel("Username:", self.launch_tab)
        self.username_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 12px; font-weight: bold;")
        self.username_layout.addWidget(self.username_label)

        self.username = QLineEdit(self.launch_tab)
        self.username.setPlaceholderText('Enter your username')
        self.username.setStyleSheet(f"color: {TEXT_COLOR}; border: 1px solid {ACCENT_COLOR}; border-radius: 5px; padding: 5px;")
        self.username.setText(self.settings.value('username', ''))
        self.username_layout.addWidget(self.username)
        self.launch_tab_layout.addLayout(self.username_layout)

        # --- Version Select ---
        self.version_select = QComboBox(self.launch_tab)
        self.version_select.setStyleSheet(f"color: {TEXT_COLOR}; border: 1px solid {ACCENT_COLOR}; border-radius: 5px; padding: 5px;")
        for version in get_version_list():
            self.version_select.addItem(version['id'])
        self.version_select.setCurrentText(self.settings.value('version', self.version_select.itemText(0)))
        self.launch_tab_layout.addWidget(self.version_select)

        # --- Progress Label ---
        self.progress_label = QLabel(self.launch_tab)
        self.progress_label.setText('')
        self.progress_label.setVisible(False)
        self.progress_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 12px; font-weight: bold;")
        self.launch_tab_layout.addWidget(self.progress_label)

        # --- Launch Button ---
        self.launch_button = RoundedButton('Launch Client', self.launch_tab)
        self.launch_button.clicked.connect(self.launch_game)
        self.launch_tab_layout.addWidget(self.launch_button)

        self.tab_widget.addTab(self.launch_tab, "Launch")

        # --- Memory Tab ---
        self.memory_tab = QWidget()
        self.memory_tab_layout = QVBoxLayout(self.memory_tab)
        self.memory_tab_layout.setContentsMargins(15, 15, 15, 15)
        self.memory_tab_layout.setSpacing(15)

        self.memory_settings_widget = MemorySettingsWidget(self)
        self.memory_tab_layout.addWidget(self.memory_settings_widget)

        self.tab_widget.addTab(self.memory_tab, "Memory")

        # --- Graphics Tab ---
        self.graphics_tab = QWidget()
        self.graphics_tab_layout = QVBoxLayout(self.graphics_tab)
        self.graphics_tab_layout.setContentsMargins(15, 15, 15, 15)
        self.graphics_tab_layout.setSpacing(15)

        self.graphics_settings_widget = GraphicsSettingsWidget(self)
        self.graphics_tab_layout.addWidget(self.graphics_settings_widget)

        self.tab_widget.addTab(self.graphics_tab, "Graphics")

        # --- Launch Thread ---
        self.launch_thread = LaunchThread(self)
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress_label)

        # --- Анимация перехода между вкладками ---
        self.tab_widget.currentChanged.connect(self.animate_tab_change)
        self.tab_animation = QPropertyAnimation(self.tab_widget, b"currentIndex")
        self.tab_animation.setDuration(250)  # Длительность анимации в мс
        self.tab_animation.setEasingCurve(QEasingCurve.InOutQuad)  # Кривая анимации

    def animate_tab_change(self, index):
        self.tab_animation.setStartValue(self.tab_widget.currentIndex())
        self.tab_animation.setEndValue(index)
        self.tab_animation.start()

    def state_update(self, value):
        self.launch_button.setDisabled(value)
        self.progress_label.setVisible(value)

    def launch_game(self):
        version_id = self.get_minecraft_version()
        username = self.username.text()
        memory_mb = self.memory_settings_widget.memory_spinbox.value()
        self.launch_thread.launch_setup_signal.emit(version_id, username, memory_mb)
        self.launch_thread.start()

    def get_minecraft_version(self):
        return self.version_select.currentText()

    def update_progress_label(self, progress, progress_max, status):
        self.progress_label.setText(f"{status} ({progress}/{progress_max})")

    def update_installed_versions(self, directory=None):
        if directory is None:
            directory = self.install_directory_widget.install_directory
        self.launch_thread.wait()  # Ждем завершения потока перед обновлением версий
        self.update_installed_versions_combobox(directory)

    def update_installed_versions_combobox(self, directory):
        self.installed_versions_combobox.clear()
        for version in get_installed_versions(directory):
            self.installed_versions_combobox.addItem(f"{version['id']} (installed)")

        self.installed_versions_combobox.currentIndexChanged.connect(self.update_version_select)

    def update_version_select(self, index):
        selected_version = self.installed_versions_combobox.itemText(index)
        selected_version = selected_version.split(" (")[0]  # Удаляем " (installed)"
        self.version_select.setCurrentText(selected_version)

    def update_directory_label(self, directory):
        self.install_directory_label.setText(f"Current directory: {directory}")

class LaunchThread(QThread):
    launch_setup_signal = pyqtSignal(str, str, int)  # Добавили memory_mb
    progress_update_signal = pyqtSignal(int, int, str)
    state_update_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.launch_setup_signal.connect(self.launch_setup)
        self.parent = parent

        # Инициализируем атрибуты
        self.version_id = ''
        self.username = ''
        self.memory_mb = 2048  # Значение по умолчанию
        self.progress = 0
        self.progress_max = 0
        self.progress_label = ''

    def launch_setup(self, version_id, username, memory_mb):  # Добавили memory_mb
        self.version_id = version_id
        self.username = username
        self.memory_mb = memory_mb  # Сохраняем значение памяти

    def run(self):
        self.state_update_signal.emit(True)

        minecraft_directory = self.parent.install_directory_widget.install_directory
        minecraft_directory = MinecraftDirectory(minecraft_directory)

        try:
            install_minecraft_version(
                versionid=self.version_id,
                minecraft_directory=minecraft_directory.path,
                callback={
                    'setStatus': self.update_progress_label_text,
                    'setProgress': self.update_progress,
                    'setMax': self.update_progress_max
                }
            )

            if self.username == '':
                self.username = generate_username()[0]

            options = {
                'username': self.username,
                'uuid': str(uuid1()),
                'token': '',
                'jvmArguments': [f'-Xmx{self.memory_mb}M', f'-Xms{self.memory_mb // 2}M']
            }

            command = get_minecraft_command(
                version=self.version_id,
                minecraft_directory=minecraft_directory.path,
                options=options
            )

            call(command)
        except Exception as e:
            print(e)
        finally:
            self.state_update_signal.emit(False)

    def update_progress_label_text(self, status):
        self.progress_label = status
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress(self, progress):
        self.progress = progress
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress_max(self, progress_max):
        self.progress_max = progress_max
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)


class MinecraftDirectory:
    def __init__(self, path):
        self.path = path

if __name__ == "__main__":
    app = QApplication(argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    window = MainWindow()
    window.update_installed_versions(window.install_directory_widget.install_directory)  # Передаем текущую директорию
    window.show()
    exit(app.exec_())
from subprocess import call
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from minecraft_launcher_lib.install import install_minecraft_version

class LaunchThread(QThread):
    launch_setup_signal = pyqtSignal(str, str, int)
    progress_update_signal = pyqtSignal(
        int, int, str
    )
    state_update_signal = pyqtSignal(bool)

    version_id = ""
    username = ""
    memory_mb = 2048
    progress = 0
    progress_max = 0
    progress_label = ""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.launch_setup_signal.connect(
            self.launch_setup
        )
        self.parent = parent

    def launch_setup(
        self, version_id, username, memory_mb
    ):
        self.version_id = version_id
        self.username = username
        self.memory_mb = memory_mb

    def run(self):
        self.state_update_signal.emit(True)

        minecraft_directory = self.parent.install_directory_widget.install_directory

        try:
            install_minecraft_version(
                versionid=self.version_id,
                minecraft_directory=minecraft_directory,
                callback={
                    "setStatus": self.update_progress_label_text,
                    "setProgress": self.update_progress,
                    "setMax": self.update_progress_max,
                },
            )

            if self.username == "":
                self.username = generate_username()[0]

            options = {
                "username": self.username,
                "uuid": str(uuid1()),
                "token": "",
                "jvmArguments": [
                    f"-Xmx{self.memory_mb}M",
                    f"-Xms{self.memory_mb // 2}M",
                ],
            }

            quality = (
                self.parent.graphics_settings_widget.quality_combobox.currentText()
            )
            performance = (
                self.parent.graphics_settings_widget.performance_checkbox.isChecked()
            )

            # Добавляем настройки качества и производительности в команду запуска
            options["gameArgs"] = []
            if quality == "Fastest":
                options["gameArgs"].append("--fast")
            elif quality == "Fast":
                options["gameArgs"].append("--fast")
            elif quality == "Fancy":
                options["gameArgs"].append("--fancy")
            elif quality == "Ultra":
                options["gameArgs"].append("--ultra")

            if performance:
                options["gameArgs"].append(
                    "--performance"
                )

            call(
                get_minecraft_command(
                    version=self.version_id,
                    minecraft_directory=minecraft_directory,
                    options=options,
                )
            )
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Failed to launch Minecraft: {e}",
            )
        finally:
            self.state_update_signal.emit(False)

    def update_progress_label_text(self, status):
        self.progress_label = status
        self.progress_update_signal.emit(
            self.progress,
            self.progress_max,
            self.progress_label,
        )

    def update_progress(self, progress):
        self.progress = progress
        self.progress_update_signal.emit(
            self.progress,
            self.progress_max,
            self.progress_label,
        )

    def update_progress_max(self, progress_max):
        self.progress_max = progress_max
        self.progress_update_signal.emit(
            self.progress,
            self.progress_max,
            self.progress_label,
        )
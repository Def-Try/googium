from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QGridLayout,
    QGroupBox,
)
import json
import os
import sys

CONFIG_FILE = "browser/config.json"


class ConfigApp(QWidget):
    def __init__(self, config_file):
        super().__init__()

        self.config_file = config_file
        self.config = {}

        self.initUI()

        self.loadConfig()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.group_box = QGroupBox("Config")
        self.group_layout = QGridLayout()
        self.group_box.setLayout(self.group_layout)
        self.layout.addWidget(self.group_box)

        self.button = QPushButton("Save Config")
        self.button.clicked.connect(self.save_config)
        self.layout.addWidget(self.button)

        self.show()

    def loadConfig(self):
        try:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)

            for n, (key, value) in enumerate(self.config.items()):
                label = QLabel(key)
                line_edit = QLineEdit(str(value))
                if type(value) == float:
                    line_edit.setValidator(QDoubleValidator(-(2**31), 2**31 - 1, 2))
                elif type(value) == int:
                    line_edit.setValidator(QIntValidator(-(2**31), 2**31 - 1, self))
                self.group_layout.addWidget(label, n, 0)
                self.group_layout.addWidget(line_edit, n, 1)

        except FileNotFoundError:
            QMessageBox.warning(
                self, "Warning", f"File '{self.config_file}' not found."
            )
        except json.decoder.JSONDecodeError:
            QMessageBox.warning(
                self, "Warning", f"Invalid JSON file '{self.config_file}'."
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Warning",
                f"An error occurred while loading config file '{self.config_file}': {e}",
            )

    def save_config(self):
        self.config = {}
        for i in range(self.group_layout.rowCount()):
            key = self.group_layout.itemAtPosition(i, 0).widget().text()
            value = self.group_layout.itemAtPosition(i, 1).widget().text()
            self.config[key] = value

        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
                QMessageBox.information(self, "Success", "Config saved.")
        except Exception as e:
            QMessageBox.warning(
                self,
                "Warning",
                f"An error occurred while saving config file '{self.config_file}': {e}",
            )


def main():
    app = QApplication(sys.argv)
    config_app = ConfigApp(CONFIG_FILE)
    sys.exit(app.exec_())


try:
    load_cfg()
except Exception as e:
    default_config = {
        "BROWSER_NAME": "googium",
        "BROWSER_HOME": "goog://home",
        "BROWSER_USERAGENT_MOBILE": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.3",
        "BROWSER_USERAGENT_PC": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.3",
        "TAB_TITLE_CUTOFF": 20,
        "PROXY_LISTEN_HOST": "127.0.0.1",
        "PROXY_LISTEN_PORT": 6913,
        "PROXY_BUFFER_SIZE": 65536,
        "PROXY_ACTIVE": False,
    }
    _ = os.path.splitext(CONFIG_FILE)
    nam = _[0] + ".bak" + _[1]
    with open(CONFIG_FILE, "r") as fr:
        with open(nam, "w") as fw:
            fw.write(fr.read())
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)


def load_cfg(populate_globals: bool = False):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    if not populate_globals:
        return config
    for k, v in config.items():
        globals()[k] = v
    return config


if __name__ == "__main__":
    main()
else:
    load_cfg(True)

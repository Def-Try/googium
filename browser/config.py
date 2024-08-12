from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator
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
    QComboBox,
)
import json
import os
import sys

USERDATA_PATH = "userdata"
os.makedirs(USERDATA_PATH, exist_ok=True)

CONFIG_FILE = USERDATA_PATH + "/config.json"


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
                if isinstance(value, float):
                    line_edit.setValidator(QDoubleValidator(-(2**31), 2**31 - 1, 2))
                    line_edit.type = float
                if isinstance(value, int):
                    line_edit.setValidator(QIntValidator(-(2**31), 2**31 - 1, self))
                    line_edit.type = int
                if isinstance(value, bool):
                    line_edit.setValidator(
                        QRegExpValidator(QRegExp("True|False"), line_edit)
                    )
                    combobox = QComboBox()
                    combobox.addItems(["True", "False"])
                    combobox.setCurrentIndex(combobox.findText(str(value)))
                    # combobox.setLineEdit(line_edit)
                    combobox.line_edit = line_edit
                    line_edit = combobox
                    line_edit.type = bool
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
            value_widget = self.group_layout.itemAtPosition(i, 1).widget()
            if isinstance(value_widget, QLineEdit):
                value = value_widget.text()
            elif isinstance(value_widget, QComboBox):
                value = value_widget.currentText()
            else:
                value = "0"
            type_ = type(r_cfg[i][1])
            if type_ == bool:

                def type_(x):
                    return x == "True"

            self.config[key] = type_(value)

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
    "BROWSER_LAYOUT": 4,
}

try:
    cfg = load_cfg()
    have_keys = set(cfg.keys())
    need_keys = set(default_config.keys())
    missing = list(need_keys - have_keys)
    if len(missing) > 0:
        for k in missing:
            cfg[k] = default_config[k]
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
except Exception as e:
    _ = os.path.splitext(CONFIG_FILE)
    nam = _[0] + ".bak" + _[1]
    try:
        with open(CONFIG_FILE, "r") as fr:
            with open(nam, "w") as fw:
                fw.write(fr.read())
    except Exception:
        pass
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)

if __name__ == "__main__":
    main()
else:
    load_cfg(True)

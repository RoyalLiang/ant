
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py

import sys

import qdarkstyle
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QWidget

from ANT.window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())

    widget = MainWindow()
    widget.setWindowTitle('ANT(批量文件命名小工具)')
    widget.setMaximumSize(1090, 885)
    widget.show()

    sys.exit(app.exec())

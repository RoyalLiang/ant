import sys

import qdarkstyle
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QFont, QAction
from PySide6.QtWidgets import QMainWindow, QLabel, QApplication, QWidget, QMenu, QMenuBar, QPlainTextEdit, QLineEdit, \
    QSizePolicy
from pydantic import BaseModel


class ControlModel(BaseModel):

    display: str
    name: str


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        label = QLabel("Hello World", self)
        label.move(50, 50)

        self.widget = QWidget(self)
        self.widget.setMinimumSize(1090, 885)
        self.setCentralWidget(self.widget)

        self.menubar = QMenuBar(self.widget)
        # self.menubar.setObjectName("menuBar")

        self.setWindowTitle("ANT | awesome mini renamed tool")

        # self._load_menu()

        self.init_ui()

    def _load_menu(self):
        self.optionMenu = QMenu(self.menubar)
        self.optionMenu.setObjectName("optionMenu")
        self.optionMenu.setTitle("选项")

        self.menubar.addAction(self.optionMenu.menuAction())
        # self.menubar.addMenu(self.optionMenu)

    def add_action(self, model: ControlModel):
        action = QAction(self.widget)
        action.setText(model.display)
        action.setObjectName(model.name)

    def add_text(self, model: ControlModel, size: tuple, pos: tuple, plain=False, readonly=False):
        if plain:
            component = QPlainTextEdit(self.widget)
        else:
            component = QLineEdit(self.widget)

        component.setObjectName(model.name)
        component.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        component.move(*pos)
        setattr(self, model.name, component)

    def add_menu(self, model: ControlModel):
        menu = QMenu(self.menubar)
        menu.setObjectName(model.name)
        menu.setTitle(model.display)

        self.menubar.addAction(menu.menuAction())
        setattr(self, model.name, menu)

    def add_action(self):
        action = QAction(self.widget)
        action.setText("选项")

    def init_ui(self):
        self.add_menu(ControlModel(display="选项", name="optionMenu"))
        self.add_menu(ControlModel(display="视图", name="viewMenu"))
        self.add_menu(ControlModel(display="编辑", name="editMenu"))
        self.add_menu(ControlModel(display="帮助", name="helpMenu"))

        self.setMenuBar(self.menubar)

        self.add_text(ControlModel(display="选项", name="pt"), size=(350, 800), pos=(self.widget.width() - 360, self.widget.height() - 820), plain=True)

        # self.create_menu()
        # self.create_upload_btn()
        # self.create_upload_line()
        # self.create_show_treeview()

    def init_components(self):
        self.init_ui()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())

    app.setFont(QFont("Microsoft YaHei", 9))

    windows = MainWindow()
    windows.show()

    sys.exit(app.exec())

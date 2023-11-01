import abc

from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QPlainTextEdit

from ANT.env import env


class BaseDialog(QDialog):
    text = ''

    def __init__(self, parent=None):
        super().__init__(parent)

        self._set_window_title()
        self.layout = QVBoxLayout(self)
        self.re_layout()

    def _set_window_title(self):
        self.setWindowTitle(self.text)

    def re_layout(self):
        raise NotImplemented("not implement")


class CleansDataDialog(BaseDialog):

    text = "ANT | 清洁剂"

    def re_layout(self):
        text_edit = QPlainTextEdit(self)
        text_edit.setMinimumSize(350, 700)
        text_edit.setMaximumSize(350, 700)

        text_edit.setPlainText("\n".join(env.cleans))
        text_edit.setReadOnly(True)

        btn = QPushButton(self)
        btn.setText('关闭')
        btn.clicked.connect(self.close)

        self.layout.addWidget(text_edit)
        self.layout.addWidget(btn)




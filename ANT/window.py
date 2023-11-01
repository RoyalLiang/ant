
from pathlib import Path

import PySide6
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileSystemModel, QFileDialog, QMessageBox, QMainWindow, QApplication, QSizePolicy

from ANT.env import env
from ANT.rename import ant
from libs.enums import NamePositionEnum, NameRuleEnum
from ui_form import Ui_MainWindow


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setMinimumSize(1090, 885)
        self.setWindowIcon(QIcon(str(env.base_dir.joinpath(r'images/avatar.png'))))

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        self._load_slot()
        self._init()

    def _init(self) -> None:

        if env.fs:
            self._ui.filters.setText('\n'.join(env.fs))
        else:
            self._ui.filters.setPlaceholderText('''请上传txt文件，内容格式如下：  \n过滤词1  \n过滤词2  \n过滤词3  \n过滤词4''')

        if env.ds:
            self._ui.deletes.setText('\n'.join(env.ds))
        else:
            self._ui.deletes.setPlaceholderText('''请上传txt文件，内容格式如下：  \n删除词1  \n删除词2  \n删除词3  \n删除词4''')

        if env.fbs:
            self._ui.forbids.setText('\n'.join(env.fbs))
        else:
            self._ui.forbids.setPlaceholderText('''匹配文件后缀进行忽略,内容格式如下：  \n忽略词1  \n忽略词2  \n忽略词3  \n忽略词4''')

        if env.fs_cache:
            self._ui.filterCache.setChecked(True)

        if env.ds_cache:
            self._ui.deleteCache.setChecked(True)

        if env.fb_cache:
            self._ui.forbidCache.setChecked(True)

        if env.str_path:
            self._ui.dirPath.setText(str(env.str_path))
            if Path(env.str_path).resolve().exists():
                self._load_tree_view(str(env.str_path))
        else:
            self._ui.dirPath.setText('')

        if env.filter_folder:
            self._ui.filterFolder.setChecked(True)

        match env.name_rule:
            case NameRuleEnum.Front:
                self._ui.ruleRadio1.setChecked(True)
            case NameRuleEnum.Backend:
                self._ui.ruleRadio2.setChecked(True)
            case NameRuleEnum.FrontAndFolder:
                self._ui.ruleRadio1.setChecked(True)
                self._ui.ruleFolder.setChecked(True)
            case NameRuleEnum.BackAndFolder:
                self._ui.ruleRadio2.setChecked(True)
                self._ui.ruleFolder.setChecked(True)

    def _load_slot(self):

        self._ui.dirButton.clicked.connect(self._open_folder_dialog)
        self._ui.deleteButton.clicked.connect(self._open_file)
        self._ui.filterButton.clicked.connect(self._open_file)
        self._ui.forbidButton.clicked.connect(self._open_file)
        self._ui.nameButton.clicked.connect(self._rename)

        self._ui.customName.textChanged.connect(self._on_name_changed)
        self._ui.dirPath.textChanged.connect(self._on_path_changed)

        self._ui.filterCache.toggled.connect(self._on_filter_cache)
        self._ui.deleteCache.toggled.connect(self._on_delete_cache)
        self._ui.forbidCache.toggled.connect(self._on_forbid_cache)
        self._ui.filterFolder.toggled.connect(self._on_filter_folder)

    def _on_filter_cache(self) -> None:
        env.fs_cache = self._ui.filterCache.isChecked()

    def _on_delete_cache(self) -> None:
        env.ds_cache = self._ui.deleteCache.isChecked()

    def _on_forbid_cache(self) -> None:
        env.fb_cache = self._ui.forbidCache.isChecked()

    def _on_filter_folder(self) -> None:
        env.filter_folder = self._ui.filterFolder.isChecked()

    def _on_path_changed(self, text) -> None:
        env.str_path = text
        env.path = Path(env.str_path).resolve()
        if env.path.exists():
            self._load_tree_view(env.str_path)
        else:
            self._ui.originList.setModel(QFileSystemModel())

    @staticmethod
    def _on_name_changed(text):
        env.name = text

    def _rename(self):
        env.cleans.clear()
        env.fulls.clear()

        if not self._check():
            return

        self._ui.namedList.clear()
        ant.rename()
        if env.cleans:
            self._show_message(title='ANT | 清洁剂', message='\n'.join(env.cleans))
        self._ui.namedList.setPlainText('\n'.join(env.fulls))

    def _check(self):
        env.path = Path(env.str_path).resolve()
        if not env.path.exists() or not env.str_path:
            self._show_message(title='ANT | 错误提示', message=f'路径 {env.str_path} 不存在')
            return False

        self._check_texts()
        self._check_cache_radio()
        self._check_name_box()
        env.check()

        return True

    def _check_texts(self):
        def _split(texts):
            return [t.strip() for t in texts.split('\n') if t.strip()]
        env.fs = _split(self._ui.filters.toPlainText())
        env.ds = _split(self._ui.deletes.toPlainText())
        env.fbs = _split(self._ui.forbids.toPlainText())

    def _check_cache_radio(self):
        env.fs_cache = True if self._ui.filterCache.isChecked() else False
        env.ds_cache = True if self._ui.deleteCache.isChecked() else False

    def _check_name_box(self):
        pos = NamePositionEnum.Prefix if self._ui.ruleRadio1.isChecked() else NamePositionEnum.Suffix
        name_folder = True if self._ui.ruleFolder.isChecked() else False

        match pos:
            case NamePositionEnum.Prefix:
                if name_folder:
                    env.name_rule = NameRuleEnum.FrontAndFolder
                else:
                    env.name_rule = NameRuleEnum.Front
            case NamePositionEnum.Suffix:
                if name_folder:
                    env.name_rule = NameRuleEnum.BackAndFolder
                else:
                    env.name_rule = NameRuleEnum.Backend

    def _show_message(self, *, title, message):
        message_box = QMessageBox(self)
        message_box.setWindowIcon(QIcon(str(env.base_dir.joinpath('images/avatar.png'))))
        message_box.setWindowTitle(title)

        ok = message_box.addButton("OK", QMessageBox.ButtonRole.YesRole)
        message_box.setTextFormat(Qt.PlainText)
        message_box.setText(message)
        message_box.exec_()

        if message_box.clickedButton() == ok:
            clipboard = QApplication.clipboard()
            clipboard.setText(message_box.text())
            message_box.close()

    def _load_tree_view(self, p):
        model = QFileSystemModel()
        model.setRootPath(p)
        self._ui.originList.setModel(model)
        self._ui.originList.setRootIndex(model.index(p))

    def _open_file(self):

        file = QFileDialog.getOpenFileName(self, '选择文件', '', '(*.txt)')[0]
        datas = self.__parse_file(file)
        match self.sender().objectName():
            case 'filterButton':
                env.fs = datas
                self._ui.filters.setText('\n'.join(datas))
            case 'deleteButton':
                env.ds = datas
                self._ui.deletes.setText('\n'.join(datas))
            case 'forbidButton':
                env.fbs = datas
                self._ui.forbids.setText('\n'.join(datas))

    @staticmethod
    def __parse_file(file: str):
        with open(file, 'r', encoding='utf8') as f:
            datas = f.read()
        return [i.strip() for i in datas.split('\n') if i.strip()]

    def _open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", dir=str(env.path.parent) if env.str_path else '')
        self._ui.dirPath.setText(folder_path)
        env.str_path = folder_path
        env.path = Path(folder_path).resolve()
        self._load_tree_view(folder_path)

    def _close_op(self):
        self._check_texts()
        self._check_cache_radio()
        self._check_name_box()
        env.check()
        self.close()

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        self._close_op()

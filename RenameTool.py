import os
import sys
import threading
import time

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QApplication, QFileSystemModel, QFileDialog, QMessageBox

from tools import RuleEnum, CheckBoxEnum, name_tool


class MainWidget(QWidget):

    work_dir = r'./'

    def __init__(self):
        super(MainWidget, self).__init__()
        self._ui = None
        self._root = None
        self._rule = None
        self._prefix = False
        self._suffix = False
        self._custom_name = ''
        self._filters = []
        self._deletes = []
        self._check_box_state = {}
        self._binder = {}
        self._check_dir()
        self._load_ui()
        self._load_slot()
        self._check_cache()
        self._get_init_radio_value()
        self._loop_task()

    def _get_init_radio_value(self):
        self._prefix = self._ui.ruleRadio1.isChecked()
        self._suffix = self._ui.ruleRadio2.isChecked()

    def _check_dir(self):
        if not os.path.exists(self.work_dir):
            os.mkdir(self.work_dir)

    def _check_cache(self):
        ps = os.listdir(self.work_dir)
        if not ps:
            return
        for p in ps:
            match p:
                case "cache_filterList.txt":
                    self._reset_box_state(p, 'filterCache', 'filterList')
                case "cache_deleteList.txt":
                    self._reset_box_state(p, 'deleteCache', 'deleteList')
                case _:
                    pass

    def _reset_box_state(self, p, name, bind):
        box = getattr(self._ui, name)
        box.setChecked(True)

        area = getattr(self._ui, bind)
        area.clear()
        with open(f"{self.work_dir}{os.sep}{p}", 'r', encoding='utf8') as f:
            datas = f.read()
        area.append(datas)
        self._binder[bind] = [i.strip() for i in datas.split('\n')[1:] if i]

    def _loop_task(self):
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def _cache(self, name):
        text = getattr(self._ui, name).toPlainText()
        if text.startswith('请上传txt文件') or text.startswith('请注意'):
            return
        with open(f'{self.work_dir}{os.sep}cache_{name}.txt', 'w', encoding='utf8') as f:
            f.write(text)

    def _loop(self):
        while True:
            try:
                for k, v in self._check_box_state.items():
                    if v != CheckBoxEnum.CHECKED:
                        self._check_cache_file()
                    match k:
                        case 'filterCache':
                            self._cache('filterList')
                        case 'deleteCache':
                            self._cache('deleteList')
                        case _:
                            pass
            except Exception as e:
                print(f"loop task process error: ", e.args)
            time.sleep(5)

    def _check_cache_file(self):
        # TODO
        pass

    def _load_ui(self):
        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self._ui = loader.load(ui_file, self)
        ui_file.close()

    def _add_box_event(self, name, func='_get_box_value'):
        getattr(self._ui, name).stateChanged.connect(getattr(self, func))
        self._check_box_state[name] = CheckBoxEnum.DEFAULT

    def _add_button_event(self, name, func, bind=None):
        btn = getattr(self._ui, name)
        btn.clicked.connect(func)
        btn.setProperty('name', name)
        btn.setProperty('bind', bind)

    def _load_slot(self):
        self._add_button_event('dirButton', self._open_folder_dialog)
        self._add_button_event('deleteButton', self._open_file, bind='deleteList')
        self._add_button_event('filterButton', self._open_file, bind='filterList')
        self._add_button_event('nameButton', self._rename)
        self._ui.customName.textChanged.connect(self._on_name_changed)
        self._ui.ruleRadio1.toggled.connect(self._get_radio_value)
        self._ui.ruleRadio2.toggled.connect(self._get_radio_value)
        self._add_box_event('ruleFolder')
        self._add_box_event('filterFolder')
        self._add_box_event('filterCache')
        self._add_box_event('deleteCache')

    def _on_name_changed(self, text):
        self._custom_name = text

    def _rename(self):
        if not self._root:
            self._show_message(title='Error', message='未选择文件夹')
            return
        names = name_tool.rename(
            root=self._root, filters=self._binder.get('filterList', []), deletes=self._binder.get('deleteList', []),
            custom_name=self._custom_name, filter_folder=self._check_box_state.get('filterFolder'), prefix=self._prefix,
            suffix=self._suffix, rule_folder=self._check_box_state.get('ruleFolder')
        )
        self._ui.namedList.setPlainText('\n'.join(names))

    def _show_message(self, *, title, message):
        message_box = QMessageBox(self)
        message_box.setWindowTitle(title)
        message_box.setMinimumSize(200, 100)
        message_box.setText(message)
        # message_box.setIcon(QMessageBox.Information)
        message_box.exec()

    def _load_tree_view(self, p):
        if p:
            model = QFileSystemModel()
            model.setRootPath(p)
            self._ui.originList.setModel(model)
            self._ui.originList.setRootIndex(model.index(p))

    def _open_file(self):
        button = self.sender()
        bind = button.property("bind")
        try:
            self.file = QFileDialog.getOpenFileName(self, '选择文件', '', '(*.txt)')[0]
            self.file_type = self.file.rsplit('.', 1)[1]

            if bind:
                binder = getattr(self._ui, bind)
                binder.clear()
            else:
                binder = None
            self.__parse_file(bind, binder)
        except Exception as e:
            print(e.args)
            self._filters = None

    def __parse_file(self, bind, binder):
        with open(self.file, 'r', encoding='utf8') as f:
            datas = f.readlines()

        self._binder[bind] = [i.strip() for i in datas]

        if binder:
            binder.append('\n'.join(self._binder[bind]))

    def _get_radio_value(self):
        if self._ui.ruleRadio1.isChecked():
            self._prefix = True
            self._suffix = False
            self._rule = RuleEnum(self._ui.ruleRadio1.text()).name
        elif self._ui.ruleRadio2.isChecked():
            self._prefix = False
            self._suffix = True
            self._rule = RuleEnum(self._ui.ruleRadio2.text()).name
        else:
            self._rule = RuleEnum.DEFAULT.name

    def _get_box_value(self, state):
        for k in self._check_box_state.keys():
            if getattr(self._ui, k).isChecked():
                self._check_box_state[k] = CheckBoxEnum.CHECKED
            else:
                self._check_box_state[k] = CheckBoxEnum.UNCHECKED

    def _open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        self._ui.dirPath.setText(folder_path)
        self._root = folder_path
        self._load_tree_view(folder_path)


if __name__ == "__main__":
    app = QApplication([])
    widget = MainWidget()
    widget.setWindowTitle("文件夹批量命名小工具")
    widget.setMaximumSize(800, 640)
    widget.setMinimumSize(800, 640)

    widget.show()
    sys.exit(app.exec())

import os
import re
import shutil
from pathlib import Path

from ANT.env import env
from libs.enums import NamePositionEnum, NameRuleEnum


__all__ = ['ant']


class ANT:
    _num_cmp = re.compile(r'((\[\d+)(-+|\.)\d+](-+|\.+)\d+(-+|\.+)\d+)|(\d+(-+|\.+)\d+)|(\d+)')
    _chapter_cmp = re.compile(r'((\d{1,3}\.\d{1,2})|(\d{1,3}-\d{1,2})|(^\d+))')
    _chapter_content_cmp = re.compile(r'([\u4e00-\u9fa5].+)|([a-zA-Z].+)\S+')

    def __init__(self) -> None:

        self._error = None

    def _reload(self, name: str, pos: NamePositionEnum, rule: NameRuleEnum):
        self._name = name
        self._name_pos = pos
        self._name_rule = rule

    def _get_name_rule(self, *, pos: NamePositionEnum, include_folder: bool = False) -> None:
        match pos:
            case NamePositionEnum.Default:
                if include_folder:
                    self._name_rule = NameRuleEnum.Folder
                self._name_rule = NameRuleEnum.Default
            case NamePositionEnum.Prefix:
                if include_folder:
                    self._name_rule = NameRuleEnum.FrontAndFolder
                self._name_rule = NameRuleEnum.Front
            case NamePositionEnum.Suffix:
                if include_folder:
                    self._name_rule = NameRuleEnum.BackAndFolder
                self._name_rule = NameRuleEnum.Backend

    def rename(self, *, root: str):
        paths = os.listdir(root)
        for p in paths:
            if p.startswith('.') and env.ignore_hide:
                continue

            abs_path = Path(root + os.sep + p).resolve()
            if self._delete_check(abs_path):
                continue

            is_dir = os.path.isdir(abs_path)
            if is_dir:
                new_root = self._op_dir(abs_path, env.filter_folder)
                env.fulls.append(new_root.name)
                self.rename(root=str(new_root))
            else:
                self._op_file(abs_path)

    def _op_dir(self, path: Path, filter_folder: bool) -> Path:
        p = path.name.strip()
        if filter_folder:
            p = self._filter(p)

        env.cleans.append(p)
        p = self._get_new_name(p, folder=True)

        if p != path.name.strip():
            os.rename(path, path.parent.joinpath(p))

        return path.parent.joinpath(p)

    def _op_file(self, path: Path) -> None:
        p = path.name.strip()
        p = self._filter(p)

        dc = list(filter(lambda x: p.startswith(x), env.ds))
        if dc:
            os.remove(path)
            return

        chapter = self._chapter_cmp.search(p)
        chapter_content = self._chapter_content_cmp.search(p)

        new_name = ''
        if chapter:
            new_name += chapter[0] + '-'
        else:
            num = self._num_cmp.search(p)
            new_name = num[0] if num else ''

        if chapter_content:
            new_name += chapter_content[0]

        env.cleans.append(new_name)

        title, cat = new_name.rsplit('.', 1)
        if env.name in title and cat in env.fbs:
            title = title.replace(env.name, '')
        elif env.name and env.name not in title and cat not in env.fbs:
            title = self._get_new_name(title)

        new = Path(path.parent.joinpath(title + '.' + cat))
        os.rename(path, new)
        env.fulls.append(str(new.name))

    @staticmethod
    def _get_new_name(name, folder=False):
        if not name:
            return ''

        match folder:
            case True:
                if env.name_rule == NameRuleEnum.FrontAndFolder:
                    name = env.name + name
                elif env.name_rule == NameRuleEnum.BackAndFolder:
                    name += env.name
            case False:
                if env.name_rule in [NameRuleEnum.FrontAndFolder, NameRuleEnum.Front]:
                    name = env.name + name
                elif env.name_rule in [NameRuleEnum.BackAndFolder, NameRuleEnum.Backend]:
                    name += env.name
        return name

    @staticmethod
    def _delete_check(path: Path) -> bool:
        if path.name in env.ds:
            shutil.rmtree(str(path))
            return True
        return False

    def _forbid_check(self, path: Path):
        pass

    @staticmethod
    def _get_str_path(path: Path):
        return str(path)

    @staticmethod
    def _filter(name: str) -> str:
        for i in env.fs:
            if i in name:
                name = name.replace(i, '')
        return name


ant = ANT()

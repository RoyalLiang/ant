import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from libs.enums import NamePositionEnum, NameRuleEnum
from libs.tools import async_func


__all__ = ['env']


class WindowEnvModel(BaseModel):

    base_dir: Path = Field(default=Path(__file__).resolve().parent.parent, exclude=True)

    path: Path = Path().resolve()
    str_path: str = ''
    name: str = Field(default='', exclude=True)
    name_rule: NameRuleEnum = NameRuleEnum.Default
    filter_folder: bool = False
    ignore_hide: bool = True

    cleans: list = Field(default=[], exclude=True)
    fulls: list = Field(default=[], exclude=True)

    fs: list = Field(default=[], exclude=True)
    fbs: list = Field(default=[], exclude=True)
    ds: list = Field(default=[], exclude=True)
    fs_name: str = 'filters'
    fb_name: str = 'forbids'
    ds_name: str = 'deletes'

    fs_cache: bool = False
    ds_cache: bool = False
    fb_cache: bool = False

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._init()

    def _init(self):
        if self.base_dir.joinpath(f'.{self.fs_name}').exists() and self.fs_cache:
            self.fs = self._load(self.base_dir.joinpath(f'.{self.fs_name}'))

        if self.base_dir.joinpath(f'.{self.ds_name}').exists() and self.ds_cache:
            self.ds = self._load(self.base_dir.joinpath(f'.{self.ds_name}'))

        if self.base_dir.joinpath(f'.{self.fb_name}').exists() and self.fb_cache:
            self.fbs = self._load(self.base_dir.joinpath(f'.{self.fb_name}'))

    @staticmethod
    def _load(path: Path):
        with open(path, 'r', encoding='utf8') as f:
            data = f.read()
        return [i for i in data.split('\n') if i.strip()]

    def _cache(self, name: str, texts: list) -> None:
        with open(self.base_dir.joinpath(f'.{name}'), 'w', encoding='utf8') as f:
            f.write('\n'.join(texts))

    @async_func
    def check(self):

        if self.fs_cache:
            self._cache(self.fs_name, self.fs)
        elif not self.fs_cache and self.base_dir.joinpath(f'.{self.fs_name}').exists():
            os.remove(self.base_dir.joinpath(f'.{self.fs_name}'))

        if self.ds_cache:
            self._cache(self.ds_name, self.ds)
        elif not self.ds_cache and self.base_dir.joinpath(f'.{self.ds_name}').exists():
            os.remove(self.base_dir.joinpath(f'.{self.ds_name}'))

        if self.fb_cache:
            self._cache(self.fb_name, self.fbs)
        elif not self.fb_cache and self.base_dir.joinpath(f'.{self.fb_name}').exists():
            os.remove(self.base_dir.joinpath(f'.{self.fb_name}'))

        with open(self.base_dir.joinpath('.env'), 'w', encoding='utf8') as f:
            f.write(env.model_dump_json())


p = Path(__file__).resolve().parent.parent.joinpath('.env')
if p.exists():
    with open(p, 'r', encoding='utf8') as f:
        env = WindowEnvModel.model_validate_json(f.read())
else:
    env = WindowEnvModel(name='', name_pos=NamePositionEnum.Default, folder_selected=False)

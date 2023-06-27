import enum
import os
import re
import shutil
import traceback


forbid_cat_list = [
    'downloading', 'java', 'yaml', 'css', 'class', 'vmdk', 'py', 'xml', 'scss', 'js', 'properties', 'yml', 'cpp',
    'launch', 'json', 'STL', 'stl', 'xacro', 'rviz', 'world', 'h', 'msg', 'so', 'pyc', 'srv', 'vmdk', 'plist', 'lck',
    'rst', 'pkl', 'sh', 'scala', 'iml', 'rpm', 'go', 'conf', 'jar', 'log', 'exe', 'pid', 'lnk', 'vcxproj', 'filters',
    'lastbuildstate', 'idb', 'sln', 'sdf', 'suo', 'tlog', 'pdb', 'obj', 'log', 'ilk', 'ts', 'lrc', 'sv', 'svh', 'apk',
    'pak', 'mqb'

]


class RuleEnum(enum.Enum):

    DEFAULT = ''
    FRONT = '前'
    BACK = '后'


class CheckBoxEnum(enum.IntEnum):

    DEFAULT = -1
    CHECKED = 1
    UNCHECKED = 0


class RenameTool:

    named = []
    errors = []
    _cmp = re.compile(r"\d{3,6}\S{2,5}")
    _name_cmp = re.compile(r'(\d{1,3}\.\d{1,2})|(\d{1,3}-\d{1,2})')
    _chapter_cmp = re.compile(r'([\u4e00-\u9fa5].+)|([a-zA-Z].+)\S+')

    @staticmethod
    def _judge_folder(name, filters):
        name = name.split('--', 1)[-1]

        for i in filters:
            if i in name:
                name = name.replace(i, '')
        return name

    @staticmethod
    def _check_folder(name, custom_name, rule_folder, prefix, suffix):
        if not rule_folder:
            return name
        if prefix:
            name = custom_name + name
        elif suffix:
            name += custom_name
        return name

    @staticmethod
    def _delete_check(file, delete_list):
        is_delete = False
        if file.endswith('.url'):
            os.remove(file)
            is_delete = True
        else:
            for i in delete_list:
                if file.endswith(i) and i and file:
                    os.remove(file)
                    is_delete = True
                    break
        return is_delete

    @staticmethod
    def _get_name_additional(tmp):
        if (not tmp.startswith('--') or not tmp.startswith(' ')) and '--' in tmp:
            tmp = tmp.split('--', 1)[-1]
        return tmp

    def _get_chapter(self, tmp):
        r1, r2 = None, None
        name = self._name_cmp.search(tmp)
        chapter = self._chapter_cmp.search(tmp)

        if name:
            r1 = name[0]
        if chapter:
            r2 = chapter[0]
        return r1, r2

    def _remove(self, name):

        name = name.rsplit('.', 1)[0]
        words = self._cmp.search(name)
        if words:
            return words[0]
        return None

    def _rename_rule(self, old):
        word = self._remove(old)
        if word:
            old = old.replace(word, "")
        tmp = old.replace('_', '')
        return tmp.strip()

    def rename(self, *, root, filters, deletes, custom_name=None, filter_folder=False, ignores=None, prefix=False, suffix=True, rule_folder=False, **kwargs):

        paths = os.listdir(root)
        for p in paths:
            if p.startswith('.'):
                continue
            try:
                dir = root + os.sep + p
                is_dir = os.path.isdir(dir)
                if is_dir:
                    if p in deletes:
                        shutil.rmtree(dir)
                        continue
                    if filter_folder:
                        new_name = self._judge_folder(p, filters)
                    else:
                        new_name = p
                    new_name = self._check_folder(new_name, custom_name, rule_folder, prefix, suffix)
                    if new_name != p:
                        folder = root + os.sep + new_name
                        os.rename(dir, folder)
                    else:
                        folder = dir

                    self.named.append(new_name)
                    self.rename(root=folder, filters=filters, deletes=deletes, custom_name=custom_name, filter_folder=filter_folder, ignores=ignores, prefix=prefix, suffix=suffix, rule_folder=rule_folder, **kwargs)
                else:
                    self._rename_no_chapter(root, p, filters, deletes, custom_name, prefix, suffix)
            except:
                print(f'error: {traceback.format_exc()}')
                continue
        return self.named

    def _rename_no_chapter(self, path, file, filters, deletes, custom_name, prefix, suffix):
        old = path + os.sep + file
        is_delete = self._delete_check(old, deletes)
        if is_delete:
            return

        tmp = self._rename_rule(file)
        if '.' not in tmp:
            return

        flag, title = self._get_chapter(tmp)
        name = ''

        if flag:
            name += f'{flag}-'

        if title:
            name += title

        if not name:
            name = self._get_name_additional(tmp)

        for i in filters:
            if i in name:
                name = name.replace(i, '')

        name, cat = name.rsplit('.', 1)
        if custom_name not in name and cat not in forbid_cat_list:
            if prefix:
                name = custom_name + name
            elif suffix:
                name += custom_name
        elif custom_name in name and cat in forbid_cat_list:
            name = name.replace(custom_name, '')

        new = path + os.sep + name + '.' + cat
        # print(new)
        os.rename(old, new)
        self.named.append(name + '.' + cat)


name_tool = RenameTool()

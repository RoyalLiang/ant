import enum
import os
from pathlib import Path


class NamePositionEnum(enum.IntEnum):

    Default = 0
    Prefix = 1
    Suffix = 2


class NameRuleEnum(enum.IntEnum):

    Default = 0
    Front = 1
    Backend = 2
    Folder = 3
    FrontAndFolder = 4
    BackAndFolder = 5


if __name__ == '__main__':
    p = Path(r'D:\Projects\QT\name-tool' + os.sep + 'libs').resolve()
    # s = str(p).split(os.sep)
    # print(s)
    # print(os.sep.join(s))

    print(p.parent)
    x = p.parent.joinpath('haha')

    n = 'dsddfwf324ee2r,wsd3ef3e'
    n = n.replace(',', '')
    print(n)
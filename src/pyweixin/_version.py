'''
_version
========
`packaging.version` 的极简替代品。

pyweixin 只用到 `version.parse(a) >= version.parse(b)` 这种比较,而 `packaging`
在干净的无头 Linux 服务器上不一定装了。这里提供一个零依赖的回退实现:
把版本号按数字段拆成元组比较(4.1.13.29 -> (4,1,13,29))。
'''
from __future__ import annotations

import re

_SEGMENT = re.compile(r'\d+')


class Version(tuple):
    '''可比较的版本号元组。'''

    def __new__(cls, text):
        segments = tuple(int(x) for x in _SEGMENT.findall(str(text)))
        return super().__new__(cls, segments)

    def __str__(self):
        return '.'.join(str(x) for x in self)

    def __repr__(self):
        return f'Version({str(self)!r})'

    def _cmp(self, other):
        other = other if isinstance(other, Version) else Version(other)
        # 补齐长度,避免 (4,1) 与 (4,1,0) 被判定为不相等
        a = list(self)
        b = list(other)
        while len(a) < len(b):
            a.append(0)
        while len(b) < len(a):
            b.append(0)
        return (a > b) - (a < b)

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __eq__(self, other):
        try:
            return self._cmp(other) == 0
        except Exception:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    __hash__ = tuple.__hash__


def parse(text) -> Version:
    return Version(text)


class _VersionModule:
    '''模拟 `from packaging import version` 里的 `version` 对象。'''

    Version = Version
    parse = staticmethod(parse)


version = _VersionModule()

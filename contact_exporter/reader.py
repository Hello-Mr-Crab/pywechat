"""Contact reading abstraction over pyweixin (WeChat 4.x) public API.

The import of pyweixin is deferred until read_contacts() is called, so the
normalizer/exporter layers and the test suite can run without WeChat or
pywinauto installed.

This layer performs ONLY read-only UI automation via
``Contacts.get_friends_detail()``. No messaging, no mutation, no hooks,
no memory scanning, no database access.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger("contact_exporter")


class ContactReadError(RuntimeError):
    """Friendly error wrapping upstream WeChat UI-automation failures."""


# Upstream exceptions (src/pyweixin/Errors.py) translated to user-facing hints.
_UPSTREAM_ERRORS: dict[str, str] = {
    "NotStartError": "微信未启动，请先启动并登录微信后再运行导出工具。",
    "NotLoginError": "微信未登录，请先扫码登录后再运行导出工具。",
    "NotFoundError": (
        "无法定位微信主界面（UI 树不可见）。微信 4.1+ 需要使用过无障碍模式"
        "（讲述人）的账号；详见仓库内 Weixin4.0.md。"
    ),
    "NetWorkError": "当前网络不可用，无法进行 UI 自动化。",
    "NotInstalledError": "未找到微信注册表路径，可能未安装 PC 微信。",
}


@runtime_checkable
class ContactReader(Protocol):
    def read_contacts(self) -> list[dict[str, Any]]: ...


class PyWeixinContactReader:
    """Read contacts via pyweixin.Contacts.get_friends_detail (read-only)."""

    def __init__(self, interval: float = 0.1, close_weixin: bool = False) -> None:
        # close_weixin defaults False to avoid closing the user's WeChat.
        self.interval = interval
        self.close_weixin = close_weixin

    def read_contacts(self) -> list[dict[str, Any]]:
        try:
            from pyweixin import Contacts  # public API (delayed import)
        except Exception as e:  # pragma: no cover - environment dependent
            raise ContactReadError(f"无法导入 pyweixin：{e}") from e

        try:
            data = Contacts.get_friends_detail(
                interval=self.interval,
                is_maximize=False,
                close_weixin=self.close_weixin,
                is_json=False,
            )
        except Exception as e:
            name = type(e).__name__
            if name in _UPSTREAM_ERRORS:
                raise ContactReadError(_UPSTREAM_ERRORS[name]) from e
            raise ContactReadError(f"读取联系人失败：{e}") from e

        if isinstance(data, str):
            # Defensive: is_json=False normally returns list, but handle JSON too.
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = []
        if not isinstance(data, list):
            data = []

        logger.info("从 pyweixin 读取到 %d 条联系人", len(data))
        return data


class MockContactReader:
    """Returns canned data for tests / dry-run. No WeChat required."""

    def __init__(self, data: list[dict[str, Any]] | None = None) -> None:
        self._data: list[dict[str, Any]] = list(data) if data else []

    def read_contacts(self) -> list[dict[str, Any]]:
        return [dict(d) for d in self._data]


def reader_factory(backend: str = "pyweixin", **kwargs: Any) -> ContactReader:
    if backend == "pyweixin":
        return PyWeixinContactReader(**kwargs)
    if backend in ("mock", "dry-run"):
        return MockContactReader(**kwargs)
    raise ValueError(f"未知 backend: {backend}")

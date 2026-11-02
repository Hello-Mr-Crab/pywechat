# CONTACT_EXPORTER_IMPLEMENTATION_PLAN

> 代码勘察结论 + 实现计划（第一阶段：勘察，未修改核心代码）
> Base HEAD: `ebe8d4b`（origin/main）
> 分支: `feat/contact-exporter`

## 0. 勘察结论摘要

- 上游 `Hello-Mr-Crab/pywechat` 是 pywinauto / UI Automation 实现的 PC 微信 RPA 库（README 明确：不涉及逆向 Hook 操作）。
- 仓库内有两个包：
  - `src/pyweixin/`：适配微信 4.1.6+，当前主力维护（导出工具首选后端）。
  - `src/pywechat/`：适配微信 3.9.12.x 旧版。
- `Contacts.get_friends_detail()` 真实存在（两个包都有）。
- 当前仓库没有任何可复用的 CSV/TXT/JSON 联系人导出逻辑。
- 联系人读取是纯 UI Automation（点击/键盘导航/读取文本），无任何写操作、无 Hook、无数据库访问。

## 1. Current API Findings（12 问逐一回答）

### 1.1 当前最新版联系人读取 API 的准确 import 路径是什么？

主力后端（微信 4.x）：
```python
from pyweixin import Contacts                # 由 pyweixin/__init__.py 导出
from pyweixin.WeChatAuto import Contacts     # 等价
```
旧版后端（微信 3.9.x，本机 import 失败，见 2.4）：
```python
from pywechat.WeChatAuto import Contacts
```

### 1.2 Contacts.get_friends_detail() 是否真实存在？
是。验证于：
- `src/pyweixin/WeChatAuto.py` class Contacts（行 774）-> get_friends_detail（行 1038）
- `src/pywechat/WeChatAuto.py` class Contacts（行 4917）-> get_friends_detail（行 5137）
- 本机 `hasattr(Contacts,'get_friends_detail')` -> True（pyweixin）。

### 1.3 函数签名是什么？
```python
# pyweixin（微信 4.x，主力）
@staticmethod
def get_friends_detail(
    interval: float = 0.1,          # 遍历停留间隔（秒）
    is_maximize: bool = None,       # 主界面是否全屏；None->GlobalConfig.is_maximize（默认 False）
    close_weixin: bool = None,      # 结束是否关微信；None->GlobalConfig.close_weixin（默认 False）
    is_json: bool = False,          # 是否返回 JSON 字符串
) -> (list[dict] | str)

# pywechat（微信 3.9.x，旧版）
@staticmethod
def get_friends_detail(
    is_json: bool = False, is_maximize: bool = None, close_wechat: bool = None,
) -> str
```

### 1.4 返回类型是什么？
- `is_json=False`（默认）-> list[dict]（每个 dict 一个联系人字段映射）。
- `is_json=True` -> json.dumps(ensure_ascii=False, indent=2) 字符串。
- 空/无联系人分区时可能返回 []。

### 1.5 返回联系人字段有哪些？
pyweixin get_friends_detail 的 dict 键（缺失字段值为 '无'）：

| dict 键 | 含义 | 导出字段 |
| --- | --- | --- |
| 昵称 | 昵称 | nickname |
| 微信号 | 微信号 | wechat_id |
| 地区 | 地区 | region |
| 备注 | 备注 | remark |
| 电话 | 手机号 | phone |
| 标签 | 标签 | tags |
| 来源 | 好友来源 | source |
| 描述 | 描述 | 预留 |
| 朋友权限 | 朋友权限 | 预留 |
| 共同群聊 | 共同群聊 | 预留 |
| 个性签名 | 个性签名 | 预留 |

同类的其他方法：get_friends_info（快速取备注名 list[str]）、get_wecom_friends_detail（企业微信）、get_serAcc_detail / get_offAcc_detail（服务号/公众号）、get_tags（list[tuple[str,int]]，最新提交新增）。

### 1.6 微信未启动时会发生什么？
`Tools.is_weixin_running()` 检测 Weixin.exe 进程；`Navigator.open_weixin()` 未启动时 raise `NotStartError`（"微信未启动,请先启动并登录微信后再使用pyweixin!"）。可预期异常：
- 窗口类为 mmui::LoginWindow -> `NotLoginError`（已启动未登录）
- 检测到离线按钮 -> `NetWorkError`
- 主窗口无法识别 -> `NotFoundError`（UI 树不可见）
异常定义在 src/pyweixin/Errors.py。

### 1.7 UI Automation 不可访问时会发生什么？
`Navigator.open_weixin` 找不到 mmui::MainWindow 时 raise `NotFoundError`。根因（README/Weixin4.0.md）：微信 4.1+ 收紧了无障碍策略，只有使用过无障碍模式（讲述人）的账号 UI 树才可见；从未使用过的新号无法通过 UI Automation 读取（官方推荐 OCR RPA）。这是上游项目本身的硬性限制，导出工具需透明传播并在报错中给出可执行提示。

### 1.8 是否需要逐联系人打开资料页？
不是。get_friends_detail 的实现：
1. Navigator.open_contacts() 打开通讯录面板（主窗口内）。
2. 点击联系人分区，click_input() 选中第一个好友。
3. for 循环内 pyautogui.keyDown('down') 逐个移动选中项，同时读取右侧常驻详情面板（ContactProfileGroup / auto_id=contact_profile_view）文本。
即：主窗口内的列表选中 + 右侧面板读取，不打开独立窗口、不进入编辑态。

### 1.9 当前实现是否会执行任何微信侧写操作？
不会。get_friends_detail 全程只做：窗口定位/置前、点击通讯录入口、键盘导航（DOWN）、读取 UI 文本、按参数关闭窗口。无发消息/加好友/改备注/拉群/朋友圈/资料编辑。close_weixin 默认 False，不会关闭用户微信。且 get_friends_detail 本身不调用 Tools.get_current_wxid()，不读取进程内存映射、不触碰微信数据库。

### 1.10 当前实现对微信版本有什么限制？
- pyweixin：微信 4.1.6+；部分 UI 分支按 GlobalConfig.Version >= 4.1.12 切换；Windows 10/11。
- pywechat：微信 3.9.12.x。
- 语言：简中 / English / 繁中（自动检测）。
- Python >= 3.10。本机 3.13.15 满足。

### 1.11 当前项目是否已有 CSV/JSON/TXT 导出逻辑可以复用？
没有。仓库内无联系人 CSV/TXT/JSON 导出模块。pyweixin.Notes2MD.py 是笔记转 Markdown，无关。get_friends_detail(is_json=True) 只提供序列化，不含文件写入。导出逻辑需新建。

### 1.12 哪些代码最适合保持独立，避免污染上游核心逻辑？
- 新增独立顶层包 contact_exporter/（reader/normalizer/exporter/cli/models/logging），只通过上游公开 API（Contacts.get_friends_detail）读取。
- 新增根级入口 export_contacts.py。
- 新增 tests/（纯本地，mock 读取层）。
- 只改一个上游文件：.gitignore（增加 output/、logs/、*.egg-info/ 精确规则）。
- 不改 src/pyweixin/、src/pywechat/、Mcp/、Skill/。

## 2. Compatibility

| 项 | 支持 | 说明 |
| --- | --- | --- |
| 操作系统 | Windows 10 / 11 | 上游 pyweixin 要求 |
| Python | >= 3.10（本机 3.13.15） | TypeHint 语法 |
| 微信版本 | 4.1.6+（pyweixin 主力）；3.9.12.x（pywechat 可选） | |
| UI 树可见性 | 必须可见 | 未启用无障碍模式的账号会 NotFoundError |
| 登录状态 | 必须已登录 | 未启动->NotStartError；未登录->NotLoginError |
| 语言 | 简中 / English / 繁中 | 上游自动检测 |
| 无微信环境 | 工具可导入、测试可运行 | reader 层延迟导入 pyweixin |

### 2.4 实测环境（本机）注意
- pyweixin 包可正常 import（无需微信 4.x 安装）。
- pywechat（3.9 旧版）import 即抛 NotInstalledError（本机未装 3.9 微信、注册表缺失）-> 导出工具默认并首选 pyweixin 后端。

## 3. Proposed Architecture

分层：
- reader 只负责从上游 API 拿到原始 list[dict]；适配到 models.Contact 之前在 normalizer 完成。
- normalizer / exporter 不 import pyweixin，保证可单测、可在无微信环境运行。
- cli 只编排，不包含业务逻辑。

目录结构（结合原项目实际：根级 src-layout + Mcp/Skill）：
```
pywechat/
|- contact_exporter/          # 新增独立包（不进入 pywechat127 发行包）
|  |- __init__.py
|  |- cli.py
|  |- reader.py
|  |- normalizer.py
|  |- exporter.py
|  |- models.py
|  |- logging_config.py
|- tests/
|  |- test_normalizer.py
|  |- test_exporter.py
|  |- fixtures/sample_contacts.json
|- output/                    # gitignore
|- logs/                      # gitignore
|- export_contacts.py         # 入口
|- PRD_WECHAT_CONTACT_EXPORTER.md
|- CONTACT_EXPORTER_IMPLEMENTATION_PLAN.md
|- README_CONTACT_EXPORTER.md
|- .gitignore                 # 唯一改动（追加精确规则）
|- src/ Mcp/ Skill/ ...       # 上游，不动
```
> 不把 contact_exporter 放进 src/：避免改动上游打包配置，保证 100% 附加式、零侵入。

## 4. Files To Add

| 文件 | 职责 |
| --- | --- |
| contact_exporter/__init__.py | 包标识、版本、__all__ |
| contact_exporter/models.py | Contact dataclass、EXPORT_FIELDS 字段顺序 |
| contact_exporter/reader.py | ContactReader 协议、PyWeixinContactReader（延迟导入）、MockContactReader、reader_factory |
| contact_exporter/normalizer.py | normalize()：中文键->英文键、'无'/None/''->''、deduplicate |
| contact_exporter/exporter.py | export_csv / export_txt / export_all；时间戳文件名、不覆盖旧文件、UTF-8 BOM |
| contact_exporter/cli.py | argparse CLI（format/output-dir/deduplicate/verbose） |
| contact_exporter/logging_config.py | 控制台+文件日志、PII 脱敏 |
| export_contacts.py | 根级入口 |
| tests/test_normalizer.py | normalizer 单元测试 |
| tests/test_exporter.py | CSV/TXT 导出单元测试 |
| tests/fixtures/sample_contacts.json | 模拟上游返回数据 |
| PRD_WECHAT_CONTACT_EXPORTER.md | 需求基线 |
| CONTACT_EXPORTER_IMPLEMENTATION_PLAN.md | 本文件 |
| README_CONTACT_EXPORTER.md | 使用说明 |

## 5. Files To Modify

| 文件 | 改动 | 风险 |
| --- | --- | --- |
| .gitignore | 追加 output/、logs/、*.egg-info/（精确规则，不用 *.txt） | 低；避免误伤上游需要版本控制的 .txt |

上游 src/pywechat/、src/pyweixin/、Mcp/、Skill/ 零改动。

## 6. Risk Boundary

| 风险 | 描述 | 处置 |
| --- | --- | --- |
| 微信未运行 / 未登录 | NotStartError / NotLoginError | 转友好错误，退出码非 0，不写文件 |
| UI 树不可见 | NotFoundError | 报错并给出指引；属上游硬限制 |
| 网络不可用 | NetWorkError | 透传报错 |
| 微信版本不符 | 4.1.6 以下缺 UI | 报错提示版本要求 |
| 字段缺失 | 无备注/微信号 | 留空，不终止；'无' 视为空 |
| 重复联系人 | 同名/同微信号 | 默认按微信号去重 |
| 隐私 | 手机号/微信号 | 日志脱敏；output/logs 不进 Git |
| 覆盖旧文件 | 同秒重复运行 | 自动追加序号，不覆盖 |

安全边界确认：本方案只调用 Contacts.get_friends_detail()（UI Automation 只读）+ 本地文件 IO。不引入 Hook、注入、进程内存扫描、数据库密钥提取/解密、非官方协议、消息发送、联系人修改。若导出字段必须依赖禁止能力，则该字段留空并在日志提示。

## 7. Test Plan

| 用例 | 文件 | 断言要点 |
| --- | --- | --- |
| normalizer 基本映射 | test_normalizer.py | 中文键->英文键正确 |
| None 字段 | test_normalizer.py | None/'无'/缺失->'' |
| 中文 | test_normalizer.py | 中文值完整保留 |
| 特殊字符 | test_normalizer.py | 逗号/引号/换行不破坏结构 |
| 重复联系人 | test_normalizer.py | deduplicate=True 去重；False 保留 |
| 空联系人 | test_exporter.py | 仍产出含表头的文件 |
| CSV exporter | test_exporter.py | UTF-8 BOM、表头、行内容 |
| TXT exporter | test_exporter.py | 备注/昵称/微信号/手机号/地区/标签 竖线分隔 |
| 不覆盖旧文件 | test_exporter.py | 已存在->追加 _1/_2，不覆盖 |
| reader（mock） | test_normalizer.py | MockContactReader 喂入固定数据 |

运行：python -m pytest tests/ -v（无需微信；pyweixin 延迟导入保证 import 安全）。

## 8. Acceptance Mapping

| PRD 条目 | 实现位置 | 验收方式 |
| --- | --- | --- |
| python export_contacts.py --format csv | cli+exporter | 集成冒烟（mock reader） |
| --format txt / all | cli+exporter | 同上 |
| --output-dir | cli | 文件落在指定目录 |
| --deduplicate（默认 true） | normalizer | 单元测试 |
| --verbose | logging_config | 日志级别切换 |
| 字段 8 项 | models/normalizer | 表头与 CSV 行验证 |
| UTF-8 BOM | exporter | 文件头 EF BB BF |
| 不覆盖旧文件 | exporter | 单元测试 |
| 隐私（gitignore） | .gitignore | git check-ignore output logs |
| mock 测试（不依赖微信） | tests | pytest 全绿 |

## 9. 后续提交计划（小步提交）

```text
docs: add contact exporter product requirements
docs: add contact exporter implementation plan
feat: add contact reader abstraction
feat: add csv and txt contact exporters
feat: add contact exporter cli
test: add contact exporter tests
docs: add contact exporter usage guide
```

不 push 上游，仅本地分支。

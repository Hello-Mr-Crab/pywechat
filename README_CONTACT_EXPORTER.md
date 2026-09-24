# 微信联系人导出工具 (Contact Exporter)

本地、**只读** 地把当前登录微信账号的联系人导出为 CSV / TXT。
基于 `Hello-Mr-Crab/pywechat` 的 `pyweixin` 包（UI Automation，不修改微信、无 Hook/注入/数据库解密）。

## 安全边界

本工具仅：

- 调用 `pyweixin.Contacts.get_friends_detail()`（UI Automation 只读）
- 本地数据清洗与 CSV/TXT 文件输出
- 本地日志（默认脱敏手机号）

**不会**：发消息、加好友、改备注、拉群、发朋友圈、Hook、DLL 注入、内存扫描、
数据库密钥提取/解密、非官方协议登录、风控绕过。

## 环境要求

- Windows 10 / 11
- Python >= 3.10
- 微信 4.1.6+（pyweixin）；已登录且 **UI 树可见**（需使用过无障碍模式/讲述人的账号，详见 `Weixin4.0.md`）
- 已安装本仓库依赖：`pip install -r src/requirements.txt` + `pip install -e src/`

## 快速使用

在仓库根目录：

```powershell
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 导出 CSV（默认）
python export_contacts.py --format csv

# 导出 TXT
python export_contacts.py --format txt

# 同时导出 CSV + TXT
python export_contacts.py --format all

# 关闭去重
python export_contacts.py --format csv --no-deduplicate

# 指定输出目录
python export_contacts.py --format csv --output-dir D:\my-exports

# 详细日志（微信号 OCR 候选始终脱敏）
python export_contacts.py --format csv --verbose
```

## 无微信环境冒烟测试（mock）

```powershell
python export_contacts.py --format csv --backend mock --mock-data tests/fixtures/sample_contacts.json --verbose
```

## 参数

| 参数 | 可选值 | 默认 | 说明 |
| --- | --- | --- | --- |
| `--format` | `csv` / `txt` / `all` | `csv` | 输出格式 |
| `--output-dir` | 路径 | `./output` | 输出目录 |
| `--deduplicate` / `--no-deduplicate` | - | `true` | 按微信号去重 |
| `--verbose` | - | `false` | 详细日志（含 PII） |
| `--backend` | `pyweixin` / `mock` | `pyweixin` | 读取后端 |
| `--mock-data` | JSON 路径 | - | mock 后端数据文件 |

## 导出字段

`nickname, remark, wechat_id, phone, region, tags, source, exported_at`

CSV appends `wechat_id_status`, `wechat_id_source`, `wechat_id_confidence`,
`wechat_id_reason`, and `wechat_id_candidate`; TXT includes the same review
fields after the existing columns. Only `CONFIRMED` records fill `wechat_id`;
legacy input without a confirmation status fails closed.

无法获取的字段留空，不伪造，不因单字段缺失终止。

## 输出

- `output/wechat_contacts_YYYYMMDD_HHMMSS.csv`（UTF-8 BOM，Excel/WPS 中文正常，首行表头）
- `output/wechat_contacts_YYYYMMDD_HHMMSS.txt`（UTF-8 BOM，包含微信号状态和来源）

微信号 OCR runtime/model installation, offline behavior, statuses, and
limitations are documented in [`docs/wechat-id-ocr.md`](docs/wechat-id-ocr.md).
- 同名文件已存在时自动追加 `_1`/`_2` 后缀，**不覆盖旧文件**。

## 隐私

- `output/` 与 `logs/` 已在 `.gitignore` 中忽略，不会进入版本控制。
- 联系人完整记录不会写入日志；微信号诊断即使在 debug 模式也只记录脱敏值。

## 常见错误

| 报错 | 原因与处理 |
| --- | --- |
| 微信未启动 | 先启动并登录微信 |
| 微信未登录 | 扫码登录后再运行 |
| 无法定位微信主界面（UI 树不可见） | 账号未启用无障碍模式；见 `Weixin4.0.md` |
| 当前网络不可用 | 检查网络后重试 |

## 测试

```powershell
python -m pytest tests/ -v
```

测试通过 mock 读取层，**不要求真实微信登录**。

## 目录结构

```
src/pyweixin/ocr/      # 微信号专用 OCR-primary 与 UIA-secondary 实现
contact_exporter/      # CSV/TXT 导出层与 fail-closed normalizer
  __init__.py
  cli.py
  reader.py
  normalizer.py
  exporter.py
  models.py
  logging_config.py
export_contacts.py     # 入口
tests/                 # 单元测试（mock）
output/                # 导出文件（gitignore）
logs/                  # 日志（gitignore）
```

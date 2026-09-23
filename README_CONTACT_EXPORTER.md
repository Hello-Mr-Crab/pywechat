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

# 详细日志（注意：可能打印手机号/微信号）
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

无法获取的字段留空，不伪造，不因单字段缺失终止。

## 输出

- `output/wechat_contacts_YYYYMMDD_HHMMSS.csv`（UTF-8 BOM，Excel/WPS 中文正常，首行表头）
- `output/wechat_contacts_YYYYMMDD_HHMMSS.txt`（UTF-8 BOM，`备注 | 昵称 | 微信号 | 手机号 | 地区 | 标签`）
- 同名文件已存在时自动追加 `_1`/`_2` 后缀，**不覆盖旧文件**。

## 隐私

- `output/` 与 `logs/` 已在 `.gitignore` 中忽略，不会进入版本控制。
- 日志默认脱敏手机号；`--verbose` 才会打印详情。

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
contact_exporter/      # 独立附加包（不侵入上游 src/）
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

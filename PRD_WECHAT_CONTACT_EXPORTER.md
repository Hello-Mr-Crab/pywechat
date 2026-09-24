# PRD — 微信联系人 CSV/TXT 导出工具 (WeChat Contact Exporter)

> 需求基线文档。本文件是唯一需求基线；超出本文件范围的需求需另行评审。

## 1. 背景与目标

基于 `Hello-Mr-Crab/pywechat` 项目已有的联系人读取能力（pywechat / pyweixin），
为当前登录的 PC 微信账号提供一个 **本地、只读、无侵入** 的联系人导出工具：

- 读取当前登录微信账号的联系人（仅读取，不写入）
- 本地数据清洗（去重、缺失字段留空）
- 本地 CSV / TXT 文件输出
- 本地日志
- 自动化测试（mock 联系人读取层，不要求真实微信登录）

## 2. 硬性约束（安全边界）

只允许：

- 读取当前登录微信账号的联系人
- 调用 pywechat / pyweixin 已有联系人读取能力
- 本地数据清洗
- 本地 CSV/TXT 文件输出
- 本地日志
- 自动化测试

严格禁止：

- 自动发消息、群发、自动加好友、自动通过好友、修改联系人、修改备注、自动拉群、自动朋友圈
- Hook 微信、DLL 注入、微信进程内存扫描
- 数据库密钥提取、微信数据库解密
- 非官方微信协议登录、风控绕过、封号规避

如果联系人导出必须依赖上述禁止能力，则**不实现**，直接报告阻塞原因。

## 3. MVP 范围

命令行入口（项目根目录）：

```powershell
python export_contacts.py --format csv
python export_contacts.py --format txt
python export_contacts.py --format all
```

参数：

| 参数 | 可选值 | 默认 | 说明 |
| --- | --- | --- | --- |
| `--format` | `csv` / `txt` / `all` | `csv` | 输出格式 |
| `--output-dir` | 路径 | `./output` | 输出目录 |
| `--deduplicate` / `--no-deduplicate` | - | `true` | 是否按微信号去重 |
| `--verbose` | - | `false` | 详细日志；微信号始终脱敏 |

## 4. 导出字段

| 导出字段 | 含义 | 来源（pyweixin API 中文键） |
| --- | --- | --- |
| `nickname` | 昵称 | `昵称` |
| `remark` | 备注 | `备注` |
| `wechat_id` | 微信号 | `微信号` |
| `phone` | 手机号 | `电话` |
| `region` | 地区 | `地区` |
| `tags` | 标签 | `标签` |
| `source` | 来源 | `来源` |
| `exported_at` | 导出时间（本地生成） | - |
| `wechat_id_status` | `CONFIRMED` / `NEED_REVIEW` / `NOT_FOUND` / `OCR_FAILED` | `微信号状态` |
| `wechat_id_source` | `ocr` / `ocr+uia` / `uia` / `none` | `微信号来源` |
| `wechat_id_confidence` | 两视图最低置信度 | `微信号置信度` |
| `wechat_id_reason` | 确认/复核原因 | `微信号原因` |
| `wechat_id_candidate` | 未确认的候选值，仅供人工复核 | `微信号候选` |

规则：

- 无法获取则留空
- 不伪造数据
- 不因单个字段缺失终止整个任务
- `wechat_id` 仅在状态为 `CONFIRMED` 且语法校验通过时写入；其它候选只写在独立的 `wechat_id_candidate` 字段
- 缺少显式确认状态的旧格式记录 fail-closed，不能把原始微信号写入正式字段
- 保留对未来字段扩展的兼容性

## 5. 输出格式

CSV（`output/wechat_contacts_YYYYMMDD_HHMMSS.csv`）：

- UTF-8 BOM
- Excel / WPS 中文显示正常
- 第一行为表头

TXT（`output/wechat_contacts_YYYYMMDD_HHMMSS.txt`）：

- UTF-8 BOM（保证 Windows 记事本/Excel 中文正常）
- 每行包含基础联系人字段和微信号状态、来源、置信度、原因、候选值

## 6. 隐私保护

- `output/`、`logs/` 不进入 Git（在 `.gitignore` 增加精确规则）
- 日志不打印完整微信号或整个联系人对象；微信号诊断始终脱敏

## 7. 测试要求

至少覆盖：

- normalizer 单元测试
- CSV exporter 单元测试
- TXT exporter 单元测试
- 空联系人
- None 字段
- 中文
- 特殊字符
- 重复联系人
- 不覆盖旧文件

联系人读取层通过 mock 测试；CI/自动化测试不要求真实微信登录。

## 8. 交付物

- `contact_exporter/` 附加模块（不侵入上游 `src/pywechat` / `src/pyweixin`）
- `export_contacts.py` 入口脚本
- `tests/` 自动化测试
- `CONTACT_EXPORTER_IMPLEMENTATION_PLAN.md` 实现计划
- `README_CONTACT_EXPORTER.md` 使用说明
- `CONTACT_EXPORTER_COMPLETION_REPORT.md` 验收报告

## 9. 非目标（超出 MVP，不做）

- 导出聊天记录
- 批量导入联系人
- 同步到第三方通讯录
- 云同步 / Web 服务
- OCR 兜底读取（当 UI 树不可见时）

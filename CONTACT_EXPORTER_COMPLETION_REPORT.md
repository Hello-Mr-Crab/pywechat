# CONTACT_EXPORTER_COMPLETION_REPORT

## Repository
- 仓库: https://github.com/Hello-Mr-Crab/pywechat.git
- 本地路径: D:\Projects\pywechat
- Remote: origin -> https://github.com/Hello-Mr-Crab/pywechat.git (未 push 上游)

## Branch
- 当前分支: feat/contact-exporter
- 默认/基线分支: main (origin/main)

## Base HEAD
- ebe8d4b  修改pull_messages相关的方法的稳定性  (origin/main, merge-base)

## Final HEAD
- a9e4eec  docs: add contact exporter completion report  （本报告所在提交）
- 最后一个功能/文档交付提交: e13b46c  docs: add contact exporter usage guide
- 说明: 本报告由 a9e4eec 引入；此后如再修订本报告（例如 docs-only 修正提交），
  分支 tip 会前进，请以 `git rev-parse feat/contact-exporter` 为最终事实来源。

## Modified files
| 文件 | 改动 |
| --- | --- |
| .gitignore | +output/ +logs/ +*.egg-info/ +.pytest_cache/ +.venv/ +!tests/ 例外规则（仅 1 个上游文件被修改） |

上游 src/pywechat/、src/pyweixin/、Mcp/、Skill/、setup.py、pyproject.toml **零改动**。

## Added files
- PRD_WECHAT_CONTACT_EXPORTER.md
- CONTACT_EXPORTER_IMPLEMENTATION_PLAN.md
- README_CONTACT_EXPORTER.md
- contact_exporter/__init__.py
- contact_exporter/models.py
- contact_exporter/reader.py
- contact_exporter/normalizer.py
- contact_exporter/exporter.py
- contact_exporter/cli.py
- contact_exporter/logging_config.py
- export_contacts.py
- tests/conftest.py
- tests/fixtures/sample_contacts.json
- tests/test_normalizer.py
- tests/test_exporter.py

## Actual pyweixin contact API used
- import: `from pyweixin import Contacts`（等价 `from pyweixin.WeChatAuto import Contacts`）
- 调用: `Contacts.get_friends_detail(interval=0.1, is_maximize=False, close_weixin=False, is_json=False)`
  -> 返回 `list[dict]`，键：昵称/微信号/地区/备注/电话/标签/来源/描述/朋友权限/共同群聊/个性签名（缺失为 '无'）
- 仅读取，无写操作；延迟导入，使 normalizer/exporter/tests 不依赖微信/pywinauto。

## Supported export formats
- csv (默认), txt, all（csv+txt）
- CSV: UTF-8 BOM，首行表头，Excel/WPS 中文正常
- TXT: UTF-8 BOM，`备注 | 昵称 | 微信号 | 手机号 | 地区 | 标签`

## Export fields
nickname, remark, wechat_id, phone, region, tags, source, exported_at
（缺失留空，不伪造；字段顺序稳定，可追加扩展）

## Tests executed
命令: `.venv\Scripts\python.exe -m pytest tests/ -v`

| 用例 | 结果 |
| --- | --- |
| test_basic_key_mapping | PASS |
| test_none_and_sentinel_fields_become_empty | PASS |
| test_missing_keys_default_empty | PASS |
| test_clean_helper | PASS |
| test_chinese_values_preserved | PASS |
| test_special_characters_do_not_break_structure | PASS |
| test_deduplicate_default_drops_duplicates | PASS |
| test_no_deduplicate_keeps_all | PASS |
| test_deduplicate_by_nickname_when_no_wechat_id | PASS |
| test_export_fields_order_stable | PASS |
| test_non_dict_entries_skipped | PASS |
| test_empty_input | PASS |
| test_mock_reader_feeds_normalizer | PASS |
| test_csv_has_utf8_bom | PASS |
| test_csv_header_row | PASS |
| test_csv_row_content | PASS |
| test_csv_chinese_values | PASS |
| test_csv_special_characters_safe | PASS |
| test_csv_empty_contacts_still_has_header | PASS |
| test_txt_has_utf8_bom | PASS |
| test_txt_header_and_format | PASS |
| test_txt_empty_contacts_has_header_only | PASS |
| test_csv_does_not_overwrite_existing | PASS |
| test_txt_does_not_overwrite_existing | PASS |
| test_export_all_timestamps_match | PASS |
| test_none_fields_render_as_empty_in_csv | PASS |
| test_output_dir_created | PASS |

## Test results
- 27 passed in 0.08s（0 失败）
- 联系人读取层通过 mock，CI/自动化测试不要求真实微信登录。

## Known compatibility limitations
- 微信版本: 4.1.6+（pyweixin）；旧版 3.9.12.x 走 pywechat（本机未装 3.9，import 失败，故默认 pyweixin）。
- UI 树可见性: 微信 4.1+ 需“使用过无障碍模式（讲述人）的账号”，否则 `NotFoundError`（上游硬限制，非本工具可解）。
- 必须已登录: 未启动→NotStartError；未登录→NotLoginError；断网→NetWorkError。
- 操作系统: Windows 10/11。
- 终端中文显示为 mojibake 仅因 Windows 控制台代码页；文件内容为 UTF-8（BOM 已验证）。

## Safety boundary verification
- 仅调用 `Contacts.get_friends_detail()`（UI Automation 只读：点击通讯录入口 + 键盘 DOWN 导航 + 读取右侧详情面板文本）。
- `close_weixin=False`，不关闭用户微信。
- 不调用 `Tools.get_current_wxid()`/`where_wxid_folder`，不读进程内存映射、不碰微信数据库。
- reader 层延迟导入 pyweixin，normalizer/exporter/tests 仅依赖标准库。
- output/ 与 logs/ 已 gitignore；日志默认脱敏手机号。

## Remaining issues
- 真机端到端（真实微信登录读取）未在本机执行（环境无 UI 树可见账号）；读取层已用 mock 验证完整链路，真实读取行为完全委托上游公开 API。
- pywechat(3.9) 后端未接入 CLI（本机 import 即失败）；如需可后续加 `--backend pywechat`，但需 3.9 微信环境。

## Exact run commands
```powershell
cd D:\Projects\pywechat
.\.venv\Scripts\Activate.ps1

# 测试
python -m pytest tests/ -v

# 真实导出（需微信 4.1.6+ 已登录且 UI 树可见）
python export_contacts.py --format csv
python export_contacts.py --format txt
python export_contacts.py --format all

# 无微信环境冒烟（mock）
python export_contacts.py --format csv --backend mock --mock-data tests/fixtures/sample_contacts.json --verbose

# 去重/目录/日志
python export_contacts.py --format csv --no-deduplicate --output-dir D:\exports --verbose
```

## 提交历史（本地，未 push）
```
a9e4eec docs: add contact exporter completion report
e13b46c docs: add contact exporter usage guide
faad01e feat: add mock-data option to contact exporter cli
72848bd test: add contact exporter tests
3dd261f feat: add contact exporter cli
6354168 feat: add csv and txt contact exporters
d4cd49c feat: add contact reader abstraction
527fb73 docs: add contact exporter implementation plan
4ae3e94 docs: add contact exporter product requirements
ebe8d4b (origin/main) 修改pull_messages相关的方法的稳定性
```

---

## 安全声明

是否存在 Hook：NO
是否存在 DLL 注入：NO
是否读取微信数据库：NO
是否提取数据库密钥：NO
是否发送微信消息：NO
是否修改微信联系人：NO
是否仅执行联系人读取和本地文件导出：YES

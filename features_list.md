# feature_list

## Changed

| 位置 | 修改内容 |
| :--- | :--- |
| \src\pyweixin\WeChatAuto.py\Class Messages pull_messages | **新的聊天列表消息导出方式,更快更稳定** |
| \src\pyweixin\WeChatAuto.py\Class Messages dump_chat_history | **新的聊天记录消息导出方式，更快更稳定** |
| \src\pyweixin\WeChatAuto.py\Class Contacts check_my_info | **增加保存头像选项** |
| \src\pyweixin\WeChatAuto.py\Class Contacts get_friend_profile | **增加保存头像选项** |
| \src\pyweixin\WeChatAuto.py\Class Collections collect_offAcc_articles | **修改公众号链接获取方式** |
| \src\pyweixin\WeChatAuto.py\Class Messages send_messages_to_friend | **移除clear参数** |
| \src\pyweixin\WeChatAuto.py\Class Messages send_messages_to_friends | **移除clear参数** |
| \src\pyweixin\WeChatAuto.py\Class Messages send_files_to_friend | **移除clear参数** |
| \src\pyweixin\WeChatAuto.py\Class Messages send_files_to_friends | **移除clear参数** |
| \src\pyweixin\WeChatAuto.py\Class Messages send_audios_to_friend | **支持多版本不同UI发送语音** |
| \src\pyweixin\WeChatAuto.py\Class Messages message_chain | **适配不同版本下的群内消息接龙** |
| \src\pyweixin\WeChatAuto.py\Class Messages pull_messages | **考虑消息少,数量多,遍历到顶的情况** |
| \src\pyweixin\utils.py\traverse_messages | **考虑消息少,数量多,遍历到顶的情况** |

## Add

| 位置 | 修改内容 |
| :-- | :-- |
| \src\pyweixin\Config.py\Class globalConfig\ _adjust_window_size | 自动调整**GlobalConfig.window_size**微信窗口大小 |
| \src\pyweixin\utils.py\get_focused_item\ | 获取全局键盘焦点元素的方式 |
| \src\pyweixin\utils.py\traver_chatList\ | 新的遍历消息列表方式 |
| \src\pyweixin\utils.py\traver_chatHistoryList\ | 新的遍历聊天记录列表方式 |
| \src\pyweixin\utils.py\parse_message\ | 新的解析聊天列表内的消息方式 |
| \src\pyweixin\utils.py\parse_message\ | 新的解析聊天记录列表内的消息方式 |

## ToDo

- 维护内部方法,保证稳定性...

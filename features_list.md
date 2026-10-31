# feature_list

## Changed

| 位置 | 修改内容 |
| :--- | :--- |
| \src\pyweixin\WeChatAuto.py\Class Contacts check_my_info | **增加保存头像选项** |
| \src\pyweixin\WeChatAuto.py\Class Contacts get_friend_profile | **增加保存头像选项** |
| \src\pyweixin\WeChatAuto.py\Class Collections collect_offAcc_articles | **修改公众号链接获取方式** |
| \src\pyweixin\WeChatAuto.py\Class Messages send_messages_to_friend | **移除clear参数** |
| \src\pyweixin\WeChatAuto.py\Class Messages send_messages_to_friends | **移除clear参数** |
| \src\pyweixin\WeChatAuto.py\Class Messages send_files_to_friend | **移除clear参数** |
| \src\pyweixin\WeChatAuto.py\Class Messages send_files_to_friends | **移除clear参数** |
| \src\pyweixin\WeChatAuto.py\Class Messages message_chain | **适配不同版本下的群内消息接龙** |
| \src\pyweixin\WeChatAuto.py\Class Messages pull_messages | **考虑消息少,数量多,遍历到顶的情况** |
| \src\pyweixin\utils.py\traverse_messages | **考虑消息少,数量多,遍历到顶的情况** |

## ToDo

- 维护内部方法,保证稳定性...

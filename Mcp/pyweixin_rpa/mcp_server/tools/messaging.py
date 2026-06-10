from fastmcp import FastMCP
from pyweixin.WeChatAuto import Messages # 假设这是你的包名

# 假设你有一个配置读取，或者直接用 GlobalConfig
# 这里为了演示，我们把默认值写在 MCP 层，或者让 MCP 读取全局配置

mcp=FastMCP("messaging")

@mcp.tool()
def wechat_send_messages(
    target: str, 
    messages: list[str], 
    at_members: list[str] = [], 
    at_all: bool = False,
    send_delay: float = 0.2
) -> dict:
    """
    向指定的微信好友或群聊发送一系列文本消息。
    
    !!! 注意: 单条消息超过2000字会自动转为TXT文件发送。
    
    Args:
        target: 好友或群聊的备注名/昵称。例如："张三"、"工作群"。
        messages: 待发送的消息列表。例如：["你好", "这是第二条消息"]。
        at_members: (仅群聊有效) 需要@的群成员昵称列表。例如：["李四", "王五"]。
        at_all: (仅群聊有效) 是否@所有人。
        send_delay: 每条消息发送后的延迟时间(秒)，防止被风控。默认 0.2 秒。
        
    Returns:
        发送结果摘要。
    """
    try:
        # 调用你的底层库，这里我们把其他参数固定为默认值或从全局读取
        # 注意：这里去掉了 friend (改为 target), messages 保持列表
        # 其他参数如 clear=True, is_maximize=False 等，根据你的 GlobalConfig 默认行为来
        
        Messages.send_messages_to_friend(
            friend=target,
            messages=messages,
            at_members=at_members,
            at_all=at_all,
            # 下面的参数我们不再暴露给 AI，由系统默认决定
            search_pages=None,  # 使用默认全局配置
            clear=None,         # 使用默认全局配置 (通常默认清理)
            send_delay=send_delay,
            is_maximize=None,   # 使用默认全局配置
            close_weixin=None   # 通常 MCP 模式下不主动关闭微信，除非你希望如此
        )
        
        return {
            "success": True,
            "summary": f"成功向 '{target}' 发送了 {len(messages)} 条消息"
        }
        
    except Exception as e:
        return {"success": False, "summary": f"发送失败: 发生错误 - {str(e)}"}


@mcp.tool()
def wechat_send_audios(
    target: str,
    audios: list[str],
    audio_length: int = 60,
    at_members: list[str] = [],
    at_all: bool = False
) -> dict:
    """
    向指定的微信好友或群聊发送语音消息。
    
    Args:
        target: 好友或群聊的备注名/昵称。
        audios: 语音文件路径列表。例如：[r"C:\voice1.wav", r"C:\voice2.mp3"]。
                注意：微信限制语音长度为 1~60 秒，会自动裁剪。
        audio_length: 每条语音的播放长度（秒）。默认 60 秒。
        at_members: (仅群聊有效) 需要@的群成员昵称列表。
        at_all: (仅群聊有效) 是否@所有人。
        
    Returns:
        发送结果摘要。
    """
    try:
        Messages.send_audios_to_friend(
            friend=target,
            audios=audios,
            audio_length=audio_length,
            at_members=at_members,
            at_all=at_all,
            # 同样，隐藏复杂的底层参数
            search_pages=None,
            clear=None,
            send_delay=None, # 语音可能有自己的内部延迟处理
            is_maximize=None,
            close_weixin=None
        )
        return {
            "success": True,
            "summary": f"成功向 '{target}' 发送了 {len(audios)} 条语音"
        }
    except Exception as e:
        return {"success": False, "summary": f"发送失败: {str(e)}"}


if __name__ == "__main__":
    mcp.run()
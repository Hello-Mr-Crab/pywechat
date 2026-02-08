class LongTextWarning(Warning):
    '''消息字数超长警告'''
    #微信字数限制2000字，超长部分不发送，这时需要转化为txt发送
    pass
class ChatHistoryNotEnough(Warning):
    '''聊天记录不足指定的个数'''
    pass
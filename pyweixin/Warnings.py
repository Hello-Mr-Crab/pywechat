'''
微信UI自动化过程中可能引发的Warning
'''
class LongTextWarning(Warning):
    '''微信消息字数超长警告'''
    #微信字数限制2000字，超长部分不发送，这时需要转化为txt发送
    pass
class NoChatHistoryWarning(Warning):
    '''聊天记录不足指定的个数'''
    pass
class LanguageDetectionFailedWarning(Warning):
    '''微信当前使用的语言探测失败'''
    pass
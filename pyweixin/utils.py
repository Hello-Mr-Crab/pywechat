import re
import os
import time
import emoji
import pyautogui
import soundfile as sf
import sounddevice as sd
from packaging import version
from pywinauto import WindowSpecification,Desktop,mouse
from .Config import GlobalConfig
from .WeChatTools import Navigator,Tools
from .WinSettings import SystemSettings
from .Uielements import Main_window,SideBar,Buttons,Edits,Lists,Windows,Texts,MenuItems
#######################################################################################
pyautogui.FAILSAFE=False#防止鼠标在屏幕边缘处造成的误触
desktop=Desktop(backend='uia')#windows桌面WindowSpecification示例
language=GlobalConfig.language#微信语言
Version=GlobalConfig.Version#微信版本
class Regex_Pattern():
    '''微信内常用正则pattern,适配多语言'''
    def __init__(self,language=language):
        self.language=language
        self.QtWindow_pattern=re.compile(r'Qt\d+QWindowIcon')#qt窗口通用classname
        self.Filename_pattern=re.compile(r'.*\.\w+\s')#用来匹配.docx,.ppt等文件名，只适合在微信聊天文件界面中使用
        self.GroupMember_Num_pattern=re.compile(r'\((\d+)\)$')#通讯录设置界面中每个最近群聊ListItem后边的数字
        self.Article_Timestamp_pattern=re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|昨天|星期\w|今天)')#公众号文章的时间戳
        self.UserLib_Pattern=re.compile(r'--user-lib-dir=(.*?)')#匹配微信命令行参数内的userlib文件夹路径
        if self.language=='简体中文':
            #|表示或的逻辑关系,关于Python正则表达式的任何问题和入门级教程可以看这篇博客:https://blog.csdn.net/weixin_73953650/article/details/151123336?spm=1001.2014.3001.5501
            self.Audio_pattern=re.compile(r'(?<=语音)\d+"秒(.*)$')#语音转文字后的文本内容
            self.Sns_Timestamp_pattern=re.compile(r'\s(\d+分钟前|\d+小时前|昨天|\d+天前)\s')#朋友圈好友发布内容左下角的时间戳,注意使用findall()[-1]获取不要直接search因为朋友群文本内容内可能也有类似的,但无论如何真正的时间戳永远是最后被匹配到,所以[-1]
            self.Contain_Images_pattern=re.compile(r'\s包含(\d+)张图片\s')#朋友圈包含\d+张图片
            self.Chafile_Timestamp_pattern=re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|昨天|星期\w|\d{1,2}:\d{2})')#微信聊天文件时间戳
            self.Snsdetail_Timestamp_pattern=re.compile(r'\s(\d{4}年\d{1,2}月\d{1,2}日\s\d{1,2}:\d{2}|\d{1,2}月\d{1,2}日\s\d{1,2}:\d{2}|昨天\s\d{1,2}:\d{2}|星期\w\s\d{1,2}:\d{2}|\d{1,2}:\d{2})\s')#微信好友朋友圈主页内的时间戳,注意使用findall()[-1]获取不要直接search因为朋友群文本内容内可能也有类似的,但无论如何真正的时间戳永远是最后被匹配到,所以[-1]
            self.Chathistory_Timestamp_pattern=re.compile(r'(?<=\s)(\d{4}年\d{1,2}月\d{1,2}日\s\d{2}:\d{2}|\d{1,2}月\d{1,2}日\s\d{2}:\d{2}|\d{2}:\d{2}|昨天\s\d{2}:\d{2}|星期\w\s\d{2}:\d{2})$')#聊天记录界面内的时间戳
            self.Session_Timestamp_pattern=re.compile(r'(?<=\s)(\d{4}/\d{1,2}/\d{1,2}|\d{1,2}/\d{1,2}|\d{2}:\d{2}|昨天 \d{2}:\d{2}|星期\w)$')#主界面左侧会话列表内的时间戳
            self.File_pattern=re.compile(r'文件\n(.*)\n')#微信聊天窗口发送的聊天文件卡片上的内容(有两个换行符)
            self.Message_Timestamp_pattern=re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日\s星期\w\s\d{2}:\d{2}|\d{1,2}月\d{1,2}日\s星期\w\s\d{2}:\d{2}|\d{1,2}月\d{1,2}日\s\d{2}:\d{2}|昨天\s\d{2}:\d{2}|星期\w\s\d{2}:\d{2}|\d{2}:\d{2})')#聊天界面内的时间戳
            self.newMessage_pattern=re.compile(r'\n\[(\d+)条\]')#微信主页左侧会话列表内带有新消息提示的好友
        if self.language=='English':
            self.Audio_pattern=re.compile(r'(?<=Audio)\d+"sec(.*)$')#语音转文字后的文本内容
            self.Sns_Timestamp_pattern=re.compile(r'\s(\d+\sminute\(s\)\sago|\d+\shour\(s\)\sago|Yesterday|\d+\sday\(s\)\sago)\s')#朋友圈好友发布内容左下角的时间戳
            self.Contain_Images_pattern=re.compile(r'\sContain\s(\d+)\simage\(s\)\s')#朋友圈包含\d+张图片
            self.Chafile_Timestamp_pattern=re.compile(r'(\d{4}-\d{1,2}-\d{1,2}|Yesterday|\w+day|\d{1,2}:\d{2})')#微信聊天文件界面内文件右下角的时间戳
            self.Snsdetail_Timestamp_pattern=re.compile(r'\s(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{2}|Yesterday\s\d{1,2}:\d{2}|\d{1,2}:\d{2})\s')#微信好友朋友圈主页内的时间戳
            self.Chathistory_Timestamp_pattern=re.compile(r'(?<=\s)(\d{4}-\d{1,2}-\d{1,2}\s\d{2}:\d{2})$')#聊天记录界面内的时间戳
            self.Session_Timestamp_pattern=re.compile(r'(?<=\s)(\d{4}/\d{1,2}/\d{1,2}|\d{1,2}/\d{1,2}|\d{2}:\d{2}|Yesterday \d{2}:\d{2}|\w+day)$')#主界面左侧会话列表内的时间戳
            self.File_pattern=re.compile(r'File\n(.*)\n')#微信聊天窗口发送的聊天文件卡片上的内容(有两个换行符)
            self.Message_Timestamp_pattern=re.compile(r'(\d{4}-\d{1,2}-\d{1,2}\s\d{2}:\d{2}|\d{1,2}/\d{1,2}\s\d{2}:\d{2}|Yesterday\s\d{2}:\d{2}|\w+day\s\d{2}:\d{2}|\d{2}:\d{2})')#聊天界面内的时间戳
            self.newMessage_pattern=re.compile(r'\n\[(\d+)\]')#微信主页左侧会话列表内带有新消息提示的好友
        if self.language=='繁體中文':
            self.Audio_pattern=re.compile(r'(?<=語音)\d+"秒(.*)$')#语音转文字后的文本内容
            self.Sns_Timestamp_pattern=re.compile(r'\s(\d+分鐘前|\d+小時前|昨天|\d+天前)\s')#朋友圈好友发布内容左下角的时间戳,注意使用findall()[-1]获取不要直接search因为朋友群文本内容内可能也有类似的,但无论如何真正的时间戳永远是最后被匹配到,所以[-1]
            self.Contain_Images_pattern=re.compile(r'\s包含\s(\d+)\s張圖片\s')#朋友圈包含\d+张图片
            self.Chafile_Timestamp_pattern=re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|昨天|星期\w|\d{1,2}:\d{2})')#微信聊天文件时间戳
            self.Snsdetail_Timestamp_pattern=re.compile(r'\s\d{4}年\d{1,2}月\d{1,2}日\s\d{1,2}:\d{2}|\d{1,2}月\d{1,2}日\s\d{1,2}:\d{2}|昨天\s\d{1,2}:\d{2}|星期\w\s\d{1,2}:\d{2}|\d{1,2}:\d{2}\s')#微信好友朋友圈主页内的时间戳,注意使用findall()[-1]获取不要直接search因为朋友群文本内容内可能也有类似的,但无论如何真正的时间戳永远是最后被匹配到,所以[-1]
            self.Chathistory_Timestamp_pattern=re.compile(r'(?<=\s)(\d{4}年\d{1,2}月\d{1,2}日\s\d{2}:\d{2}|\d{1,2}月\d{1,2}日\s\d{2}:\d{2}|\d{2}:\d{2}|昨天\s\d{2}:\d{2}|星期\w\s\d{2}:\d{2})$')#聊天记录界面内的时间戳
            self.Session_Timestamp_pattern=re.compile(r'(?<=\s)(\d{4}/\d{1,2}/\d{1,2}|\d{1,2}/\d{1,2}|\d{2}:\d{2}|昨天 \d{2}:\d{2}|星期\w)$')#主界面左侧会话列表内的时间戳
            self.File_pattern=re.compile(r'檔案\n(.*)\n')#微信聊天窗口发送的聊天文件卡片上的内容(有两个换行符)
            self.Message_Timestamp_pattern=re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日\s星期\w\s\d{2}:\d{2}|\d{1,2}月\d{1,2}日\s星期\w\s\d{2}:\d{2}|\d{1,2}月\d{1,2}日\s\d{2}:\d{2}|昨天\s\d{2}:\d{2}|星期\w\s\d{2}:\d{2}|\d{2}:\d{2})')#聊天界面内的时间戳
            self.newMessage_pattern=re.compile(r'\n\[(\d+)条\]')#微信主页左侧会话列表内带有新消息提示的好友            
class Special_Label():
    '''常用的一些微信内的标签,比如:“消息已置顶”，这些标签随着微信的语言会变化.'''
    def __init__(self,language=language):
        self.language=language
        self.EnterPrise='企业'
        self.RealName='实名'
        self.State='员工状态'
        self.Duty='职务'
        self.WorkingTime='工作时间'
        self.OnlineTime='在线时间'
        self.Location='地址'
        self.From='来自'
        self.WeCom='企业微信'
        if self.language=='简体中文':
            self.EnterPriseInfomation='企业信息'
            self.Block='加入黑名单'
            self.UnBlock='移出黑名单'
            self.StuckonTop='已置顶\n'
            self.Star='设为星标朋友'
            self.UnStar='不再设为星标朋友'
            self.MuteNotifications='消息免打扰\n'
            self.LightMode='浅色模式'
            self.DarkMode='深色模式'
            self.Automatic='跟随系统'
            self.Image='图片'
            self.File='文件\n'
            self.Link='[链接]'
            self.Video='视频'
            self.WxNum='微信号：'
            self.Nickname='昵称：' 
            self.Region='地区：'
            self.Remark='备注'
            self.SharedGroups='共同群聊' 
            self.Signature='个性签名' 
            self.Source='来源'
            self.Mobile='电话'
            self.Description='描述'
            self.Tags='标签'
            self.Privacy='朋友权限'
            self.ViewAll='查看全部'
            self.YearSep='年'
            self.MonthSep='月'
            self.DaysAgo='天前'
            self.NotDownloaded='未下载'
            self.Expired='已过期'
            self.SendInterrupt='发送中断'
            self.Yesterday='昨天'
            self.Moments='朋友圈'
            self.Messages='发消息'
            self.VoiceCall='语音聊天'
            self.VideoCall='视频聊天'
            self.Download='下载'
            self.RedPacket='微信红包'
            self.Transfer='微信转账'
            self.MiniProgram='小程序'
            self.Music='音乐'
            self.Channels='视频号'
            self.ChatHistory='聊天记录'
            self.NotCare={'session_item_服务号','session_item_公众号'}
            self.Minutes={f'{i}分钟前' for i in range(1,60)}
            self.Hours={f'{i}小时前' for i in range(1,24)}
            self.WeekDays={f'{i}天前' for i in range(1,8)}
            self.MonthDays={f'{i}天前' for i in range(1,31)}
            self.Hours.update(self.Minutes)
            self.WeekDays.update(self.Hours)
            self.WeekDays.add(self.Yesterday)
            self.MonthDays.update(self.WeekDays)
        if self.language=='English':
            self.Block='Block'
            self.UnBlock='UnBlock'
            self.EnterPriseInfomation='Enterprise Information'
            self.StuckonTop='Stuck on Top\n'
            self.Star='Star'
            self.UnStar='UnStar'
            self.MuteNotifications='Mute Notifications\n'
            self.LightMode='LightMode'
            self.DarkMode='DarkMode'
            self.Automatic='Automatic'
            self.Image='Image'
            self.File='File\n'
            self.Link='[Link]'
            self.Video='Video'
            self.WxNum='Weixin ID:'
            self.Nickname='Name:' 
            self.Region='Region:'
            self.Remark='Remark'
            self.SharedGroups='Shared Groups' 
            self.Signature="What's Up" 
            self.Source='Source'
            self.Mobile='Mobile'
            self.Description='Description'
            self.Tags='Tags'
            self.Privacy='Privacy'
            self.ViewAll='View All'
            self.YearSep='-'
            self.MonthSep='-'
            self.DaysAgo='day(s) ago'
            self.NotDownloaded='Not Downloaded'
            self.Expired='Expired'
            self.SendInterrupt='Send Interrupt'
            self.Yesterday='Yesterday'
            self.Moments='Moments'
            self.Messages='Messages'
            self.VoiceCall='Voice Call'
            self.VideoCall='Video Call'
            self.Download='Download'
            self.RedPacket='Weixin Red Packet'
            self.MiniProgram='Mini Programs'
            self.Music='Music'
            self.Channels='Channels'
            self.Transfer='WeChat Transfer'
            self.ChatHistory='Chat History'
            self.NotCare={'session_item_Service Accounts','session_item_Official Accounts'}
            self.Minutes={f'{i} minute(s) ago' for i in range(1,60)}
            self.Hours={f'{i} hour(s) ago' for i in range(1,24)}
            self.WeekDays={f'{i} day(s) ago' for i in range(1,8)}
            self.MonthDays={f'{i} day(s) ago' for i in range(1,31)}
            self.Hours.update(self.Minutes)
            self.WeekDays.update(self.Hours)
            self.WeekDays.add(self.Yesterday)
            self.MonthDays.update(self.WeekDays)
        if self.language=='繁體中文':
            self.Block='加入黑名單'
            self.UnBlock='移出黑名單'
            self.Star='設為超級好友'
            self.UnStar='不再設為超級好友'
            self.StuckonTop='已置頂\n'
            self.MuteNotifications='訊息免打擾\n'
            self.LightMode='淺色模式'
            self.DarkMode='深色模式'
            self.Automatic='跟隨系统'
            self.Image='圖片'
            self.File='檔案\n'
            self.Link='[連結]'
            self.Video='影片'
            self.WxNum='微信 ID:'
            self.Nickname='暱稱:' 
            self.Region='地區:'
            self.Remark='備註'
            self.SharedGroups='共同群組' 
            self.Signature='個性簽名' 
            self.Source='來源'
            self.Mobile='電話'
            self.Description='描述'
            self.Tags='標籤'
            self.Privacy='朋友權限'
            self.ViewAll='查看全部'
            self.YearSep='年'
            self.MonthSep='月'
            self.DaysAgo='天前'
            self.NotDownloaded='未下載'
            self.Expired='已逾期'
            self.SendInterrupt='发送中断'
            self.Yesterday='昨天'
            self.Moments='朋友圈'
            self.Download='下載'
            self.RedPacket='微信紅包'
            self.MiniProgram='小程式'
            self.Music='音樂'
            self.Channels='影音號'
            self.Transfer='WeChat 轉賬'
            self.ChatHistory='聊天記錄'
            self.VoiceCall='語音通話'
            self.VideoCall='視訊通話'
            self.NotCare={'session_item_服務賬號','session_item_官方賬號'}
            self.Minutes={f'{i}分鐘前' for i in range(1,60)}
            self.Hours={f'{i}小時前' for i in range(1,24)}
            self.WeekDays={f'{i}天前' for i in range(1,8)}
            self.MonthDays={f'{i}天前' for i in range(1,31)}
            self.Hours.update(self.Minutes)
            self.WeekDays.update(self.Hours)
            self.WeekDays.add(self.Yesterday)
            self.MonthDays.update(self.WeekDays)

class ColorMatch():
    '''朋友圈点赞评论时需要用颜色识别点击按钮'''
    @staticmethod
    def _is_green_pixel(r:int,g:int,b:int)->bool:
        '''微信发送按钮绿色像素启发式判断'''
        if g < 80:
            return False
        if (g-r) < 18 or (g-b) < 8:
            return False
        if g < int(r*1.18):
            return False
        if g < int(b*1.10):
            return False
        return True

    @staticmethod
    def _find_green_button_center(region:tuple[int,int,int,int]):
        '''在给定区域内寻找绿色按钮中心点,找不到返回None'''
        try:
            screenshot=pyautogui.screenshot(region=region).convert('RGB')
        except Exception:
            return None
        width,height=screenshot.size
        if width<=0 or height<=0:
            return None
        pixels=screenshot.load()
        min_x,min_y=width,height
        max_x,max_y=-1,-1
        hit_count=0
        for y in range(0,height,2):
            for x in range(0,width,2):
                r,g,b=pixels[x,y]
                if ColorMatch._is_green_pixel(r,g,b):
                    hit_count+=1
                    if x<min_x:
                        min_x=x
                    if y<min_y:
                        min_y=y
                    if x>max_x:
                        max_x=x
                    if y>max_y:
                        max_y=y

        if hit_count<16 or max_x<0 or max_y<0:
            return None
        if (max_x-min_x)<10 or (max_y-min_y)<6:
            return None
        center_x=region[0]+(min_x+max_x)//2
        center_y=region[1]+(min_y+max_y)//2+2
        return center_x,center_y

    @staticmethod
    def _find_gray_button_center(region: tuple[int, int, int, int]):
        '''在指定区域内快速查找灰色省略号按钮的中心点'''
        try:
            screenshot=pyautogui.screenshot(region=region).convert('RGB')
        except Exception:
            return None
        width,height=screenshot.size
        pixels=screenshot.load()
        #直接寻找最亮的浅灰色像素块
        target_pixels=[]
        for y in range(height):
            for x in range(width):
                r, g, b=pixels[x, y]
                # 条件放宽：接近白色但不是纯白
                if r >220 and g>220 and b>220:#很亮的灰色
                    if abs(r-g)<15 and abs(g-b)<15: #RGB值接近
                        target_pixels.append((x,y))
        if len(target_pixels)<5: #像素太少说明没找到
            return None
        #计算中心点
        xs=[p[0] for p in target_pixels]
        ys=[p[1] for p in target_pixels]
        center_x=region[0]+(min(xs)+max(xs))//2
        center_y=region[1]+(min(ys)+max(ys))//2
        return center_x, center_y

    @staticmethod
    def click_green_send_button(rectangle,x_offset:int=70,y_offset:int=42)->bool:
        '''
        通过像素颜色识别点击评论区的绿色发送按钮,识别失败时回退原坐标点击
        Args:
            rectangle:评论区列表项目所属的矩形
            x_offset:相较于该列表项目右侧靠左的距离
            y_offset:相较于该列表项目底部靠上的距离
        '''
        fallback_coords=(rectangle.right-x_offset,rectangle.bottom-y_offset)
        regions=[
            (max(fallback_coords[0]-80,0),max(fallback_coords[1]-45,0),170,90),
            (max(rectangle.right-(x_offset+150),0),max(rectangle.bottom-(y_offset+90),0),280,170),
        ]
        for region in regions:
            center=ColorMatch._find_green_button_center(region)
            if center is not None:
                mouse.click(coords=center)
                return True
        mouse.click(coords=fallback_coords)
        return False

    @staticmethod
    def click_gray_ellipsis_button(rectangle,x_offset:int=70,y_offset:int=33) -> bool:
        '''
        通过像素颜色识别点击灰色省略号按钮
        Args:
            rectangle:评论区列表项目所属的矩形
            x_offset:相较于该列表项目右侧靠左的距离
            y_offset:相较于该列表项目底部靠上的距离
        '''
        #45x33的搜索区域
        region_width=45
        region_height=33
        region_x=rectangle.right-x_offset
        region_y=rectangle.bottom-y_offset
        region=(region_x,region_y,region_width,region_height)
        center=ColorMatch._find_gray_button_center(region)
        if center is not None:
            mouse.click(coords=center)
            return True
        else:
            #直接点击固定坐标
            fallback_x=rectangle.right-44
            fallback_y=rectangle.bottom-15
            mouse.click(coords=(fallback_x, fallback_y))
            return False

class TimeStamp():
    '关于微信内的一些时间戳'
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version

    def get_current_week_dates(self)->list[str]:
        '''按照获取当前周的所有日期
        Returns:
            week_dates:['2026-04-xx',...,'2026-04-xx+7']
        '''
        now=time.localtime()
        current_weekday=now.tm_wday
        current_timestamp=time.mktime(now)
        monday_timestamp=current_timestamp-current_weekday*24*3600
        week_dates=[]
        for i in range(7):
            day_timestamp=monday_timestamp+i*24*3600
            if self.language=='English':
                date_str=time.strftime("%Y-%m-%d",time.localtime(day_timestamp))
                date_str=re.sub('-0','-',date_str)
            else:
                date_str=time.strftime("%Y年%m月%d日",time.localtime(day_timestamp))
                date_str=re.sub('年0','年',date_str)
            week_dates.append(date_str)
        return week_dates
    
    def get_yesterday_label(self)->str:
        '''获取昨天日期'''
        now=time.time()
        if self.language=='English':
            yesterday=time.strftime("%Y-%m-%d",time.localtime(now-86400))
            yesterday=re.sub(r'-0','-',yesterday)
        else:
            yesterday=time.strftime("%Y年%m月%d日",time.localtime(now-86400))
            yesterday=re.sub(r'年0','年',yesterday) 
        return yesterday
    
    def get_today_label(self)->str:
        '''获取今天日期'''
        if self.language=='English':
            today_label=time.strftime("%Y-%m-%d")
            today_label=re.sub(r'-0','-',today_label)
        else:
            today_label=time.strftime("%Y年%m月%d日")
            today_label=re.sub(r'年0','年',today_label)
        return today_label

    def get_month_label(self)->str:
        '''获取本月日期'''
        if self.language=='English':
            month_label=time.strftime("%Y-%m")
            month_label=re.sub(r'-0','-',month_label)
        else:
            month_label=time.strftime("%Y年%m月")
            month_label=re.sub(r'年0','年',month_label)
        return month_label

class Messages():
    '''发送消息的一些操作,传入的参数是main_window(微信),且不涉及关闭微信窗口,便于个人二次开发'''
    @staticmethod
    def send_messages_to_friend(main_window:WindowSpecification,messages:list[str],send_delay:float=None):
        '''
        该函数用于给当前微信界面内所在的好友发送信息
        Args:
            main_window:已切换到某个好友聊天框后的微信主界面或者是单独的聊天窗口
            messages:所有待发送消息列表。格式:message=["消息1","消息2"]
            send_delay:发送单条消息延迟,单位:秒/s,默认0.2s(0.1-0.2之间是极限)。
        '''
        if send_delay is None:send_delay=GlobalConfig.send_delay
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        if not edit_area.exists(timeout=0.1):
            print('非正常好友,无法发送消息!')
            return 
        for message in messages:
            if 0<len(message)<2000:
                edit_area.click_input()
                edit_area.set_text(message)
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
            elif len(message)>2000:#字数超过200字发送txt文件
                SystemSettings.convert_long_text_to_txt(message)
                pyautogui.hotkey('ctrl','v',_pause=False)
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
    @staticmethod
    def send_files_to_friend(main_window:WindowSpecification,files:list[str],send_delay:float=None)->None:
        '''
        该函数用于给当前聊天界面内的好友或群聊发送多个文件
        Args:
            main_window:已切换到某个聊天后的微信主界面或者是单独的聊天窗口
            files:所有待发送文件所路径列表。
            send_delay:发送单条信息或文件的延迟,单位:秒/s,默认0.2s。
        '''
        #发送文件逻辑
        def send_files(files):
            if len(files)<=9:
                SystemSettings.copy_files_to_clipboard(filepaths_list=files)
                pyautogui.hotkey("ctrl","v")
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
            else:
                files_num=len(files)
                rem=len(files)%9
                for i in range(0,files_num,9):
                    if i+9<files_num:
                        SystemSettings.copy_files_to_clipboard(filepaths_list=files[i:i+9])
                        pyautogui.hotkey('ctrl','v')
                        time.sleep(send_delay)
                        pyautogui.hotkey('alt','s',_pause=False)
                if rem:
                    SystemSettings.copy_files_to_clipboard(filepaths_list=files[files_num-rem:files_num])
                    pyautogui.hotkey('ctrl','v')
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
        
        if send_delay is None:send_delay=GlobalConfig.send_delay
        #对发送文件校验
        if files:            
            files=[file for file in files if os.path.isfile(file)]
            files=[file for file in files if 0<os.path.getsize(file)<1073741824]#0到1g之间的文件才可以发送
        if not files:return
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        if not edit_area.exists(timeout=0.1):
            print(f'非正常好友,无法发送文件!')
            return 
        send_files(files)

    @staticmethod
    def send_audios_to_friend(main_window:WindowSpecification,audios:list[str],audio_length:int=60,send_delay:int=None):
        '''
        该方法用于给当前聊天界面内的好友或群聊发送语音
        Args:
            friend:好友或群聊备注。格式:friend="好友或群聊备注"
            audios:所有待发送消息列表。格式:audios=["xxx.wav","yyy.mp3"...]
            audio_length:语音长度,按照微信语音
            send_delay:发送单条信息的延迟,单位:秒/s,默认0.2s。
        '''
        if send_delay is None:send_delay=GlobalConfig.send_delay
        current_version=GlobalConfig.Version
        if version.parse(current_version)>=version.parse('4.1.9'):
            audios=process_audios(audios=audios,audio_length=audio_length)
            if audios:
                sd.default.device=SystemSettings.get_default_output()
                edit_area=main_window.child_window(**Edits.CurrentChatEdit)
                if not edit_area.exists(timeout=0.1):
                    return 
                send_audio_button=main_window.child_window(**Buttons.SendAudioButon)
                window_center=main_window.rectangle().mid_point()
                button_center=send_audio_button.rectangle().mid_point()
                for samplerate,audio in audios:
                    send_audio_button.click_input() 
                    mouse.move(coords=(window_center.x,window_center.y))
                    sd.play(audio,samplerate)
                    sd.wait()
                    mouse.click(coords=(button_center.x,button_center.y))
                    time.sleep(send_delay)
        else:
            print(f'当前微信版本不支持发送语音!')
    
    @staticmethod
    def message_chain(main_window:WindowSpecification,content:str=None,theme:str=None,example:str=None,description:str=None):
        '''
        该函数用来在当前微信界面所在的群聊发起接龙
        Args:
            main_window:已切换到某个群聊后的微信主界面或者是单独的聊天窗口
            content:发起接龙时自己所填的内容
            theme:接龙的主题
            example:接龙的例子
            description:接龙详细描述
        '''
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        if not edit_area.exists(timeout=0.1):
            print(f'非正常好友,无法发送消息')
            return
        if Tools.is_group_chat(main_window):
            edit_area.set_text('#接龙')
            pyautogui.press('down')
            pyautogui.press('enter')
            solitaire_window=main_window.child_window(**Windows.SolitaireWindow)
            solitaire_button=solitaire_window.child_window(**Buttons.SolitaireButton)
            solitaire_list=solitaire_window.child_window(**Lists.SolitaireList)
            if content is not None:
                SystemSettings.copy_text_to_clipboard(content)
                solitaire_list.click_input()#自己填写的内容正好在接龙列表的中间,所以直接click_input()
                pyautogui.hotkey('ctrl','a')#全选删除然后复制content
                pyautogui.press('backspace')
                pyautogui.hotkey('ctrl','v')
            if isinstance(theme,str):
                solitaire_window.child_window(control_type='Edit',found_index=0).set_text(theme)
            if isinstance(example,str):
                solitaire_window.child_window(control_type='Edit',found_index=1).set_text(example)
            if isinstance(description,str):
                text=solitaire_window.child_window(**Texts.AddContentText)
                rec=text.rectangle()
                position=rec.left+2,rec.mid_point().y
                mouse.click(coords=position)
                solitaire_window.child_window(control_type='Edit',found_index=2).set_text(description)
            solitaire_button.click_input()



def At(main_window:WindowSpecification,at_members:list[str]):
    '''
    在群里@指定的好友,可用于自定义的消息发送函数中
    Args:
        main_window:微信主界面
        at_members:群内所有at对象,必须是群昵称
    '''
    def select(mention_popover:WindowSpecification,member:str):
        '''
        微信的@机制必须type_keys打字才可以唤醒,并且是模糊文字匹配(只匹配文字,空格表情都不匹配)
        若好友的名字中有空格和表情,那么打字的内容只能是第一个空格之前的所有非空格文字,但凡多一个空格
        就不会唤醒@,同时由于表情不好打字,所以替换掉,出现mention面板然后在弹出的列表里完整匹配
        '''
        is_find=True
        mention_list=mention_popover.child_window(control_type='List',title='')
        first_item=mention_list.children()[0].window_text()#弹出列表后的第一个人
        selected_listitem=[listitem for listitem in mention_list.children() if listitem.is_selected()][0]
        while selected_listitem.window_text()!=member:#一直按着下键找，找到了结束循环，或者遍历完一圈又回到了起点也结束循环(即选中的对象与第一个人名字相同)
            mention_list.type_keys('{DOWN}')
            selected_listitem=[listitem for listitem in mention_list.children() if listitem.is_selected()][0]
            if selected_listitem.window_text()==first_item:
                is_find=False
                break
        return is_find
        
    if Tools.is_group_chat(main_window):
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        mention_popover=main_window.child_window(**Windows.MentionPopOverWindow)
        for member in at_members:
            cleaned_member=emoji.replace_emoji(member,'')#去掉emoji
            cleaned_member=cleaned_member.split(' ')[0]#找到第一个空格字段之前内容
            edit_area.type_keys(f'@{cleaned_member}',pause=0.1)
            if mention_popover.exists(timeout=0.1):
                is_find=select(mention_popover,member)
                if is_find:
                    edit_area.type_keys('{ENTER}')
                if not is_find:
                    pyautogui.press('backspace',presses=len(cleaned_member)+1)
            else:
                edit_area.set_text('')

def At_all(main_window:WindowSpecification):
    '''在群里@所有人'''
    if Tools.is_group_chat(main_window):
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        mention_popover=main_window.child_window(**Windows.MentionPopOverWindow)
        edit_area.type_keys(f'@',pause=0.1)
        if mention_popover.exists(timeout=0.1):
            mention_list=mention_popover.child_window(control_type='List',title='')
            first_item=mention_list.children()[0].window_text()#弹出列表后的第一个人
            if first_item!='所有人':
                pyautogui.press('backspace',presses=1)
                print(f'你不是该群群主或管理员,无权@所有人')
            else:
                edit_area.type_keys('{ENTER}')

def get_new_message_num(main_window:WindowSpecification=None,is_maximize:bool=None,close_weixin:bool=None):
    '''
    该函数用来获取侧边栏左侧微信按钮上的红色新消息总数
    Args:
        main_window:微信主界面,可以不传入,不传入时自动打开微信
        is_maximize:微信界面是否全屏，默认不全屏
        close_weixin:任务结束后是否关闭微信，默认关闭
    Returns:
        new_message_num:新消息总数
    '''
    if is_maximize is None:
        is_maximize=GlobalConfig.is_maximize
    if close_weixin is None:
        close_weixin=GlobalConfig.close_weixin
    if main_window is None:
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
    weixin_button=main_window.child_window(auto_id="MainView.main_tabbar", control_type="ToolBar").children()[0]
    #左上角微信按钮的红色消息提示(\d+条新消息)在FullDescription属性中,
    #只能通过id来获取,id是30159，之前是30007,可能是qt组件映射关系不一样
    full_desc=weixin_button.element_info.element.GetCurrentPropertyValue(30159)
    new_message_num=re.search(r'\d+',full_desc)#正则提取数量
    if close_weixin:main_window.close()
    return int(new_message_num.group(0)) if new_message_num  else 0


def NativeChooseFolder(folder:str):
    '''
    该函数用来在微信点击保存按钮后弹出的windows界面中保存文件
    '''
    SystemSettings.copy_text_to_clipboard(folder)
    choose_folder_window=desktop.window(**{'control_type':'Window','framework_id':'Win32','top_level_only':False,'found_index':0})
    choose_folder_button=choose_folder_window.child_window(control_type='Button',title='选择文件夹')
    prograss_bar=choose_folder_window.child_window(control_type='ProgressBar',class_name='msctls_progress32',framework_id='Win32')
    path_bar=prograss_bar.child_window(class_name='ToolbarWindow32',control_type='ToolBar',found_index=0)
    if re.search(r':\s*(.*)',path_bar.window_text()).group(1)!=folder:
        rec=path_bar.rectangle()
        mouse.click(coords=(rec.right-5,int(rec.top+rec.bottom)//2))
        pyautogui.press('backspace')
        pyautogui.hotkey('ctrl','v',_pause=False)
        pyautogui.press('enter')
        time.sleep(0.5)
    choose_folder_button.click_input()
    
def scan_for_new_messages(main_window:WindowSpecification=None,delay:float=0.3,is_maximize:bool=None,close_weixin:bool=None)->dict:
    '''
    该函数用来扫描检查一遍会话列表中的所有新消息,返回发送对象以及新消息数量(不包括免打扰)
    Args:
        main_window:微信主界面实例,可以用于二次开发中直接传入main_window,也可以不传入,不传入自动打开
        delay:在会话列表查询新消息时的翻页延迟时间,默认0.3秒
        is_maximize:微信界面是否全屏，默认不全屏
        close_weixin:任务结束后是否关闭微信，默认关闭
    Returns:
        newMessages_dict:有新消息的好友备注及其对应的新消息数量构成的字典
    '''
    def traverse_messsage_list(listItems):
        #newMessageTips为newMessagefriends中每个元素的文本:['测试365 5条新消息','一家人已置顶20条新消息']这样的字符串列表
        listItems=[listItem for listItem in listItems if listItem.automation_id() not in not_care 
        and mute_notifications not in listItem.window_text()]
        listItems=[listItem for listItem in listItems if new_message_pattern.search(listItem.window_text())]
        senders=[listItem.automation_id().replace('session_item_','') for listItem in listItems]
        newMessageTips=[listItem.window_text() for listItem in listItems if listItem.window_text() not in newMessageSenders]
        newMessageNum=[int(new_message_pattern.search(text).group(1)) for text in newMessageTips]
        return senders,newMessageNum

    not_care=Special_Labels.NotCare
    mute_notifications=Special_Labels.MuteNotifications
    if is_maximize is None:
        is_maximize=GlobalConfig.is_maximize
    if close_weixin is None:
        close_weixin=GlobalConfig.close_weixin
    if main_window is None:
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
    newMessageSenders=[]
    newMessageNums=[]
    newMessages_dict={}
    chats_button=main_window.child_window(**SideBar.Weixin)
    chats_button.click_input()
    #左上角微信按钮的红色消息提示(\d+条新消息)在FullDescription属性中,
    #只能通过id来获取,id是30159，之前是30007,可能是qt组件映射关系不一样
    full_desc=chats_button.element_info.element.GetCurrentPropertyValue(30159)
    session_list=main_window.child_window(**Main_window.SessionList)
    session_list.type_keys('{HOME}')
    new_message_num=re.search(r'\d+',full_desc)#正则提取数量
    #微信会话列表内ListItem标准格式:备注\s(已置顶)\s(\d+)条未读\s最后一条消息内容\s时间
    new_message_pattern=Regex_Patterns.newMessage_pattern#只给数量分组.group(1)获取
    if not new_message_num:return {}
    if new_message_num:
        new_message_num=int(new_message_num.group(0))
        session_list=main_window.child_window(**Main_window.SessionList)
        session_list.type_keys('{END}')
        time.sleep(1)
        last_item=session_list.children(control_type='ListItem')[-1].window_text()
        session_list.type_keys('{HOME}')
        time.sleep(1)
        while sum(newMessages_dict.values())<new_message_num:#当最终的新消息总数之和大于等于实际新消息总数时退出循环
            #遍历获取带有新消息的ListItem
            listItems=session_list.children(control_type='ListItem')
            time.sleep(delay)
            senders,nums=traverse_messsage_list(listItems)
            ##提取姓名和数量
            newMessageNums.extend(nums)
            newMessageSenders.extend(senders)
            newMessages_dict=dict(zip(newMessageSenders,newMessageNums))
            session_list.type_keys('{PGDN}')
            if listItems[-1].window_text()==last_item:
                break
        session_list.type_keys('{HOME}')
    if close_weixin:
        main_window.close()
    return newMessages_dict

def parse_chat_history(friend:str,myName:str,details_with_name:list[str])->tuple[list,list,list,list]:
    '''私聊聊天记录消息解析,不是对方发送就是个人发送
    Args:
        friend:好友名称
        myName:本人昵称(Contacts.check_my_info)
        details_with_name:开启多选遍历得到的文本(traverse_chat_histor_list)
    Returns:
        (contents,senders,timestamps,message_types):消息内容,消息发送人,时间戳,消息类型
    '''
    senders=[]
    contents=[]
    timestamps=[]
    message_types=[]
    timestamp_pattern=Regex_Patterns.Chathistory_Timestamp_pattern
    image_label=Special_Labels.Image
    video_label=Special_Labels.Video
    file_label=Special_Labels.File
    link_label=Special_Labels.Link
    miniprogram_label=Special_Labels.MiniProgram
    channels_label=Special_Labels.Channels
    redpacket_label=Special_Labels.RedPacket
    transfer_label=Special_Labels.Transfer
    videoCall_label=Special_Labels.VideoCall
    voiceCall_label=Special_Labels.VoiceCall
    chat_history_label=Special_Labels.ChatHistory
    for text,class_name in details_with_name:
        timestamp=timestamp_pattern.search(text).group(0) if timestamp_pattern.search(text) else '红包或转账(无法获取时间戳)'
        text=timestamp_pattern.sub('',text)
        if timestamp=='红包或转账(无法获取时间戳)':
            sender='红包或转账(无法获取发送人)'
            content=text.strip()
        else:
            sender=friend if re.search(rf'^{friend}\s',text) is not None else myName
            content=re.sub(rf'^{sender}\s','',text).strip()
        if class_name=='mmui::ChatTextItemView':
            message_type='文本'
        if class_name=='mmui::ChatPersonalCardItemView':
            message_type='好友名片'
        if class_name=='mmui::ChatBubbleReferItemView':
            if image_label in content:message_type='图片'
            if video_label in content:message_type='视频'
        if class_name=='mmui::ChatBubbleItemView':
            if content.startswith(file_label):message_type='文件'
            if content.startswith(link_label):message_type='链接'
            if content.startswith(miniprogram_label):message_type='小程序'
            if content.startswith(channels_label):message_type='视频号'
            if content.endswith(redpacket_label):message_type='微信红包'
            if content.endswith(transfer_label):message_type='微信转账'
            if content.startswith(chat_history_label):message_type='聊天记录'
            if content.startswith(voiceCall_label):message_type='语音通话'
            if content.startswith(videoCall_label):message_type='视频通话'
        senders.append(sender)
        contents.append(content)
        timestamps.append(timestamp)
        message_types.append(message_type)
    return  contents,senders,timestamps,message_types

def parse_group_chat_history(details_with_name:list[tuple[str,str]],details_without_name:list[tuple[str,str]],groupMembers:list[str])->tuple[list,list,list]:
    '''群聊内的聊天记录解析
    Args:
        texts_with_name:开启多选遍历得到的(文本,类名)元祖列表(traverse_chat_history_list)
        texts_without_name:不开启多选遍历得到的(文本,类名)文本(traverse_chat_history_list)
        groupMembers:群成员昵称列表(Contacts.get_groupMembers_info)
    Returns:
        (contents,senders,timestamps):消息内容,消息发送人,时间戳
    '''
    senders=[]
    contents=[]
    message_types=[]
    timestamps=[]
    image_label=Special_Labels.Image
    video_label=Special_Labels.Video
    file_label=Special_Labels.File
    link_label=Special_Labels.Link
    miniprogram_label=Special_Labels.MiniProgram
    channels_label=Special_Labels.Channels
    redpacket_label=Special_Labels.RedPacket
    transfer_label=Special_Labels.Transfer
    videoCall_label=Special_Labels.VideoCall
    voiceCall_label=Special_Labels.VoiceCall
    chat_history_label=Special_Labels.ChatHistory
    timestamp_pattern=Regex_Patterns.Chathistory_Timestamp_pattern
    if groupMembers:
        for text,class_name in details_with_name:
            timestamp=timestamp_pattern.search(text).group(0) if timestamp_pattern.search(text) else '红包或转账(无法获取时间戳)'
            if timestamp=='红包或转账(无法获取时间戳)':
                sender='红包或转账(无法获取发送人)'
                content=text.strip()
            else:
                for groupMember in groupMembers:
                    search_result=re.search(rf'^({re.escape(groupMember)})\s',text)
                    if search_result is not None:
                        sender=search_result.group(1)
                        content=timestamp_pattern.sub('',text).replace(sender,'').strip()
            if class_name=='mmui::ChatTextItemView':
                message_type='文本'
            if class_name=='mmui::ChatPersonalCardItemView':
                message_type='好友名片'
            if class_name=='mmui::ChatBubbleReferItemView':
                if image_label in content:message_type='图片'
                if video_label in content:message_type='视频'
            if class_name=='mmui::ChatBubbleItemView':
                if content.startswith(file_label):message_type='文件'
                if content.startswith(link_label):message_type='链接'
                if content.startswith(miniprogram_label):message_type='小程序'
                if content.startswith(channels_label):message_type='视频号'
                if content.endswith(redpacket_label):message_type='微信红包'
                if content.endswith(transfer_label):message_type='微信转账'
                if content.startswith(chat_history_label):message_type='聊天记录'
                if content.startswith(voiceCall_label):message_type='语音通话'
                if content.startswith(videoCall_label):message_type='视频通话'
            message_types.append(message_type)
            senders.append(sender)
            contents.append(content)
            timestamps.append(timestamp)
    else:
        for detail_with_name,detail_without_name in zip(details_with_name,details_without_name):
            text_with_name=detail_with_name[0]
            text_without_name=detail_without_name[0]
            class_name=detail_with_name[1]
            timestamp=timestamp_pattern.search(text_without_name).group(0) if timestamp_pattern.search(text_without_name) else '红包或转账(无法获取时间戳)'
            content=timestamp_pattern.sub('',text_without_name)
            if timestamp=='红包或转账(无法获取时间戳)':
                sender='红包或转账(无法获取发送人)'
            else:
                sender=text_with_name.replace(text_without_name,'').strip()
                sender=timestamp_pattern.sub('',sender).replace(content,'')
            if class_name=='mmui::ChatTextItemView':
                message_type='文本'
            if class_name=='mmui::ChatBubbleReferItemView':
                if video_label in content:message_type='链接'
                if image_label in content:message_type='链接'
            if class_name=='mmui::ChatBubbleItemView':
                if content.startswith(file_label):message_type='文件'
                if content.startswith(link_label):message_type='链接'
                if content.startswith(miniprogram_label):message_type='小程序'
                if content.startswith(channels_label):message_type='视频号'
                if content.endswith(redpacket_label):message_type='微信红包'
                if content.endswith(transfer_label):message_type='微信转账'
                if content.startswith(chat_history_label):message_type='聊天记录'
                if content.startswith(voiceCall_label):message_type='语音通话'
                if content.startswith(videoCall_label):message_type='视频通话'
            message_types.append(message_type)
            senders.append(sender)
            contents.append(content)
            timestamps.append(timestamp)
    return contents,senders,timestamps,message_types

def parse_messages(friend:str,myName:str,texts_with_name:list[str]):
    '''私聊解析聊天界面内的信息,不是自己发的就是对方发的
    Args:
        friend:好友名称
        myName:本人昵称(Contacts.check_my_info)
        texts_with_name:开启多选遍历得到的文本(traverse_chatList)
    Returns:
        (contents,senders,timestamps):消息内容,消息发送人,时间戳
    '''
    senders=[]
    contents=[]
    for text in texts_with_name:
        sender=friend if re.search(rf'^{re.escape(friend)}\s',text) is not None else myName
        content=re.sub(rf'^{sender}\s','',text)
        senders.append(sender)
        contents.append(content)
    return contents,senders

def parse_group_messages(texts_with_name:list[str],texts_without_name:list[str]):
    '''群聊提取信息
    Args:
        texts_with_name:开启多选遍历得到的文本(traverse_chatList)
        texts_without_name:不开启多选遍历得到的文本(traverse_chatList)
    Returns:
        (contents,senders):消息内容,消息发送人,时间戳
    '''
    senders=[]
    contents=[]
    for text_with_name,text_without_name in zip(texts_with_name,texts_without_name):
        sender=text_with_name.replace(text_without_name,'').strip()
        if sender=='':sender='红包或转账(无法获取发送人)'
        senders.append(sender)
        contents.append(text_without_name)
    return contents,senders

def traverse_chat_history_list(chat_history_window:WindowSpecification,select:bool,number:int,save_detail:bool=False,target_folder:str=None):
    '''该函数用于遍历聊天记录列表获取指定数量文本,并在选中状态下保存图片视频与文件
    Args:
        chat_history_window:聊天记录窗口
        select:是否在选中的状态下遍历
        save_detail:是否保存图片、视频、文件
        target_folder:保存图片、视频、文件的文件夹
        number:指定数量条聊天记录
    Returns:
        texts:指定数量的聊天记录文本
    '''
    file_count=0
    media_count=0
    recorded_num=0
    details=[]
    runtime_ids=[]
    image_label=Special_Labels.Image
    video_label=Special_Labels.Video
    file_label=Special_Labels.File
    chat_history_list=chat_history_window.child_window(**Lists.ChatHistoryList)
    if select:
        latest_message=Tools.select_chat_history_list(chat_history_window)
        if latest_message is None:raise ValueError(f'该聊天只有系统消息,无法在聊天记录界面中选中任何消息!')
    while recorded_num<number:
        selected=[item for item in chat_history_list.children() if item.has_keyboard_focus()]
        if selected:
            #同一个runtime_id挨着重复出现就说明到底部了无法继续下滑
            runtime_ids.append(selected[0].element_info.runtime_id)
            if len(runtime_ids)>2 and runtime_ids[-1]==runtime_ids[-2]:
                break
        if selected and selected[0].class_name()!='mmui::ChatItemView':
            details.append((selected[0].window_text(),selected[0].class_name())) 
            if selected[0].class_name()=='mmui::ChatBubbleReferItemView':
                if video_label in selected[0].window_text() and select and save_detail:
                    pyautogui.press('enter')
                    media_count+=1
                if image_label in selected[0].window_text() and select and save_detail:
                    pyautogui.press('enter')
                    media_count+=1
            if selected[0].class_name()=='mmui::ChatBubbleItemView' and file_label in selected[0].window_text():
                    if select and save_detail:pyautogui.press('enter')
            recorded_num+=1
        pyautogui.press('down',presses=1,_pause=False)
    savable_item_count=file_count+media_count
    if select and save_detail and savable_item_count!=0 and target_folder is not None:
        save_button=chat_history_window.child_window(**Buttons.SaveButton)
        save_button.click_input()
        NativeChooseFolder(target_folder)
    if select and savable_item_count==0:pyautogui.press('esc')
    chat_history_list.type_keys('{HOME}')
    return details

def traverse_chatList(main_window:WindowSpecification,select:bool,number:int):
    '''该函数用于遍历聊天窗口内的消息列表获取指定数量文本
    Args:
        main_window:微信主界面窗口
        select:是否在选中的状态下遍历
        number:指定数量条聊天记录
    Returns:
        texts:指定数量的聊天记录文本
    '''
    texts=[]
    runtime_ids=[]
    recorded_num=0
    chatList=main_window.child_window(**Lists.FriendChatList)
    if select:
        last_item=Tools.select_chatList(main_window)
        if last_item is None:
            raise ValueError(f'该聊天只有系统消息,无法在聊天界面中选中任何消息!')
        if last_item is not None:
            texts.append(last_item.window_text())
            recorded_num+=1
    while recorded_num<number:
        selected=[item for item in chatList.children() if item.has_keyboard_focus()]
        if selected:
            runtime_ids.append(selected[0].element_info.runtime_id)
            if len(runtime_ids)>2 and runtime_ids[-1]==runtime_ids[-2]:
                break
        if selected and selected[0].class_name()!='mmui::ChatItemView':
            texts.append(selected[0].window_text())
            recorded_num+=1
        pyautogui.press('up',presses=1,_pause=False)
    if select:pyautogui.press('esc')
    chatList.type_keys('{END}')
    return texts

def process_audios(audios:list[str],audio_length:int=60):
    '''
    Args:
        audios:所有音频路径列表
        audio_length:音频长度限制,按照微信语音的限制默认只获取前60s
    '''
    #soundfile库支持的格式
    supported_formats={'.WAV', '.AIFF', '.AU', '.RAW', '.PAF', '.SVX', '.NIST', '.VOC', '.IRCAM', '.W64', '.MAT4', '.MAT5', '.PVF', '.XI', 
    '.HTK', '.SDS', '.AVR', '.WAVEX', '.SD2', '.FLAC', '.CAF', '.WVE', '.OGG', '.MPC2K', '.RF64', '.MP3'}
    processed_audios=[]
    for audio_file in audios: 
        #路径存在且文件后缀在支持的音频格式内
        if os.path.exists(audio_file) and os.path.splitext(audio_file)[1].upper() in supported_formats:      
            audio,samplerate=sf.read(audio_file)
            duration=len(audio)//samplerate
            if duration>audio_length:
                samples_to_play=min(audio_length*samplerate,len(audio))
                audio=audio[:samples_to_play]
            processed_audios.append((samplerate,audio))#[(48000,ndarray),(32000,ndarray)...]
    return processed_audios

Special_Labels=Special_Label(language=language)#所有特殊符号或文本
Regex_Patterns=Regex_Pattern(language=language)#所有正则表达式
TimeStamps=TimeStamp(language=language,Version=Version)#所有常用的时间戳
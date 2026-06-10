
import json
import win32gui
import pythoncom
from  pywinauto import Desktop
def check_visibility()->bool:
    '''校验微信ui可见性，只有微信UI树可见，并且已经登录的状态下返回True'''
    pythoncom.CoInitialize()
    desktop=Desktop(backend='uia')
    hwnd=win32gui.FindWindow('Qt51514QWindowIcon','微信')#微信语言是简体中文和繁体中文
    if hwnd==0:hwnd=win32gui.FindWindow('Qt51514QWindowIcon','Weixin')#微信语言是英语
    if hwnd==0:return False#无论什么语言都找不到,说明微信没启动
    main_window=desktop.window(handle=hwnd)#hwnd窗口句柄不为0，说明找到了
    #如果ui树可见class_name是mmui::MainWindow或mmui::LoginWindow，否则还是Qt51514QWindowIcon,
    if 'mmui' in main_window.class_name():return True
    return False
if __name__=='__main__':
    visibility=check_visibility()
    output_json=json.dumps({'visibility':visibility},indent=2)
    print(output_json)
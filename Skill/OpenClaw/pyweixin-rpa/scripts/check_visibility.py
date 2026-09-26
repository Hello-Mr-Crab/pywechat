import json
import win32gui
import pythoncom
from  pywinauto import Desktop
desktop=Desktop(backend='uia')
def get_weixin_hwnd()->int:
    '''获取微信微信窗口句柄
    Returns:
        hwnd:微信窗口句柄,UI树不可见为0
    '''
    def callback(hwnd, _):
        class_name =win32gui.GetClassName(hwnd)
        if class_name=="Qt51514QWindowIcon":
            hwnds.append(hwnd) 
    hwnds=[]
    win32gui.EnumWindows(callback,None)
    hwnds=[hwnd for hwnd in hwnds if 'mmui::' in desktop.window(handle=hwnd).class_name()]
    if not hwnds:return 0
    if hwnds:return hwnds[0]

def check_visibility()->bool:
    '''校验微信ui可见性，只有微信UI树可见，并且已经登录的状态下返回True'''
    pythoncom.CoInitialize()
    hwnd=get_weixin_hwnd()
    if hwnd==0:return False#无论什么语言都找不到,说明微信没启动
    main_window=desktop.window(handle=hwnd)#hwnd窗口句柄不为0，说明找到了
    #如果ui树可见class_name是mmui::MainWindow或mmui::LoginWindow，否则还是Qt51514QWindowIcon,
    if 'mmui' in main_window.class_name():return True
    return False

if __name__=='__main__':
    visibility=check_visibility()
    output_json=json.dumps({'visibility':visibility},indent=2)
    print(output_json)
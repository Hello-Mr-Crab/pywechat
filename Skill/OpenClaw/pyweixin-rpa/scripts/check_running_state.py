import psutil
import json
def is_weixin_running()->bool:
    '''
    该方法通过检测当前windows系统的进程中
    是否有Weixin.exe该项进程来判断微信是否在运行
    '''
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower()=='weixin.exe':
            return True
    return False
if __name__=='__main__':
    is_ruinning=is_weixin_running()
    output_json=json.dumps({'is_running':is_ruinning},indent=2)
    print(output_json)
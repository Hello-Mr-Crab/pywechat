class Config:
    """位置参数全局配置"""
    _instance = None
    def __new__(cls):
        #初始化默认值
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._is_maximize=True
            cls._instance._close_weixin=True
            cls._instance._load_delay=1.5
            cls._instance._search_pages=5
            cls._instance._window_maximize=False
            cls._instance._send_delay=0.2
        return cls._instance
    
    @property
    def is_maximize(self):
        """微信主界面全屏"""
        return self._is_maximize
    
    @is_maximize.setter
    def is_maximize(self,value):
        if not isinstance(value,bool):
            raise TypeError(f"is_maximize必须是bool类型,但传入了{type(value)}:{value}")
        self._is_maximize=value
    
    @property
    def close_weixin(self):
        """任务结束是否关闭微信"""
        return self._close_weixin
    
    @close_weixin.setter
    def close_weixin(self, value):
        if not isinstance(value,bool):
            raise TypeError(f"close_weixin必须是bool类型,但传入了{type(value)}:{value}")
        self._close_weixin=value
    
    @property
    def load_delay(self):
        """打开小程序、视频号、公众号的加载时长"""
        return self._load_delay
    
    @load_delay.setter
    def load_delay(self,value):
        if not isinstance(value,float):
            raise TypeError(f"load_delay必须是float类型,但传入了{type(value)}:{value}")
        self._load_delay=value
    
    @property
    def search_pages(self):
        """会话列表搜索页数"""
        return self._search_pages
    
    @search_pages.setter
    def search_pages(self,value):
        if not isinstance(value,int):
            raise TypeError(f"search_pages必须是int类型,但传入了{type(value)}:{value}")
        self._search_pages=value
    
    @property
    def window_maximize(self):
        """独立窗口全屏"""
        return self._window_maximize
    
    @window_maximize.setter
    def window_maximize(self,value):
        if not isinstance(value,bool):
            raise TypeError(f"window_maximize必须是bool类型,但传入了{type(value)}:{value}")
        self._window_maximize=value
    
    @property
    def send_delay(self):
        """独立窗口全屏"""
        return self._send_delay
    
    @send_delay.setter
    def send_delay(self,value):
        if not isinstance(value,float):
            raise TypeError(f"send_delay必须是float类型,但传入了{type(value)}:{value}")
        self._send_delay=value
#全局实例
GlobalConfig=Config()
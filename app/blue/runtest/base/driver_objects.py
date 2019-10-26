from .base_driver import BaseDriver


class ThreadDriver():
    """
    创建一个单例对象,保存不同的driver然后根据session_id 获取要操作的driver
    """

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            org = super(ThreadDriver, cls)
            cls._instance = org.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        self.driver_dict = {}

    def start(self, phone_info):
        try:
            self.driver = BaseDriver(phone_info).get_driver()
            self.driver_dict[self.driver.session_id] = self.driver
            for k,v in self.driver_dict.items():
                print(k)
                print(v)
            return self.driver
        except Exception as e:
            return '启动会话失败: {}'.format(e)

    def quit(self, session_id):
        try:
            driver = self.driver_dict.get(session_id,'nodriver')
            driver.quit()
            # 删除字典值
            del self.driver_dict[session_id]
            return '退出会话成功: {}'.format(session_id)
        except Exception as e:
            return '退出会话失败: {}'.format(e)

    def get_driver(self, session_id):
        driver = self.driver_dict.get(session_id, '')
        return driver


td = ThreadDriver()

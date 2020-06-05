from wbminitouch import safe_connection, safe_device, MNTDevice, CommandBuilder


class ThreadDevice():
    """
    创建一个单例对象,保存不同的driver然后根据session_id 获取要操作的driver
    """

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            org = super(ThreadDevice, cls)
            cls._instance = org.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        self.device_dict = {}
        self.device_list = []

    def start_device(self,user_id, device_id):
        if device_id in self.device_list:
            return '设备已经开启'
        else:
            device = MNTDevice(device_id)
            if device:
                user_dict = self.device_dict.get(user_id,0)
                if user_dict:
                    user_dict.update({device_id:device})
                else:
                    self.device_dict[user_id] = {device_id:device}
                self.device_list.append(device_id)
                return '设备开启成功'
            else:
                return '设备开启失败'

    def if_device_is_use(self,user_id, device_id):
        if device_id in self.device_list:
            user_device_dict = self.device_dict.get(user_id, 0)
            if user_device_dict:
                if device_id in user_device_dict:
                    return 1
                else:
                    return 0
        else:
            return 2

    def get_device(self,user_id, user_name, device_id):

        if device_id in self.device_list:
            # 如果设备ID已经存在,表明已开启
            user_device_dict =  self.device_dict.get(user_id, 0)
            if user_device_dict:
                if device_id in user_device_dict:
                # 设备已开启,判断是否当前用户开启的
                    device = user_device_dict.get(device_id,0)
                    return (1,device)
                else:
                    return (0,'设备{}已被用户{}使用'.format(device_id,user_name))
        else:
            return (0,'请先连接设备')

    def stop_device(self,user_id, device_id):
        if device_id in self.device_list:
            user_device_dict = self.device_dict.get(user_id,0)
            device = user_device_dict.pop(device_id,0)
            self.device_list.remove(device_id)
            if device:
                device.stop()
                return 1,'{}设备已停止'.format(device_id)
            else:
                return  0,'此设备不属于你'
        else:
            return 0,'设备未开启'

devices = ThreadDevice()

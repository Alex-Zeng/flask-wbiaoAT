from pyminitouch import safe_connection, safe_device, MNTDevice, CommandBuilder


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

    def start_device(self, device_id):
        device = MNTDevice(device_id)
        self.device_dict[device_id] = device
        return device

    def get_device(self, device_id):
        device = self.device_dict.get(device_id, 0)
        if device:
            return device
        else:
            return self.start_device(device_id)

    def stop_device(self, device_id):
        device = self.device_dict.get(device_id, 0)
        if device:
            self.device_dict[device_id].stop()
            device = self.device_dict.pop(device_id,0)
        return device

devices = ThreadDevice()

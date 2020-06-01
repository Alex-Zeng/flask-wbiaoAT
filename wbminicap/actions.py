import time
from contextlib import contextmanager
from wbminicap.connection import MNCAPConnection, MNCAPServer
from wbminicap import config
from wbminicap.utils import restart_adb


class MNCAPDevice(object):

    def __init__(self, device_id):
        self.device_id = device_id
        self.server = None
        self.connection = None
        self.start()

    def reset(self):
        self.stop()
        self.start()

    def start(self):
        # prepare for connection
        self.server = MNCAPServer(self.device_id)
        # real connection
        self.connection = MNCAPConnection(self.server.port)

    def stop(self):
        self.connection.disconnect()
        self.server.stop()


@contextmanager
def safe_device(device_id):
    """ use MNCAPDevice safely """
    _device = MNCAPDevice(device_id)
    try:
        yield _device
    finally:
        time.sleep(config.DEFAULT_DELAY)
        _device.stop()


if __name__ == "__main__":
    restart_adb()

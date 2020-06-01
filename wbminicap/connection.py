import subprocess
import socket
import time
import os
import random
from contextlib import contextmanager
import threading
# from multiprocessing import Process,Queue
from queue import Queue
from wbminicap.logger import logger
from wbminicap import config
from wbminicap.utils import (
    str2byte,
    download_file,
    is_port_using,
    is_device_connected,
)

_ADB = config.ADB_EXECUTOR


class MNTInstaller(object):
    """ install minicap for android devices """

    def __init__(self, device_id):
        self.device_id = device_id
        self.abi = self.get_abi()
        if self.is_mnt_existed():
            logger.info("minicap already existed in {}".format(device_id))
        else:
            self.download_target_mnt()

    def get_abi(self):
        abi = subprocess.getoutput(
            "{} -s {} shell getprop ro.product.cpu.abi".format(_ADB, self.device_id)
        )
        logger.info("device {} is {}".format(self.device_id, abi))
        return abi


    def download_target_mnt(self):
        abi = self.get_abi()
        target_url = "{}/{}/bin/minicap".format(config.MNT_PREBUILT_URL, abi)
        logger.info("target minicap url: " + target_url)
        mnt_path = download_file(target_url)

        # push and grant
        subprocess.check_call(
            [_ADB, "-s", self.device_id, "push", mnt_path, config.MNT_HOME]
        )
        subprocess.check_call(
            [_ADB, "-s", self.device_id, "shell", "chmod", "777", config.MNT_HOME]
        )
        logger.info("minicap already installed in {}".format(config.MNT_HOME))

        # remove temp
        os.remove(mnt_path)

    def is_mnt_existed(self):

        file_list = subprocess.check_output(
            [_ADB, "-s", self.device_id, "shell", "ls", "/data/local/tmp"]
        )
        return "minicap" in file_list.decode(config.DEFAULT_CHARSET)


class MNCAPServer(object):
    """
    manage connection to minicap.
    before connection, you should execute minicap with adb shell.

    command eg::

        adb forward tcp:{some_port} localabstract:minicap
        adb shell /data/local/tmp/minicap

    you would better use it via safe_connection ::

        _DEVICE_ID = '123456F'

        with safe_connection(_DEVICE_ID) as conn:
            conn.send('d 0 500 500 50\nc\nd 1 500 600 50\nw 5000\nc\nu 0\nu 1\nc\n')
    """

    _PORT_SET = config.PORT_SET

    def __init__(self, device_id):
        assert is_device_connected(device_id)

        self.device_id = device_id
        logger.info("searching a usable port ...")
        self.port = self._get_port()
        logger.info("device {} bind to port {}".format(device_id, self.port))

        # check minicap
        self.installer = MNTInstaller(device_id)

        # keep minicap alive
        self._forward_port()
        self.mncap_process = None
        self._start_mnt()

        # make sure it's up
        time.sleep(1)
        assert (
            self.heartbeat()
        ), "minicap did not work. see https://github.com/williamfzc/pyminicap/issues/11"

    def stop(self):
        self.mncap_process and self.mncap_process.kill()
        self._PORT_SET.add(self.port)
        logger.info("device {} unbind to {}".format(self.device_id, self.port))

    @classmethod
    def _get_port(cls):
        """ get a random port from port set """
        new_port = random.choice(list(cls._PORT_SET))
        if is_port_using(new_port):
            return cls._get_port()
        return new_port

    def _get_size(self):
        out_put = subprocess.check_output(
            [_ADB, "-s", self.device_id, "shell", "wm", "size"]
        )

        size = out_put.decode('utf-8').split(': ')[1].strip()
        return size

    def _forward_port(self):
        """ allow pc access minicap with port """
        command_list = [
            _ADB,
            "-s",
            self.device_id,
            "forward",
            "tcp:{}".format(self.port),
            "localabstract:minicap",
        ]
        logger.debug("forward command: {}".format(" ".join(command_list)))
        output = subprocess.check_output(command_list)
        logger.debug("output: {}".format(output))

    def _start_mnt(self):
        """ fork a process to start minicap on android """
        # adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 540x960@340x720/0
        size = self._get_size().split('x')
        real_x = size[0]
        real_y = size[1]
        virtual_x = config.VIRTUAL_X
        virtual_y =config.VIRTUAL_Y
        command_list = [
            _ADB,
            "-s",
            self.device_id,
            "shell",
            "LD_LIBRARY_PATH=/data/local/tmp",
            "/data/local/tmp/minicap",
            "-P",
            "{}x{}@{}x{}/0".format(real_x,real_y,virtual_x,virtual_y),
        ]

        logger.info("start minicap: {}".format(" ".join(command_list)))
        self.mncap_process = subprocess.Popen(command_list, stdout=subprocess.DEVNULL)

    def heartbeat(self):
        """ check if minicap process alive """
        return self.mncap_process.poll() is None


class Banner:

    def __init__(self):
        self.Version = 0  # 版本信息
        self.Length = 0  # banner长度
        self.Pid = 0  # 进程ID
        self.RealWidth = 0  # 设备的真实宽度
        self.RealHeight = 0  # 设备的真实高度
        self.VirtualWidth = 0  # 设备的虚拟宽度
        self.VirtualHeight = 0  # 设备的虚拟高度
        self.Orientation = 0  # 设备方向
        self.Quirks = 0  # 设备信息获取策略

    def toString(self):
        message = "Banner [Version=" + str(self.Version) + ", length=" + str(self.Length) + ", Pid=" + str(
            self.Pid) + ", realWidth=" + str(self.RealWidth) + ", realHeight=" + str(
            self.RealHeight) + ", virtualWidth=" + str(self.VirtualWidth) + ", virtualHeight=" + str(
            self.VirtualHeight) + ", orientation=" + str(self.Orientation) + ", quirks=" + str(self.Quirks) + "]"
        return message


class MNCAPConnection(object):
    """ manage socket connection between pc and android """

    _DEFAULT_HOST = config.DEFAULT_HOST
    _DEFAULT_BUFFER_SIZE = config.DEFAULT_BUFFER_SIZE

    def __init__(self, port):
        self.port = port
        self.Pid = 0  # 进程ID
        self.banner = Banner()  # 用于存放banner头信息
        #         self.minicapSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ReadImageStreamTask = None
        self.push = None
        self.picture = Queue()
        self.data = b''
        # build connection
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self._DEFAULT_HOST, self.port))
        self.client = client

    def run(self):
        # 开始执行
        p1 = threading.Thread(target=self.ReadImageStream)
        p1.start()

    def ReadImageStream(self):
        # get minicap server info
        readBannerBytes = 0
        bannerLength = 2
        readFrameBytes = 0
        frameBodylength = 0
        dataBody = b""
        while self.client:
            try:
                reallen = self.client.recv(4096)
                length = len(reallen)
                if not length:
                    continue
                cursor = 0
                while cursor < length:
                    # 获取图片头部信息
                    if readBannerBytes < bannerLength:
                        if readBannerBytes == 0:
                            self.banner.Version = reallen[cursor]
                        elif readBannerBytes == 1:
                            bannerLength = reallen[cursor]
                            self.banner.Length = bannerLength
                        elif readBannerBytes in [2, 3, 4, 5]:
                            self.banner.Pid += (reallen[cursor] << ((readBannerBytes - 2) * 8)) >> 0
                        elif readBannerBytes in [6, 7, 8, 9]:
                            self.banner.RealWidth += (reallen[cursor] << ((readBannerBytes - 6) * 8)) >> 0
                        elif readBannerBytes in [10, 11, 12, 13]:
                            self.banner.RealHeight += (reallen[cursor] << ((readBannerBytes - 10) * 8)) >> 0
                        elif readBannerBytes in [14, 15, 16, 17]:
                            self.banner.VirtualWidth += (reallen[cursor] << (
                                    (readBannerBytes - 14) * 8)) >> 0
                        elif readBannerBytes in [18, 19, 20, 21]:
                            self.banner.VirtualHeight += (reallen[cursor] << (
                                    (readBannerBytes - 18) * 8)) >> 0
                        elif readBannerBytes == 22:
                            self.banner.Orientation = reallen[cursor] * 90
                        elif readBannerBytes == 23:
                            self.banner.Quirks = reallen[cursor]
                        cursor += 1
                        readBannerBytes += 1
                        if readBannerBytes == bannerLength:
                            logger.info(self.banner.toString())
                    elif readFrameBytes < 4:
                        # 第一个过来的图片信息的前4个字符不是图片的二进制信息，而是携带着图片大小的信息
                        frameBodylength = frameBodylength + ((reallen[cursor] << (readFrameBytes * 8)) >> 0)
                        cursor += 1
                        readFrameBytes += 1
                        # print('{} - {} '.format(cursor,frameBodylength))
                    else:
                        # 真正获取图片信息,比如我们接受到的信息长度为n,4～n部分是图片的信息，需要保存下来。
                        # print('{} - {} - {} '.format(length,cursor, frameBodylength))
                        if length - cursor >= frameBodylength:
                            dataBody = dataBody + (reallen[cursor:(cursor + frameBodylength)])
                            if dataBody[0] != 0xFF or dataBody[1] != 0xD8:
                                return
                            self.picture.put(dataBody)
                            # self.save_file('d:/pic.png', dataBody)
                            cursor += frameBodylength
                            frameBodylength = 0
                            readFrameBytes = 0
                            dataBody = b""
                        else:
                            dataBody = dataBody + reallen[cursor:length]
                            frameBodylength -= length - cursor
                            readFrameBytes += length - cursor
                            cursor = length
            except:
                logger.info('退出线程')
                break

    def disconnect(self):
        self.client and self.client.close()
        self.client = None
        logger.info("minicap disconnected")

    def send(self, content):
        """ send message and get its response """
        byte_content = str2byte(content)
        self.client.sendall(byte_content)
        logger.info("touch: {}".format(byte_content))
        return self.client.recv(self._DEFAULT_BUFFER_SIZE)


@contextmanager
def safe_connection(device_id):
    """ safe connection runtime to use """

    # prepare for connection
    server = MNCAPServer(device_id)
    # real connection
    connection = MNCAPConnection(server.port)
    try:
        yield connection
    finally:
        # disconnect
        connection.disconnect()
        server.stop()


if __name__ == "__main__":
    _DEVICE_ID = "127.0.0.1:7555"

    with safe_connection(_DEVICE_ID) as conn:
        # conn.send('d 0 150 150 50\nc\nu 0\nc\n')
        conn.send("d 0 10 300 50\nc\nu 0\nc\n")

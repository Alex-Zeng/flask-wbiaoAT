import socket
import threading
# from multiprocessing import Process,Queue
from queue import Queue
import sys
import os
from flask_sockets import Sockets
import time
from gevent import monkey
from flask import Flask
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")
monkey.patch_all()

#TODO 命令启动关闭服务
class MinicapServer:
    def __init__(self):

        self.app = Flask(__name__)
        self.sockets = Sockets(self.app)
        self.now = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))

    def start_minicap_server(self):
        server = pywsgi.WSGIServer(('0.0.0.0', 9090), self.app, handler_class=WebSocketHandler)
        server.serve_forever()

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


class MinicapStream:
    __instance = None
    __mutex = threading.Lock()

    def __init__(self):
        self.IP = "127.0.0.1"  # 定义IP
        self.PORT = 1717  # 监听的端口
        self.Pid = 0  # 进程ID
        self.banner = Banner()  # 用于存放banner头信息
        #         self.minicapSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.minicapSocket = None
        self.ReadImageStreamTask = None
        self.push = None
        self.picture = Queue()
        self.data = b''

    @staticmethod
    def getBuilder():
        """Return a single instance of TestBuilder object """
        if (MinicapStream.__instance == None):
            MinicapStream.__mutex.acquire()
            if (MinicapStream.__instance == None):
                MinicapStream.__instance = MinicapStream()
            MinicapStream.__mutex.release()
        return MinicapStream.__instance

    def get_d(self):
        print(self.picture.qsize())

    def run(self):
        # 开始执行
        # 启动socket连接
        p1 = threading.Thread(target=self.ReadImageStream)
        p1.start()
        # p1.join()


    def ReadImageStream(self):
        self.minicapSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 定义socket类型，网络通信，TCP
        self.minicapSocket.connect((self.IP, self.PORT))
        # 读取图片流到队列

        readBannerBytes = 0
        bannerLength = 2
        readFrameBytes = 0
        frameBodylength = 0
        dataBody = b""
        while True:
            reallen = self.minicapSocket.recv(4096)
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
                        print(self.banner.toString())
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

    # adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 1200x1920@1200x1920/0
    #             adb forward tcp:1313 localabstract:minicap

    def save_file(self, file_name, data):
        print(file_name)
        file = open(file_name, "wb")
        file.write(data)
        file.flush()
        file.close()

@sockets.route('/test')  # 指定路由
def echo_socket(ws):
    # sockets连接过来,启动进程从设备获取图片并处理,存入队列
    a = MinicapStream.getBuilder()
    a.run()

    # 从图片队列或缺图片,持续发送到前端
    images = a.picture
    while True:
        ws.send(bytearray(images.get()))


if __name__ == '__main__':
    #
    server = pywsgi.WSGIServer(('0.0.0.0', 9090), app, handler_class=WebSocketHandler)
    print(server.get_environ())
    print('server start')
    server.serve_forever()
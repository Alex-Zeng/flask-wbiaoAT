from gevent import monkey
monkey.patch_all()
import argparse
from wbminicap import MNCAPDevice
import sys
import os
from ext import minicap_server
from flask_sockets import Sockets
import time
from flask import Flask
from flask_cors import CORS
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")

# python \workspace\UIAtuoTest\minicapServer.py  -ms=127.0.0.1 -mp=9090
# adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 540x960@340x720/0
# adb forward tcp:1717 localabstract:minicap

# parser = argparse.ArgumentParser()
# parser.add_argument('-ms','--ms_host',type=str,help="服务端提供给前端的套接字地址")
# parser.add_argument('-mp','--ms_port',type=int,help="服务端提供给前端的套接字端口")
# args = parser.parse_args()
args={}
args['ms_host'] ='127.0.0.1'
args['ms_port'] =9090
# args['ms_host'] =
# args['ms_host'] =

app = Flask(__name__)
sockets = Sockets(app)
now = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
server = pywsgi.WSGIServer((args['ms_host'], args['ms_port']), app, handler_class=WebSocketHandler)
CORS(app, supports_credentials=True)
device_ob = {}
minicap_server[args['ms_port']] = server
@sockets.route('/getScreen/<string:device_name>')
def echo_socket(ws,device_name):
    # sockets连接过来,启动进程从设备获取图片并处理,存入队列

        if device_ob.get(device_name, 0):
            # 保证每台设备同时只被一个用户操纵
            ws.send('1'.encode('utf-8'))
        else:

            device = MNCAPDevice(device_name)
            device_ob[device_name] = device
            conn = device.connection
            # 从图片队列或缺图片,持续发送到前端
            conn.run()
            images = conn.picture
            try:
                while True:
                    ws.send(bytearray(images.get()))
            except Exception as e:
                device.stop()


@sockets.route('/stopMiniServer/<string:device_name>')
def stop_minicap_server(ws,device_name):
    device = device_ob.pop(device_name, 0)
    if device:
        device.stop()
        ws.send(1)


if __name__ == '__main__':
    server.serve_forever()
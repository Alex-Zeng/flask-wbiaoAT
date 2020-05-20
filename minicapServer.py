from gevent import monkey
monkey.patch_all()
import argparse
from wbminitouch import MinicapStream
import sys
import os
from flask_sockets import Sockets
import time
from flask import Flask
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")


#TODO 命令启动关闭服务
parser = argparse.ArgumentParser()
parser.add_argument('-ph','--pm_host',type=str,help="手机minicap地址")
parser.add_argument('-pp','--pm_port',type=int,help="手机minicap端口")
parser.add_argument('-ms','--me_host',type=str,help="服务端提供给前端的套接字地址")
parser.add_argument('-mp','--ms_port',type=str,help="服务端提供给前端的套接字端口")
args = parser.parse_args()


app = Flask(__name__)
sockets = Sockets(app)
now = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))

@sockets.route('/test')
def echo_socket(ws):
    # sockets连接过来,启动进程从设备获取图片并处理,存入队列
    a = MinicapStream(host=args.pm_host,port=args.pm_port)
    a.run()

    # 从图片队列或缺图片,持续发送到前端
    images = a.picture
    while True:
        ws.send(bytearray(images.get()))


def start_minicap_server():
    server = pywsgi.WSGIServer((args.me_host, args.ms_port), app, handler_class=WebSocketHandler)
    server.serve_forever()



if __name__ == '__main__':
    #
    start_minicap_server()
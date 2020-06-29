from main import app
from gevent.pywsgi import WSGIServer
from minicapServer import server
from multiprocessing import Process

def auto_test_server():
    print('开启自动化服务')
    http_server = WSGIServer(('localhost', 5002), app)
    http_server.serve_forever()
    print('自动化服务结束')

def minicap_server():
    print('开启minicap服务')
    server.serve_forever()
    print('minicap服务结束')

if __name__ == '__main__':
    p1 = Process(target=auto_test_server)  # 必须加,号
    p2 = Process(target=minicap_server)
    p1.start()
    p2.start()
    p2.join()
    p1.join()
    print('所有进程结束')

from main import app
from gevent.pywsgi import WSGIServer

if __name__ == '__main__':
    http_server = WSGIServer(('', 5002), app)
    http_server.serve_forever()
    # app.run(port=5002,threaded=True)
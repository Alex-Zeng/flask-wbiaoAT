from main import app
from gevent.pywsgi import WSGIServer

if __name__ == '__main__':
    # from apscheduler.schedulers.gevent import GeventScheduler
    #
    #
    # def my_job(text):
    #     print(111111)
    #     print(text)
    #
    #
    # sched = GeventScheduler()
    # text = '123'
    # sched.add_job(my_job, 'interval', seconds=5, id='1', args=[text])
    # sched.start()
    # sched.print_jobs()

    http_server = WSGIServer(('', 5002), app)
    http_server.serve_forever()
    # app.run(port=5002,threaded=True)
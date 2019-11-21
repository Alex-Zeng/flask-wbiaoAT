from multiprocessing import Pool
import os,time,random
from base.public.log import log_main

def run_test_task(name):
    log_main.info('正在运行的任务：%s，PID：（%s）' % (name, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 10)
    end = time.time()
    log_main.info('任务：%s，用时：%0.2f 秒' % (name, (end - start)))


if __name__ == '__main__':
    log_main.info('父进程ID：%s' % (os.getpid()))
    p = Pool(2)
    for i in range(2):
        p.apply_async(run_test_task, args=(i,))
    log_main.info('等待所有添加的进程运行完毕。。。')
    p.close()  # 在join之前要先关闭进程池，避免添加新的进程
    p.join()
    log_main.info('End!!,PID:%s' % os.getpid())
import os
from base.runtest_config import rtconf

path = rtconf.logDir
# 遍历文件夹
def walkFile(file):
    for root, dirs, files in os.walk(file):

        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list

        # 遍历文件
        print(files)
            # print(os.path.join(root, f))


def main():
    walkFile(path)


if __name__ == '__main__':
    main()
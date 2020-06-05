import platform
import subprocess


# connection
DEFAULT_HOST = "127.0.0.1"
PORT_SET = set(range(21000, 22000))
DEFAULT_BUFFER_SIZE = 0
DEFAULT_CHARSET = "utf-8"

# operation
DEFAULT_DELAY = 0.05

# installer
MNT_PREBUILT_URL = r"https://github.com/Alex-Zeng/stf-binaries/tree/master/node_modules/minicap-prebuilt/prebuilt"
MNT_HOME = "/data/local/tmp/minicap"

# system
# 'Linux', 'Windows' or 'Darwin'.
SYSTEM_NAME = platform.system()
NEED_SHELL = SYSTEM_NAME != "Windows"
ADB_EXECUTOR = "adb"

# minicap 虚拟屏幕像素大小
VIRTUAL_X = 0.3
VIRTUAL_Y = 0.3
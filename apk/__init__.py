import os
curPath = os.path.abspath(os.path.dirname(__file__))
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)
apk_path  = PATH(curPath)
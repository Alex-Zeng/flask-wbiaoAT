#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/16 13:41
# @Author  : 曾德辉
# @File    : __init__.py.py
from itsdangerous import BadData, constant_time_compare
from ext import login_manager, simple_cache
from flask import jsonify, request
from app.models.uitest import *
from app.models.run_test import *

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'status': 2, 'data': {'url': request.url}, 'msg': "未登录,请先登陆"})


def load_token(token):
    # 通过loads()方法来解析浏览器发送过来的token，从而进行初步的验证
    key = current_app.config.get("SECRET_KEY", "The securet key by C~C!")

    try:
        s = URLSafeSerializer(key)
        id, name, password, browser_id, life_time = s.loads(token)
    except BadData:
        print("token had been modified!")
        return None

    # 判断浏览器信息是否改变
    bi = create_browser_id()
    if not constant_time_compare(str(bi), str(browser_id)):
        print("the user environment had changed, so token has been expired!")
        return None

    # 校验密码
    user = User.query.get(id)
    if user:
        # 能loads出id，name等信息，说明已经成功登录过，那么cache中就应该有token的缓存
        token_cache = simple_cache.get(token)
        if not token_cache:  # 此处找不到有2个原因：1.cache中因为超时失效（属于正常情况）；2.cache机制出错（属于异常情况）。
            print("the token is not found in cache.")
            return None
        if str(password) != str(user.password):
            print("the password in token is not matched!")
            simple_cache.delete(token)
            return None
        else:
            simple_cache.set(token, 1, timeout=life_time)  # 刷新超时时长
    else:
        print('the user is not found, the token is invalid!')
        return None
    return user


@login_manager.user_loader
def user_loader(token):
    """
    校验token
    这里的入参就是get_id()的返回值
    """
    return load_token(token)
import re

from django.contrib.auth.backends import ModelBackend
from .models import User


def get_user_by_account(account):
    """
    根据account查询用户
    :param account: 用户名或手机号
    :return: user
    """
    try:
        # 手机号登陆
        if re.match(r'^1[345789]\d{9}$', account):
            user = User.objects.get(mobile=account)
        # 用户名登陆
        else:
            user = User.objects.get(username=account)
    except Exception:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义用户认证后端"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写认证方法,实现用户名和手机号都能登陆的功能
        :param request: 请求对象
        :param username: 用户名
        :param password: 密码
        :param kwargs: 其他参数
        :return: user
        """
        # 自定义验证用户是否存在的函数
        # 根据传入的username获取user对象
        # username可以是手机号也可以是账号
        user = get_user_by_account(username)
        # 如果此次身份认证是后台站点登陆,则只允许超级管理员登陆
        if request is None:
            if user.is_staff != 1:
                return None
        # 校验user是否存在并校验密码是否正确
        if user and user.check_password(password):
            return user

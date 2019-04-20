import re

from django import http
from django.contrib.auth import login
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

# Create your views here.
from meiduo_mall.utils.response_code import RETCODE
from .models import User


class MobileCountView(View):
    """判断手机号是否重复注册"""

    # /mobiles/(?P<mobile>1[3-9]\d{9})/count/
    def get(self, request, mobile):
        """
        获取手机号,查询手机号在数据库中的个数并返回
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        # 去数据库中查询该手机号的个数
        count = User.objects.filter(mobile=mobile).count()
        # 返回状态码,错误信息和个数
        return http.JsonResponse({'code': 'RETCODE.OK', 'errmsg': 'OK', 'count': count})


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    # / usernames / (?P < username >[a-zA-Z0-9_-]{5, 20}) / count /
    def get(self, request, username):
        """
        获取用户名,查询用户名在数据库中的个数并返回
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        # 去数据库中查询该用户名的个数
        count = User.objects.filter(username=username).count()
        # 返回状态码,错误信息和个数
        return http.JsonResponse({'code': 'RETCODE.OK', 'errmsg': 'OK', 'count': count})


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """
        提供注册界面
        :param request:请求对象
        :return:注册页面
        """
        return render(request, 'register.html')

    def post(self, request):
        """
        实现用户注册
        :param request:请求对象
        :return:注册结果
        """
        # 1.接收请求,提取参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        # TODO sms_code短信验证码没写
        # 2.校验参数
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden('您输入的手机号格式不正确')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')
        # 3.保存注册数据
        try:
            # 调用create_user方法会对密码进行自动加密,如调用create方法,需手动加密
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '保存注册数据失败'})
        # 实现状态保持
        # login方法中封装了request.session[key] = value,可实现保存用户信息功能
        # login方法必需两个参数,第一个request,第二个user.    create_user方法会返回user
        login(request, user)
        # 4.响应注册结果
        # return http.HttpResponse('注册成功,应该跳转到首页')
        return redirect(reverse('contents:index'))

import re

from django import http
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

# Create your views here.
from .models import User


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
            User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '保存注册数据失败'})
        # 4.响应注册结果
        # return http.HttpResponse('注册成功,应该跳转到首页')
        return redirect(reverse('contents:index'))

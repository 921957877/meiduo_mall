import re

from django import http
from django.contrib.auth import login, authenticate, logout
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredMixin
from .models import User
from django_redis import get_redis_connection


# Create your views here.
# 定义我们自己的类视图, 需要让它继承自: 工具类 + View
class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """提供个人信息界面"""
        return render(request, 'user_center_info.html')


class LoginoutView(View):
    """退出登陆"""

    def get(self, request):
        """实现退出登陆逻辑"""
        # 清理session
        logout(request)
        # 退出登陆,重定向到首页
        response = redirect(reverse('contents:index'))
        # 退出登陆时删除cookie中的username
        response.delete_cookie('username')
        # 返回响应
        return response


class LoginView(View):
    """用户登陆"""

    def get(self, request):
        """
        提供登陆界面
        :param request: 请求对象
        :return: 登陆界面
        """
        return render(request, 'login.html')

    def post(self, request):
        """
        实现登陆逻辑
        :param request: 请求对象
        :return: 登陆结果
        """
        # 1.接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 2.校验参数
        # 判断参数是否齐全 由于remembered 这个参数可以是 None 或是 'on'，所以不对它是否存在进行判断
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 3.查看数据库中是否存在该账户,如存在返回对象,不存在返回None
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
        # 4.状态保持
        login(request, user)
        # 根据用户的选择设置状态保持的时间
        # 不记住登陆,0表示关闭浏览器就过期
        if remembered is None:
            request.session.set_expiry(0)
        # 记住登陆,None表示默认过期时间:两周后过期
        else:
            request.session.set_expiry(None)
        # 5.登陆成功,重定向到首页
        # return redirect(reverse('contents:index'))
        # 获取要前往的地址
        next = request.GET.get('next')
        # 生成响应对象
        # 判断参数是否存在
        if next:
            # 如果不是从首页来的,则重定向到要前往的地址
            response = redirect(next)
        else:
            # 如果从首页来的,则重定向到首页
            response = redirect(reverse('contents:index'))
        # 在cookie中设置用户名信息,有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # 返回响应对象
        return response


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
        sms_code_client = request.POST.get('sms_code')
        allow = request.POST.get('allow')
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
        # 校验短信验证码
        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 从redis数据库中获取暂存的短信验证码
        sms_code_server = redis_conn.get('sms_code_%s' % mobile)
        # 判断暂存在redis数据库中的验证码是否存在
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已失效'})
        # 校验
        if sms_code_server.decode() != sms_code_client:
            return render(request, 'register.html', {'sms_code_errmsg': '输入验证码有误'})
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
        # return redirect(reverse('contents:index'))
        # 生成响应对象
        response = redirect(reverse('contents:index'))
        # 在cookie中设置用户名信息,有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        # 返回响应对象
        return response

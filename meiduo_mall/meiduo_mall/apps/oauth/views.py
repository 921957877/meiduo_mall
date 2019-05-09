import re
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.contrib.auth import login
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse

from carts.utils import merge_cart_cookie_to_redis
from oauth.models import OAuthQQUser
from oauth.utils import generate_access_token, check_access_token
from users.models import User
from django.views import View
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection
import logging

logger = logging.getLogger('django')


# Create your views here.
class QQUserView(View):
    """用户扫码登陆的回调处理"""

    def get(self, request):
        """
        实现QQ登陆的第二个接口,用于接收前端发来的code值,拿着code值去QQ服务器换取access_token,
        拿着access_token换取openid,再拿着openid去数据库中查看用户是否是第一次进行QQ登陆
        如用户不是第一次,则直接登陆成功
        如用户是第一次,则把openid加密生成access_token并返回给前端
        :param request: 请求对象
        :return: 登陆成功或access_token
        """
        # 1.接收code参数
        code = request.GET.get('code')
        # 2.校验参数,判断code是否存在
        if not code:
            return http.HttpResponseForbidden('缺少code参数')
        # 3.创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 4.携带code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)
            # 5.携带access_token向eQQ服务器请求openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('oauth2.0认证失败')
        # 6.判断用户账号是否使用QQ登陆过(openid是否在数据库中)
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        # 6.1 用户账号没使用QQ登陆过(openid不在数据库中)
        except OAuthQQUser.DoesNotExist:
            # 把openid加密成access_token
            access_token = generate_access_token(openid)
            context = {'access_token': access_token}
            # 返回access_token并跳转到绑定页面
            return render(request, 'oauth_callback.html', context)
        # 6.2 用户账号使用QQ登陆过(openid在数据库中)
        else:
            # 根据user外键,获取对应的QQ用户
            qq_user = oauth_user.user
            # 实现状态保持
            login(request, qq_user)
            # # 创建重定向到首页的对象
            # response = redirect(reverse('contents:index'))
            # 重定向到首页或用户要前往的页面
            next = request.GET.get('state')
            if next:
                response = redirect(next)
            else:
                response = redirect(reverse('contents:index'))
            # 将用户名写入cookie,有效期15天
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 15)
            # 合并购物车数据
            response = merge_cart_cookie_to_redis(request, response)
            # 返回响应
            return response

    def post(self, request):
        """
        实现QQ登陆的第三个接口,用于接收前端发来的手机号,密码,短信验证码,access_token,校验这些参数后,
        查看数据库中是否有用户数据
        如有,直接将openid绑定用户数据
        如没有,创建用户数据并绑定openid
        :param request: 请求对象
        :return: 响应结果
        """
        # 1.接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token = request.POST.get('access_token')
        # 2.校验参数
        # 判断参数是否齐全
        if not all([mobile, password, sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断手机号是否合法
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden('您输入的手机号格式不正确')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致
        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 从redis数据库中获取保存的短信验证码值
        sms_code_server = redis_conn.get('sms_code_%s' % mobile)
        # 如果获取的为空
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '短信验证码已失效'})
        # 如果用户输的验证码和数据库中存的不一致
        if sms_code_server.decode() != sms_code_client:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '短信验证码输入错误'})
        # 校验access_token
        # 把access_token解密成openid
        openid = check_access_token(access_token)
        # 如果openid不存在
        if openid is None:
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'access_token不正确'})
        # 查看数据库中是否有用户数据
        try:
            user = User.objects.get(mobile=mobile)
        # 没有,创建用户数据
        except User.DoesNotExist:
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        # 有,检查密码
        else:
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'account_errmsg': '密码错误'})
        # openid绑定用户数据
        try:
            OAuthQQUser.objects.create(user=user, openid=openid)
        except DatabaseError:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': '绑定用户失败'})
        else:
            # 实现状态保持
            login(request, user)
            # 重定向到首页或用户要前往的页面
            next = request.GET.get('state')
            if next:
                response = redirect(next)
            else:
                response = redirect(reverse('contents:index'))
            # 登录时用户名写入到 cookie，有效期15天
            response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
            # 合并购物车数据
            response = merge_cart_cookie_to_redis(request, response)
            # 返回响应
            return response


class QQURLView(View):
    """提供QQ登陆页面网址"""

    def get(self, request):
        """
        实现QQ登陆的第一个接口:用于接收前端发送来的next参数,返回QQ登陆网址
        :param request:  请求对象
        :return:  QQ登陆网址
        """
        # 1.接收参数(该参数不是必传)
        next = request.GET.get('next')
        # 2.创建工具类(QQLoginTool)的对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # 3.调用对象生成QQ登陆网址的方法
        login_url = oauth.get_qq_url()
        # 4.返回登陆地址
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'login_url': login_url})

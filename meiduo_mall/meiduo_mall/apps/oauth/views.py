from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
import logging

from django.urls import reverse

from oauth.models import OAuthQQUser
from oauth.utils import generate_access_token

logger = logging.getLogger('django')
# Create your views here.
from django.views import View

from meiduo_mall.utils.response_code import RETCODE


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
        # 用户账号没使用QQ登陆过(openid不在数据库中)
        except OAuthQQUser.DoesNotExist:
            # 把openid加密成access_token
            access_token = generate_access_token(openid)
            context = {'access_token': access_token}
            # 返回access_token并跳转到绑定页面
            return render(request, 'oauth_callback.html', context)
        # 用户账号使用QQ登陆过(openid在数据库中)
        else:
            # 根据user外键,获取对应的QQ用户
            qq_user = oauth_user.user
            # 实现状态保持
            login(request, qq_user)
            # 创建重定向到首页的对象
            response = redirect(reverse('contents:index'))
            # 将用户名写入cookie,有效期15天
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 15)
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

from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from django.views import View

from meiduo_mall.utils.response_code import RETCODE


class QQUrlView(View):
    """提供QQ登陆页面网址"""

    def get(self, request):
        # 1.接收参数(该参数不是必传)
        next = request.GET.get('next')
        # 2.创建工具类(QQLoginTool)的对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # 3.调用对象生成QQ登陆网址的方法
        login_url = oauth.get_qq_url()
        # 4.返回登陆地址
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'login_url': login_url})

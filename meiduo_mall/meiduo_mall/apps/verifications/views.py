from django import http
from django.shortcuts import render

from django.views import View
# Create your views here.
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection


class ImageCodeView(View):
    """图片验证码"""

    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属于的用户
        :return: image/jpg
        """
        # 1.生成图片
        text, image = captcha.generate_captcha()
        # 2.服务端保存:redis
        # 2.1 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 2.2 保存信息  setex(name, time, value)
        redis_conn.setex('img_code_%s' % uuid, 300, text)
        # 3.返回:图片  HttpResponse(content=响应体, content_type=‘响应体数据类型’, status=状态码(100-599))
        return http.HttpResponse(image, content_type='image/jpg')

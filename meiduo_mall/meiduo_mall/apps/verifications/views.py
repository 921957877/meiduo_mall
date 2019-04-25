import random

from django import http
from django.shortcuts import render

from django.views import View
# Create your views here.
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from meiduo_mall.libs.yuntongxun.ccp_sms import CCP
from meiduo_mall.utils.response_code import RETCODE
import logging

logger = logging.getLogger('django')


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        # 创建连接到redis的对象
        redis_conn = get_redis_connection('verify_code')
        # 避免频繁发送短信验证码
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 1.接收参数  查询字符串:request.GET  表单:request.POST
        # 获取客户端发送来的图形验证码
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        # 2.校验参数
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

        # 4.获取暂存在redis中的图形验证码
        image_code_server = redis_conn.get('img_code_%s' % uuid)

        # 图形验证码过期或不存在
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码已失效'})
        # 5.删除存放在redis中的图形验证码，防止恶意测试图形验证码
        try:
            redis_conn.delete('img_code_%s' % uuid)
        except Exception as e:
            logger.error(e)
        # 6.对比图形验证码
        # 由于从redis数据库中取出来的数据都是bytes格式,所以需要进行解码,把二进制变为字符串
        if image_code_server.decode().lower() != image_code_client.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入的验证码有误'})
        # 7.生成6位数的短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)
        # 8.暂存短信验证码到redis数据库,有效期为5分钟
        # pipeline通过减少客户端与Redis的通信次数来实现降低往返延时时间
        # 创建redis管道
        pl = redis_conn.pipeline()
        # 将redis请求添加到队列
        pl.setex('sms_code_%s' % mobile, 300, sms_code)
        pl.setex('send_flag_%s' % mobile, 60, 1)
        # 执行管道
        pl.execute()
        # 9.发送短信验证码
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # from celery_tasks.sms.tasks import send_sms_code TODO
        # send_sms_code.delay(mobile, sms_code)
        # 10.响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


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

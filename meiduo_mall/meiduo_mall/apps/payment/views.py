import os

from alipay import AliPay
from django import http
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from django.views import View

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJsonMixin
from orders.models import OrderInfo


class PaymentView(LoginRequiredJsonMixin, View):
    """支付宝第一个接口:接收order_id,返回支付宝支付网址"""

    def get(self, request, order_id):
        # 校验order_id
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=request.user,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')
        # 创建支付宝支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        # 生成登陆支付宝链接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
        )
        # 拼接支付宝支付网址
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        # 返回支付宝支付网址
        return http.JsonResponse({'code': RETCODE.OK,
                                  'errmsg': 'OK',
                                  'alipay_url': alipay_url})

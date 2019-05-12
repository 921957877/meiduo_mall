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
from payment.models import Payment


class PaymentStatusView(View):
    """支付宝第二个接口:保存订单支付结果"""

    def get(self, request):
        # 获取QueryDict对象
        query_dict = request.GET
        data = query_dict.dict()
        # 剔除字典中的sign
        signature = data.pop('sign')
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
        # 校验这个重定向是否是支付宝重定向过来的
        success = alipay.verify(data, signature)
        # 如果校验成功
        if success:
            # 保存订单号和流水号到数据库
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')
            Payment.objects.create(order_id=order_id, trade_id=trade_id)
            # 将订单状态由待支付修改为待评价
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
            # 将流水号返回
            context = {
                'trade_id': trade_id
            }
            return render(request, 'pay_success.html', context)
        else:
            # 如果校验失败,返回报错信息
            return http.HttpResponseForbidden('非法请求')


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

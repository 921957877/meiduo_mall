import json
from decimal import Decimal

from django import http
from django.db import transaction
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredMixin, LoginRequiredJsonMixin
from orders.models import OrderInfo, OrderGoods
from users.models import Address
import logging

logger = logging.getLogger('django')


class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功"""
    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')
        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request, 'order_success.html', context)


class OrderCommitView(LoginRequiredJsonMixin, View):
    """提交订单"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseForbidden('参数address_id有误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method有误')
        # 生成订单编号:年月日时分秒+用户编号
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d' % request.user.id
        # 开启事务
        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()
            try:
                # 保存订单信息
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=request.user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0.00),
                    freight=Decimal(10.00),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM[
                        'UNSEND']
                )
                # 从redis中读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('carts')
                item_dict = redis_conn.hgetall('carts_%s' % request.user.id)
                cart_selected = redis_conn.smembers('selected_%s' % request.user.id)
                carts = {}
                for sku_id in cart_selected:
                    carts[int(sku_id)] = int(item_dict[sku_id])
                # 获取选中的商品id
                sku_ids = carts.keys()
                # 遍历购物车中被勾选的商品信息
                for sku_id in sku_ids:
                    # 增加死循环
                    while True:
                        # 获取单个商品
                        sku = SKU.objects.get(id=sku_id)
                        # 保存原始库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales
                        # 判断商品购买量是否大于库存
                        sku_count = carts[sku.id]
                        if sku.stock < sku_count:
                            # 出错就回滚
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': RETCODE.STOCKERR,
                                                      'errmsg': '库存不足'})
                        # # sku库存减少,销量增加
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()
                        # 乐观锁更新库存和销量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)
                        # 如果为0,说明库存更改了,重新下单,直到下单成功或库存不足为止
                        if result == 0:
                            continue
                        # spu销量增加
                        sku.goods.sales += sku_count
                        sku.goods.save()
                        # 保存订单商品信息
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price
                        )
                        # 保存商品订单中总价和总数量
                        order.total_count += sku_count
                        order.total_amount += sku_count * sku.price
                        # 下单成功跳出循环
                        break
                # 添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                logger.error(e)
                # 出错就回滚
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR,
                                          'errmsg': '保存失败'})
            # 提交订单成功,提交事务
            transaction.savepoint_commit(save_id)
        # 清除购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % request.user.id, *cart_selected)
        pl.srem('selected_%s' % request.user.id, *cart_selected)
        pl.execute()
        # 响应提交订单结果
        return http.JsonResponse({'code': RETCODE.OK,
                                  'errmsg': 'OK',
                                  'order_id': order.order_id})


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        # 获取用户地址
        try:
            addresses = Address.objects.filter(user=request.user, is_deleted=False)
        except Address.DoesNotExist:
            # 如果地址为空,渲染模板时会判断并跳转到地址编辑页面
            addresses = None
        # 创建redis连接对象
        redis_conn = get_redis_connection('carts')
        # 从hash表和set表中获取数据
        item_dict = redis_conn.hgetall('carts_%s' % request.user.id)
        cart_selected = redis_conn.smembers('selected_%s' % request.user.id)
        # 拼接字典,key:勾选上的商品id,value:该商品的数量
        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(item_dict.get(sku_id))
        # 准备初始值
        total_count = 0
        total_amount = Decimal(0.00)
        # 获取sku_ids
        sku_ids = cart.keys()
        # 获取要购买的商品列表
        skus = SKU.objects.filter(id__in=sku_ids)
        # 遍历商品列表,拼接商品信息
        for sku in skus:
            sku.count = cart.get(sku.id)
            sku.amount = sku.count * sku.price
            # 计算总数量和总金额
            total_count += sku.count
            total_amount += sku.amount
        # 补充运费
        freight = Decimal(10.00)
        # 拼接返回数据
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        # 渲染界面
        return render(request, 'place_order.html', context)
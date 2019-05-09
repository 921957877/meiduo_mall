from decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.views import LoginRequiredMixin
from users.models import Address


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

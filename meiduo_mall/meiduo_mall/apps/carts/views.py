import base64
import json
import pickle

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE


class CartsView(View):
    """购物车管理"""

    def put(self, request):
        """修改购物车"""
        # 接收json格式的参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 校验参数
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id有误')
        # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')
        # 判断selected是否为bool值
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')
        # 判断用户是否登陆
        if request.user.is_authenticated:
            # 用户已登陆,修改redis
            # 连接redis, 获取连接对象
            redis_conn = get_redis_connection('carts')
            # 创建管道
            pl = redis_conn.pipeline()
            # 往hash表中修改数据
            pl.hset('carts_%s' % request.user.id, sku_id, count)
            # 判断商品是否选中
            if selected:
                # 选中往set表中增加该商品的id
                pl.sadd('selected_%s' % request.user.id, sku_id)
            else:
                # 未选中往set表中删除该商品的id
                pl.srem('selected_%s' % request.user.id, sku_id)
            # 执行管道
            pl.execute()
            # 拼接返回数据
            cart_sku = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image_url,
                'count': count,
                'selected': selected,
                'amount': sku.price * count
            }
            # 返回json数据
            return http.JsonResponse({
                'code': RETCODE.OK,
                'errmsg': '修改购物车成功',
                'cart_sku': cart_sku
            })
        else:
            # 用户未登录,修改cookie
            # 获取cookie
            cookie_cart = request.COOKIES.get('carts')
            # 判断cookie值是否存在
            if cookie_cart:
                # 如果存在,解密成字典
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                # 如果不存在,定义一个空字典
                cart_dict = {}
            # 修改字典
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 加密字典
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 拼接返回数据
            cart_sku = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image_url,
                'count': count,
                'selected': selected,
                'amount': sku.price * count
            }
            # 创建响应对象
            response = http.JsonResponse({
                'code': RETCODE.OK,
                'errmsg': '修改购物车成功',
                'cart_sku': cart_sku
            })
            # 写入cookie
            response.set_cookie('carts', cart_data)
            # 返回响应
            return response

    def get(self, request):
        """展示购物车"""
        if request.user.is_authenticated:
            # 用户已登陆,查询redis
            # 连接redis,获取连接对象
            redis_conn = get_redis_connection('carts')
            # 从hash表中获取数据
            item_dict = redis_conn.hgetall('carts_%s' % request.user.id)
            # 从set表中获取数据
            cart_selected = redis_conn.smembers('selected_%s' % request.user.id)
            # 为了方便统一查询,将redis中的数据构造成跟cookie中的格式一样
            cart_dict = {}
            for sku_id, count in item_dict.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            # 用户未登录,查询cookie
            cookie_cart = request.COOKIES.get('carts')
            # 如果cookie中有购物车的数据
            if cookie_cart:
                # 将cookie解密成字典
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                # 如没有,定义一个空字典
                cart_dict = {}
        # 获取所有的商品id
        sku_ids = cart_dict.keys()
        # 通过所有的商品id获得所有的商品
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        # 遍历获得单个商品
        for sku in skus:
            # 拼接要响应的数据,一个商品一个字典,放入列表中
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': str(sku.price),
                'default_image_url': sku.default_image_url,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),
                'amount': str(cart_dict.get(sku.id).get('count') * sku.price)
            })
        # 拼接字典数据
        context = {
            'cart_skus': cart_skus
        }
        # 渲染页面
        return render(request, 'cart.html', context)

    def post(self, request):
        """添加购物车"""
        # 接收json格式的参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 校验参数
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id有误')
        # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')
        # 判断selected是否为bool值
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')
        # 判断用户是否登陆
        if request.user.is_authenticated:
            # 用户已登陆,操作redis
            # 连接redis,获取连接对象
            redis_conn = get_redis_connection('carts')
            # 创建管道
            pl = redis_conn.pipeline()
            # 往hash表中累加数据
            pl.hincrby('carts_%s' % request.user.id, sku_id, count)
            # 往set表中增加选中的商品id
            if selected:
                pl.sadd('selected_%s' % request.user.id, sku_id)
            # 执行管道
            pl.execute()
            # 返回响应结果
            return http.JsonResponse({
                'code': RETCODE.OK,
                'errmsg': '添加购物车成功'
            })
        else:
            # 用户未登录,操作cookie
            # 获取以前存储的cookie值
            cookie_cart = request.COOKIES.get('carts')
            # 如果cookie中有购物车的数据
            if cookie_cart:
                # 将cookie解密得到字典
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                # 如果cookie中没有购物车的数据,则定义一个空字典
                cart_dict = {}
            # 判断要加入购物车的商品是否已经在购物车中
            if sku_id in cart_dict:
                # 如有相同的商品,累加求和
                count += cart_dict.get(sku_id).get('count')
            # 更新字典
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 将字典加密
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 创建响应对象
            response = http.JsonResponse({
                'code': RETCODE.OK,
                'errmsg': '添加购物车成功'
            })
            # 写入cookie
            response.set_cookie('carts', cart_data)
            # 返回响应
            return response

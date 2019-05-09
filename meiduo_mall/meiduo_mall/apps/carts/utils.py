import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response):
    """登录后合并cookie购物车数据到redis购物车数据
    合并方案：
    1.Redis数据库中的购物车数据保留
    2.如果cookie中的购物车数据在Redis数据库中已存在
    将cookie购物车数据覆盖Redis购物车数据
    3.如果cookie中的购物车数据在Redis数据库中不存在,
    将cookie购物车数据新增到Redis
    4.最终购物车的勾选状态以cookie购物车勾选状态为准"""
    # 获取cookie
    cookie_cart = request.COOKIES.get('carts')
    # 如果cookie不存在,直接返回响应结果
    if not cookie_cart:
        return response
    # 如果cookie存在,解密
    cart_dict = pickle.loads(base64.b64decode(cookie_cart))
    # 组织数据
    new_dict = {}
    new_add = []
    new_remove = []
    for sku_id, item in cart_dict.items():
        new_dict[sku_id] = item['count']
        if item['selected']:
            new_add.append(sku_id)
        else:
            new_remove.append(sku_id)
    # 创建redis连接对象
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    # 将组织的数据写入redis中的hash表和set表
    pl.hmset('carts_%s' % request.user.id, new_dict)
    # 将勾选状态同步到redis数据库
    # 如果new_add中有数据,将set表中的这些商品id增加
    if new_add:
        pl.sadd('selected_%s' % request.user.id, *new_add)
    # 如果new_remove中有数据,将set表中的这些商品id删除
    if new_remove:
        pl.srem('selected_%s' % request.user.id, *new_remove)
    pl.execute()
    # 清除cookie
    response.delete_cookie('carts')
    # 返回响应结果
    return response

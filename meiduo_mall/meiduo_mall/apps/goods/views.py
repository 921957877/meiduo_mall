import datetime

from django import http
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views import View
from goods.models import GoodsCategory, SKU, GoodsVisitCount
from goods.utils import get_categories, get_breadcrumb, get_goods_and_spec
from meiduo_mall.utils.response_code import RETCODE
import logging

logger = logging.getLogger('django')


class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self, request, category_id):
        """记录分类商品访问量"""
        # 根据传入的category_id获取对应类别的商品
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('缺少必传参数')
        # 获取今天的日期
        # 获取时间对象
        t = timezone.localtime()
        # 根据时间对象拼接日期的字符串形式
        today_str = '%d-%02d-%02d' % (t.year, t.month, t.day)
        # 将字符串转为日期格式
        today_date = datetime.datetime.strptime(today_str, '%Y-%m-%d')
        try:
            # 根据传入的今天的日期获取该商品今天的访问量
            counts_data = category.goodsvisitcount_set.get(date=today_date)
        except GoodsVisitCount.DoesNotExist:
            # 如果该类别的商品今天没有过访问记录,就新建一个访问记录
            counts_data = GoodsVisitCount()
        try:
            # 更新模型类对象里面的属性category和count
            counts_data.category = category
            counts_data.count += 1
            counts_data.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('服务器异常')
        # 返回json
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        # 获取商品频道分类
        categories = get_categories()
        # 调用封装的函数,根据sku_id获取对应的商品数据字典
        data = get_goods_and_spec(sku_id, request)
        # 拼接字典数据
        context = {
            'categories': categories,
            'sku': data.get('sku'),
            'goods': data.get('goods'),
            'specs': data.get('goods_specs'),
        }
        # 渲染页面
        return render(request, 'detail.html', context)


class HotGoodsView(View):
    """商品热销排行"""

    def get(self, request, category_id):
        """提供商品热销排行的Json数据"""
        # 获取当前分类并且上架的商品并倒序处理取前两个
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]
        # 拼接数据
        hot_skus = []
        for sku in skus:
            hot_skus.append(
                {
                    'id': sku.id,
                    'default_image_url': sku.default_image_url,
                    'name': sku.name,
                    'price': sku.price
                }
            )
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


class ListView(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        """提供商品列表页"""
        # 1.校验category_id
        try:
            # 获取三级菜单分类信息
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseNotFound('GoodsCategory不存在')
        # 2.获取商品频道分类
        categories = get_categories()
        # 3.获取面包屑导航
        breadcrumb = get_breadcrumb(category)
        # 4.获取前端用查询字符串方式传来的sort参数,如没有,则取默认值default
        sort = request.GET.get('sort', 'default')
        # 5.判断排序方式,确认排序依据
        if sort == 'price':
            # 按照价格由低到高排序
            sortkind = 'price'
        elif sort == 'hot':
            # 按照销量由高到低排序
            sortkind = '-sales'
        else:
            sort = 'default'
            # 默认排序,按照创建时间排序
            sortkind = 'create_time'
        # 6.获取当前分类并且上架的商品,并对商品按照上面的排序方式进行排序
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(sortkind)
        # 7.创建一个分页器对象,第一个参数为要展示的数据列表,第二个参数为每页的显示数量
        paginator = Paginator(skus, 5)
        # 8.获取对应页面的商品
        try:
            page_skus = paginator.page(page_num)
        # 如果只有四页数据,但是前端索求第五页的数据,则报错
        except EmptyPage:
            return http.HttpResponseNotFound('Empty Page')
        # 9.获取总页数
        total_page = paginator.num_pages
        # 10.拼接数据字典
        context = {
            'categories': categories,  # 频道分类
            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 对应页面的商品
            'total_page': total_page,  # 总页数
            'page_num': page_num  # 当前页码
        }
        # 11.渲染页面
        return render(request, 'list.html', context)

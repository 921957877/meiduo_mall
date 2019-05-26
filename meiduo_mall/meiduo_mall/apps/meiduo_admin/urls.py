from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from meiduo_admin.views.data_views import UserTotalCountView, UserDayCountView, UserDayActiveCountView, \
    UserDayOrderCountView, UserMonthCountView, GoodsDayVisitCountView
from meiduo_admin.views.sku_views import SKUView, GoodsCategoryView, SPUView, SPUSpecView
from meiduo_admin.views.user_views import UserView

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),  # JWT认证
    url(r'^statistical/total_count/$', UserTotalCountView.as_view()),  # 用户总数统计
    url(r'^statistical/day_increment/$', UserDayCountView.as_view()),  # 日增用户统计
    url(r'^statistical/day_active/$', UserDayActiveCountView.as_view()),  # 日活跃用户统计
    url(r'^statistical/day_orders/$', UserDayOrderCountView.as_view()),  # 日下单用户统计
    url(r'^statistical/month_increment/$', UserMonthCountView.as_view()),  # 月增用户统计
    url(r'^statistical/goods_day_views/$', GoodsDayVisitCountView.as_view()),  # 日分类商品访问量统计
    url(r'^users/$', UserView.as_view()),  # 获取和增加用户
    url(r'^skus/$', SKUView.as_view({'get': 'list', 'post': 'create'})),  # 获取,创建sku商品数据
    url(r'^skus/(?P<pk>\d+)/$', SKUView.as_view({'delete': 'destroy', 'get': 'retrieve', 'put': 'update'})),
    # 删除,获得,更新一个sku商品数据
    url(r'^skus/categories/$', GoodsCategoryView.as_view()),  # 获取三级分类信息
    url(r'^goods/simple/$', SPUView.as_view()),  # 获取SPU表名称数据
    url(r'^goods/(?P<pk>\d+)/specs/$', SPUSpecView.as_view()),  # 获取SPU商品规格信息
]

from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from meiduo_admin.views.data_view import UserTotalCountView, UserDayCountView, UserDayActiveCountView, \
    UserDayOrderCountView, UserMonthCountView, GoodsDayVisitCountView

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),  # JWT认证
    url(r'^statistical/total_count/$', UserTotalCountView.as_view()),  # 用户总数统计
    url(r'^statistical/day_increment/$', UserDayCountView.as_view()),  # 日增用户统计
    url(r'^statistical/day_active/$', UserDayActiveCountView.as_view()),  # 日活跃用户统计
    url(r'^statistical/day_orders/$', UserDayOrderCountView.as_view()),  # 日下单用户统计
    url(r'^statistical/month_increment/$', UserMonthCountView.as_view()),  # 月增用户统计
    url(r'^statistical/goods_day_views/$', GoodsDayVisitCountView.as_view()),  # 日分类商品访问量统计
]

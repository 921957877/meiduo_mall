from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^areas/$', views.ProvinceAreasView.as_view()),  # 获取省份数据
    url(r'^areas/(?P<pk>[1-9]\d+)/$', views.SubAreasView.as_view()),  # 获取市,区数据
]

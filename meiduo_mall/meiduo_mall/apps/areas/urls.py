from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^areas/$', views.ProvinceAreasView.as_view()),  # 获取省份数据
]

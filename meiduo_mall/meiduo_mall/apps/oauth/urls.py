from django.conf.urls import url
from . import views

urlpatterns = [
    # 获取QQ登陆页面网址
    url(r'^qq/authorization/$', views.QQURLView.as_view()),
    # QQ用户扫码登陆的回调处理
    url(r'^oauth_callback/$', views.QQUserView.as_view()),
]

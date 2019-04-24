from django.conf.urls import url
from . import views

urlpatterns = [
    # 获取QQ登陆页面网址
    url(r'^qq/authorization/$', views.QQUrlView.as_view()),
]

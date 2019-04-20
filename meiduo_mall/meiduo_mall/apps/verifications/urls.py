from django.conf.urls import url

from . import views

urlpatterns = [
    # image_codes/(?P<uuid>[\w-]+)/
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),  # 图形验证码
]

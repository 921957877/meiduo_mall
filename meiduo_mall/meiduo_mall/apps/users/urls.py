from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),  # 注册
    # /usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),  # 判断用户名是否重复
    # /mobiles/(?P<mobile>1[3-9]\d{9})/count/
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),  # 判断手机号是否重复
    url(r'^login/$', views.LoginView.as_view(), name='login'),  # 登陆
    url(r'^logout/$', views.LoginoutView.as_view(), name='logout'),  # 退出登陆
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),  # 用户中心个人信息
    url(r'^emails/$', views.EmailView.as_view()),  # 添加邮箱
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),  # 验证邮箱
]

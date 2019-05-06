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
    url(r'^addresses/$', views.AddressView.as_view(), name='address'),  # 收货地址
    url(r'^addresses/create/$', views.CreateAddressView.as_view()),  # 新增收货地址
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),  # 修改和删除收货地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),  # 设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),  # 修改地址标题
    url(r'^password/$', views.ChangePasswordView.as_view(), name='pass'),  # 修改密码
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view()),  # 用户浏览记录
]

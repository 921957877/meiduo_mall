from django.conf.urls import url

from carts import views

urlpatterns = [
    # 购物车增删改查
    url(r'^carts/$', views.CartsView.as_view(), name='info')
]

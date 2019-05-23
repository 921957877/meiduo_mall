from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from meiduo_admin.views import JWTLogin
from . import views

urlpatterns = [
    # url(r'^authorizations/$', JWTLogin.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
]

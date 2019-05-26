from rest_framework.generics import ListCreateAPIView

from meiduo_admin.pages import MyPage
from meiduo_admin.serializers.user_serializers import UserSerializer
from users.models import User


class UserView(ListCreateAPIView):
    """获取和增加用户"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = MyPage

    # 重写get_queryset方法,根据前端是否传递keyword值返回不同查询结果
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(username__contains=keyword)
        return self.queryset.all()

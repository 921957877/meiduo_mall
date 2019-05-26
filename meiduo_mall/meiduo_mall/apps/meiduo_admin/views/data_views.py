from datetime import date, timedelta

from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import GoodsVisitCount
from users.models import User


class UserTotalCountView(APIView):
    """用户总数统计"""
    # 指定管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当日日期
        now_date = date.today()
        # 获取所有用户总数
        count = User.objects.all().count()
        return Response({
            'count': count,
            'date': now_date
        })


class UserDayCountView(APIView):
    """日增用户统计"""
    # 指定管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当日日期
        now_date = date.today()
        # 获取当日注册用户数量
        count = User.objects.filter(date_joined__gte=now_date).count()
        return Response({
            "count": count,
            "date": now_date
        })


class UserDayActiveCountView(APIView):
    """日活跃用户统计"""
    # 指定管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当日日期
        now_date = date.today()
        # 获取当日登录用户数量
        count = User.objects.filter(last_login__gte=now_date).count()
        return Response({
            "count": count,
            "date": now_date
        })


class UserDayOrderCountView(APIView):
    """日下单用户统计"""
    # 指定管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当日日期
        now_date = date.today()
        # 获取当日下单用户数量
        count = User.objects.filter(orders__create_time__gte=now_date).count()
        return Response({
            'count': count,
            'date': now_date
        })


class UserMonthCountView(APIView):
    """月增用户统计"""
    # 指定管理员权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当日日期
        now_date = date.today()
        # 获取一个月前的日期
        start_date = now_date - timedelta(days=29)
        user_list = []
        # 遍历这一个月的每一天
        for i in range(30):
            # 获取每天注册的用户数量
            count = User.objects.filter(date_joined__gte=start_date + timedelta(days=i),
                                        date_joined__lt=start_date + timedelta(days=i + 1)).count()
            # 拼接字典
            data = {
                'count': count,
                'date': start_date + timedelta(days=i)
            }
            # 添加到列表
            user_list.append(data)
        return Response(user_list)


class GoodsVisitCountSerializer(serializers.ModelSerializer):
    # 指定返回分类名称
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ['category', 'count']


class GoodsDayVisitCountView(ListAPIView):
    """日分类商品访问量统计"""
    # 指定管理员权限
    permission_classes = [IsAdminUser]
    # 获取当日日期
    now_date = date.today()
    queryset = GoodsVisitCount.objects.filter(date=now_date)
    serializer_class = GoodsVisitCountSerializer


from django.shortcuts import render

# Create your views here.
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

from users.models import User


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # 接收参数并校验
        username = attrs['username']
        password = attrs['password']
        # 获取用户对象
        user = User.objects.get(username=username)
        # 如果用户存在并且校验密码正确
        if user and user.check_password(password):
            # 生成jwt_token
            payload = jwt_payload_handler(user)
            jwt_token = jwt_encode_handler(payload)
            return {
                'username': user.username,
                'user_id': user.id,
                'token': jwt_token
            }
        raise serializers.ValidationError('用户验证失败')


class JWTLogin(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

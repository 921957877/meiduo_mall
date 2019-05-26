from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'password']
        # 给password添加额外的约束条件,只参与保存,不返回给前端
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # 重写create方法,保存用户数据并对密码进行加密
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

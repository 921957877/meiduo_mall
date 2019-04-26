from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer


# Create your models here.
# 我们重写用户模型类,继承自AbstractUser
class User(AbstractUser):
    """自定义用户模型类"""
    # 在用户模型类中增加mobile字段
    mobile = models.CharField(max_length=11, verbose_name='手机号', unique=True)
    # 增加email_active字段,用于记录邮箱是否验证过,默认为False,未验证
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    # 对当前表进行相关设置
    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    # 在str魔法方法中返回用户名称
    def __str__(self):
        return self.username

    """这个函数的主要作用是根据每个人的不同, 生成不同的邮箱验证链接,由于每个用户对于模型类来说是不同的,
    所以生成的验证链接也是不同的,因此把函数定义在模型类内"""
    def generate_verify_email(self):
        """
        生成邮箱验证链接
        :return: 验证链接
        """
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=60 * 60 * 24)
        # 拼接参数
        data = {
            'user_id': self.id,
            'email': self.email
        }
        # 生成token值并解码
        token = serializer.dumps(data).decode()
        verify_email = settings.EMAIL_VERIFY_URL + '?token=' + token
        # 返回
        return verify_email


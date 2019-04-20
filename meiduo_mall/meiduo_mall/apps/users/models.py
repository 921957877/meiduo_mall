from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
# 我们重写用户模型类,继承自AbstractUser
class User(AbstractUser):
    """自定义用户模型类"""
    # 在用户模型类中增加mobile字段
    mobile = models.CharField(max_length=11, verbose_name='手机号', unique=True)

    # 对当前表进行相关设置
    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    # 在str魔法方法中返回用户名称
    def __str__(self):
        return self.username

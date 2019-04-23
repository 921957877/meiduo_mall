from django.db import models

# Create your models here.
from meiduo_mall.utils.BaseModel import BaseModel


# 定义qq登陆的模型类
class OAuthQQUser(BaseModel):
    """QQ登陆用户数据"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    # db_index=True可使openid也成为该表的主键
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登陆用户数据'
        verbose_name_plural = verbose_name

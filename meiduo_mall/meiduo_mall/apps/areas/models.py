from django.db import models


# Create your models here.
class Area(models.Model):
    """行政区划"""
    name = models.CharField(max_length=20, verbose_name='名称')
    # 自关联字段 parent
    # 第一个参数是 self : parent关联自己
    # on_delete=models.SET_NULL:  如果省删掉了,省内其他的信息为 NULL
    # related_name='subs': 设置之后,我们就这样调用获取市: area.area_set.all() ==> area.subs.all()
    # null=True值可为空,blank=True表单可为空,即不填
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,
                               blank=True, related_name='subs', verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

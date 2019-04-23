from django.contrib.auth.decorators import login_required


# 添加扩展类:
# 因为这类扩展其实就是Mixin扩展类的扩展方式
# 所以我们起名时,最好也加上Mixin
class LoginRequiredMixin(object):
    """验证用户是否登陆的扩展类"""

    # 重写as_view函数
    @classmethod
    def as_view(cls, **initkwargs):
        # 调用父类的as_view函数
        view = super().as_view()
        # 添加装饰行为 login_required 这个装饰器用来判断用户是否登录
        # 内部封装了 is_authenticate,如果通过登录验证则进入到视图内部,执行视图逻辑.
        # 如果未通过登录验证则被重定向到 LOGIN_URL 配置项指定的地址
        return login_required(view)

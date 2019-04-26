from django import http
from django.contrib.auth.decorators import login_required
from django.utils.decorators import wraps

# 添加扩展类:
# 因为这类扩展其实就是Mixin扩展类的扩展方式
# 所以我们起名时,最好也加上Mixin
from meiduo_mall.utils.response_code import RETCODE


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


def login_required_json(view_function):
    """
    判断用户是否登陆的装饰器,并返回json
    :param view_function: 被装饰的视图函数
    :return: json
    """
    # @wraps装饰器可返回view_function的名字和文档,否则返回的是内层函数的引用,即view指向了wrapper
    @wraps(view_function)
    def wrap(request, *args, **kwargs):
        # 如果用户未登陆,返回json数据
        if not request.user.is_authenticated():
            return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})
        # 如果用户登陆,进入到view_function中
        return view_function(request, *args, **kwargs)

    return wrap


class LoginRequiredJsonMixin(object):
    """验证用户是否登陆并返回json数据的扩展类"""
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required_json(view)

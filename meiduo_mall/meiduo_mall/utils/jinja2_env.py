from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from jinja2 import Environment


def jinja2_environment(**options):
    env = Environment(**options)
    env.globals.update({
        # 确保可以使用Django模板引擎中的{% url('') %} {% static('') %}这类的语句
        'static': staticfiles_storage.url,
        'url': reverse,
    })
    return env

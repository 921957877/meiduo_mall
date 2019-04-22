import os

from celery import Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")
# 创建celery对象
# 需要添加一个参数,是个字符串,内容随意添加
celery_app = Celery('meiduo')
# 给celery添加配置
# 里面的参数为我们创建的config配置文件
celery_app.config_from_object('celery_tasks.config')
# 让celery_app自动捕获目标地址下的任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])
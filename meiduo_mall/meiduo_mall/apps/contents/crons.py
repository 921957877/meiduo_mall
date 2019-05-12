import os

from django.conf import settings
from django.template import loader

from contents.models import ContentCategory
from goods.utils import get_categories


def generate_static_index_html():
    """生成静态的主页html文件"""
    # 查询商品频道和分类
    categories = get_categories()
    # 定义一个空的字典
    dict = {}
    # 查询出所有的广告类别
    content_categories = ContentCategory.objects.all()
    # 遍历所有的广告类别,然后放入定义的空字典中
    for cat in content_categories:
        # 获取类别所对应的展示数据,并对数据进行排序
        dict[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
    # 拼接参数
    context = {
        'categories': categories,
        'contents': dict
    }
    # 获取首页模板文件
    template = loader.get_template('index.html')
    # 渲染首页html字符串
    html_text = template.render(context)
    # 将首页html字符串写入到指定目录，命名'index.html'
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)

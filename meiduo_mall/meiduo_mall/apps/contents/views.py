from django.shortcuts import render
from django.views import View

# Create your views here.
from contents.models import ContentCategory
from goods.utils import get_categories


class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告页面"""
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
        # 返回界面,同时传入参数
        return render(request, 'index.html', context)

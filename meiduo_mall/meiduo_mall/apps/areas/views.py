from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from areas.models import Area
from meiduo_mall.utils.response_code import RETCODE


class ProvinceAreasView(View):
    """省级地区"""

    def get(self, request):
        """提供省级地区数据"""
        # 1.查询省级数据
        try:
            province_model_list = Area.objects.filter(parent__isnull=True)
            # 2.整理省级数据
            province_list = []
            for province_model in province_model_list:
                province_list.append({'id': province_model.id,
                                      'name': province_model.name})
        except Exception:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})
        else:
            # 3.响应省级数据 TODO 为什么这里不用写safe=false
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MyPage(PageNumberPagination):
    page_size = 5
    max_page_size = 10
    page_size_query_param = 'pagesize'

    # # 重写分页返回方法,按照指定的字段进行分页数据返回
    def get_paginated_response(self, data):
        # data:数据集分页后的子集
        return Response({
            'counts': self.page.paginator.count,  # 对象总数
            'lists': data,
            'page': self.page.number,  # 当前页数
            'pages': self.page.paginator.num_pages,  # 总页数
            'pagesize': self.page_size  # 后端指定的每页显示数量
        })
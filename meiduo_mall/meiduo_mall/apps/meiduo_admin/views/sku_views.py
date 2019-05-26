from rest_framework.generics import ListAPIView, DestroyAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from goods.models import SKU, GoodsCategory, Goods, GoodsSpecification
from meiduo_admin.pages import MyPage
from meiduo_admin.serializers.sku_serializers import SKUSerializer, GoodsCategorySerializer, SPUSerializer, \
    SPUSpecSerializer


# class SKUView(ListAPIView, DestroyAPIView, CreateAPIView, RetrieveAPIView):
class SKUView(ModelViewSet):
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    pagination_class = MyPage

    # 重写get_queryset方法,根据前端是否传递keyword值返回不同查询结果
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(name__contains=keyword)
        return self.queryset.all()


class GoodsCategoryView(ListAPIView):
    # parent_id大于37为三级分类信息
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)
    serializer_class = GoodsCategorySerializer


class SPUView(ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = SPUSerializer


class SPUSpecView(ListAPIView):
    serializer_class = SPUSpecSerializer

    # 已知SPU的id(主表),查询SPU的规格(从表)
    def get_queryset(self):
        goods_id = self.kwargs.get('pk')
        return GoodsSpecification.objects.filter(goods_id=goods_id)

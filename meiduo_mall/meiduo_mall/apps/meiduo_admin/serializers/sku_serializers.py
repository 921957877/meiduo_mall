from rest_framework import serializers

from goods.models import SKU, SKUSpecification, GoodsCategory, Goods, GoodsSpecification, SpecificationOption


class SKUSpecSerializer(serializers.ModelSerializer):
    """SKU规格表序列化器"""
    spec_id = serializers.IntegerField(read_only=True)
    option_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):
    """SKU表序列化器"""
    goods = serializers.StringRelatedField(read_only=True)
    goods_id = serializers.IntegerField()
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField()
    specs = SKUSpecSerializer(read_only=True, many=True)

    class Meta:
        model = SKU
        fields = '__all__'


class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品类别表序列化器"""

    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']


class SPUSerializer(serializers.ModelSerializer):
    """商品SPU表序列化器"""

    class Meta:
        model = Goods
        fields = ['id', 'name']


class SpecOptSerializer(serializers.ModelSerializer):
    """规格选项表序列化器"""
    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


class SPUSpecSerializer(serializers.ModelSerializer):
    """SPU规格表序列化器"""
    goods = serializers.StringRelatedField(read_only=True)
    goods_id = serializers.IntegerField(read_only=True)
    options = SpecOptSerializer(read_only=True, many=True)

    class Meta:
        model = GoodsSpecification
        fields = ['id', 'name', 'goods', 'goods_id', 'options']

import rest_framework.serializers

from webshops.models import Category, Product, Webshop, Order


class LightCategorySerializer(rest_framework.serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'parent'
        )


class CategoryDetailSerializer(rest_framework.serializers.ModelSerializer):

    def get_products(self, obj):
        if obj:
            return ProductSerializer(obj.get_products(), many=True).data

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'parent'
        )


class ProductIdOnlySerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = 'id',
        readonly = 'id',


class ProductSerializer(rest_framework.serializers.ModelSerializer):
    showing_price = rest_framework.serializers.ReadOnlyField()
    discount_price = rest_framework.serializers.ReadOnlyField()

    def get_available_qty_in_stock(self, obj):
        if obj and obj.is_child and getattr(obj, 'parent_qty_in_stock', None) is not None:
            return obj.parent_qty_in_stock
        return obj and obj.pcs_in_stock

    class Meta:
        model = Product
        fields = '__all__'


class ProductDetailSerializer(ProductSerializer):
    has_children = rest_framework.serializers.ReadOnlyField()
    has_options = rest_framework.serializers.ReadOnlyField()
    category = LightCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class WebshopSerializer(rest_framework.serializers.ModelSerializer):
    """
        Webshop serializer of the company one for the chat contacts list and others
    """

    class Meta:
        model = Webshop
        fields = ('id', 'name')


class OrderSerializer(rest_framework.serializers.ModelSerializer):
    """
        Order serializer for the order list
    """
    # url = rest_framework.serializers.ReadOnlyField(source="get_absolute_url")

    class Meta:
        model = Order
        fields = ('id', 'paid', 'shipped',)

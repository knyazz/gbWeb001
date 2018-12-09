import rest_framework.decorators
import rest_framework.mixins
import rest_framework.viewsets

from django_filters.rest_framework import DjangoFilterBackend

from django.db import models

from webshops.models import Category, Product, Order
from webshops.pagination import ProductPagination
from webshops import serializers


class CategoryViewSet(rest_framework.viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LightCategorySerializer
    model = Category
    queryset = model.objects.select_related('parent').all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('webshop', 'parent', 'active')

    def get_serializer_class(self):
        if self.action in ('retrieve',):
            return serializers.CategoryDetailSerializer
        return self.serializer_class


class ProductIdOnlyViewSet(rest_framework.viewsets.ModelViewSet):
    serializer_class = serializers.ProductIdOnlySerializer
    model = Product
    queryset = model.objects.select_related(
        'webshop', 'category', 'category__parent',
        'webshop', 'webshop'
    ).all()
    filter_backends = (DjangoFilterBackend,)
    fields = ('active', 'parent', 'webshop', 'structure', 'category')


class ProductViewSet(ProductIdOnlyViewSet):
    serializer_class = serializers.ProductSerializer
    queryset = Product.objects.select_related(
        'webshop', 'category', 'category__parent',
        'webshop', 'webshop',
        'parent'
    ).annotate(
        parent_qty_in_stock=models.F('parent__pcs_in_stock'),
    ).all()
    pagination_class = ProductPagination

    def get_serializer_class(self):
        if self.action in ('retrieve', ):
            return serializers.ProductDetailSerializer
        elif self.action in ('create', 'partial_update', 'update'):
            return serializers.ProductDetailSerializer
        return self.serializer_class


class OrderViewSet(rest_framework.viewsets.ModelViewSet):
    model = Order
    serializer_class = serializers.OrderSerializer
    queryset = model.objects.all()
    #filter_backends = (DjangoFilterBackend,)
    #filter_fields = ('paid', 'shipped', 'customer', 'company')
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('customer',)

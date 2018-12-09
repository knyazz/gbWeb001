# coding: utf-8
from __future__ import unicode_literals
import random
import string
import decimal

from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from simpleAPI.testtools import BaseTest

import webshops.factories
import webshops.serializers

__author__ = 'smirnov.ev'


class CategoryDetailSerializerTestCase(BaseTest):

    def setUp(self):
        self.obj_model = webshops.factories.CategoryFactory._meta.model
        self.name = ''.join(random.choice(string.letters) for _ in range(100))
        self.webshop = webshops.factories.WebshopFactory.create()
        self.object = webshops.factories.CategoryFactory(
            webshop=self.webshop, name=self.name)
        self.serializer_class = webshops.serializers.CategoryDetailSerializer

    def tearDown(self):
        self.object.delete()
        self.webshop.delete()
        self.assertEqual(self.obj_model.objects.count(), 0)

    def test_init(self):
        """ Testing webshops.serializers.CategoryDetailSerializer serializer init """
        self.assertIsNotNone(self.serializer_class())
        self.assertIsNotNone(self.serializer_class(instance=self.object))

    def test_blank_data(self):
        """ Testing webshops.serializers.CategoryDetailSerializer serializer blank data """
        serializer = self.serializer_class(data={})
        self.assertFalse(serializer.is_valid())
        for field in ('name',):
            self.assertEqual(
                serializer.errors[field], [_('This field is required.')])

    def test_get_products_method(self):
        """ Testing webshops.serializers.CategoryDetailSerializer serializer get_products method """
        serializer = self.serializer_class()
        self.assertEqual(serializer.get_products(self.object), [])
        self.assertIsNone(serializer.get_products(None))


class ProductDetailSerializerTestCase(BaseTest):

    def setUp(self):
        self.obj_model = webshops.factories.ProductFactory._meta.model
        self.name = ''.join(random.choice(string.letters) for _ in range(100))
        self.webshop = webshops.factories.WebshopFactory.create()
        self.category = webshops.factories.CategoryFactory(webshop=self.webshop)
        self.price = decimal.Decimal(99.99)
        self.object = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=self.price)
        self.serializer_class = webshops.serializers.ProductDetailSerializer

    def tearDown(self):
        self.object.delete()
        self.category.delete()
        self.webshop.delete()
        self.assertEqual(self.obj_model.objects.count(), 0)

    def test_init(self):
        """ Testing webshops.serializers.ProductDetailSerializer serializer init """
        self.assertIsNotNone(self.serializer_class())
        self.assertIsNotNone(self.serializer_class(instance=self.object))

    def test_blank_data(self):
        """ Testing webshops.serializers.ProductDetailSerializer serializer blank data """
        serializer = self.serializer_class(data={})
        self.assertFalse(serializer.is_valid())
        for field in ('name', 'webshop'):
            self.assertEqual(
                serializer.errors[field], [_('This field is required.')])


class ProductSerializerTestCase(BaseTest):

    def setUp(self):
        self.obj_model = webshops.factories.ProductFactory._meta.model
        self.name = ''.join(random.choice(string.letters) for _ in range(100))
        self.art_nr = ''.join(random.choice(string.letters) for _ in range(100))
        self.webshop = webshops.factories.WebshopFactory.create()
        self.category = webshops.factories.CategoryFactory(webshop=self.webshop)
        self.price = decimal.Decimal(99.99)
        self.pcs_in_stock = 10
        self.object = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=self.price,
            pcs_in_stock=self.pcs_in_stock
        )
        self.serializer_class = webshops.serializers.ProductSerializer

    def tearDown(self):
        self.object.delete()
        self.category.delete()
        self.webshop.delete()
        self.assertEqual(self.obj_model.objects.count(), 0)

    def test_init(self):
        """ Testing webshops.serializers.ProductSerializer serializer init """
        self.assertIsNotNone(self.serializer_class())
        self.assertIsNotNone(self.serializer_class(instance=self.object))

    def test_blank_data(self):
        """ Testing webshops.serializers.ProductSerializer serializer blank data """
        serializer = self.serializer_class(data={})
        self.assertFalse(serializer.is_valid())
        for field in ('name', 'webshop'):
            self.assertEqual(
                serializer.errors[field], [_('This field is required.')])

    @transaction.atomic()
    def test_get_available_qty_in_stock_method(self):
        """ Testing webshops.serializers.ProductSerializer serializer get_available_qty_in_stock method """
        serializer = self.serializer_class()
        self.assertEqual(serializer.get_available_qty_in_stock(self.object), 10)
        self.assertIsNone(serializer.get_available_qty_in_stock(None))

        _parent = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=self.price, pcs_in_stock=3,
            structure=self.obj_model.PARENT
        )

        self.object.parent = _parent
        self.object.structure = self.obj_model.CHILD
        self.object.save()
        self.object.parent_qty_in_stock = self.object.parent.pcs_in_stock

        self.assertEqual(serializer.get_available_qty_in_stock(self.object), 3)
        self.assertIsNone(serializer.get_available_qty_in_stock(None))

        self.object.parent = None
        self.object.structure = self.obj_model.STANDALONE
        self.object.save()
        _parent.delete()

# coding: utf-8
from __future__ import unicode_literals
import json
import random
import string
import decimal

from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import Client

from rest_framework.test import APIClient

from simpleAPI.testtools import BaseTest

import webshops.factories
import webshops.serializers

__author__ = 'smirnov.ev'


class APIBaseTestCase(BaseTest):
    """ Base class for API with creating a default user with password 12345 """

    def setUp(self):
        self.client = Client()
        self.apiclient = APIClient()
        self.user = webshops.factories.UserFactory.create(is_active=True)
        self.user_password = '12345'
        with transaction.atomic():
            self.user.set_password(self.user_password)
            self.user.save()

    def tearDown(self):
        self.user.delete()


class CategoryAPITestCase(APIBaseTestCase):

    def setUp(self):
        super(CategoryAPITestCase, self).setUp()
        self.obj_model = webshops.factories.CategoryFactory._meta.model
        self.webshop = webshops.factories.WebshopFactory.create()
        self.name = ''.join(random.choice(string.letters) for _ in range(100))
        self.object = webshops.factories.CategoryFactory.create(
            webshop=self.webshop,
            name=self.name,
        )
        self.serializer_class = webshops.serializers.LightCategorySerializer

    @transaction.atomic()
    def test_api_list_view(self):
        ''' Testing webshops.apis.CategoryViewSet list view'''
        url = reverse('webshops:api_category-list')
        res = self.apiclient.get(url)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(len(data), 1)
        _obj = data[0]
        self.assertEqual(_obj['id'], self.object.id)
        self.assertEqual(_obj['name'], self.name)
        self.assertIsNone(_obj['parent'])

        # authorization
        res = self.apiclient.login(password='12345', username=self.user)
        self.assertTrue(res)

        res = self.apiclient.get(url)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(len(data), 1)
        _obj = data[0]
        self.assertEqual(_obj['id'], self.object.id)
        self.assertEqual(_obj['name'], self.name)
        self.assertIsNone(_obj['parent'])

        res = self.apiclient.logout()

    @transaction.atomic()
    def test_api_detail_view(self):
        ''' Testing webshops.apis.CategoryViewSet detail view'''
        url = reverse('webshops:api_category-detail', kwargs=dict(pk=self.object.pk))
        res = self.apiclient.get(url)
        self.assertEqual(res.status_code, 200)

    def tearDown(self):
        super(CategoryAPITestCase, self).tearDown()
        self.webshop.delete()
        self.object.delete()


class ProductAPITestCase(APIBaseTestCase):

    def setUp(self):
        super(ProductAPITestCase, self).setUp()
        self.obj_model = webshops.factories.ProductFactory._meta.model
        self.webshop = webshops.factories.WebshopFactory.create()
        self.category = webshops.factories.CategoryFactory.create(webshop=self.webshop)
        self.name = ''.join(random.choice(string.letters) for _ in range(100))
        self.price = decimal.Decimal(random.randrange(10000)) / 100
        self.object = webshops.factories.ProductFactory.create(
            webshop=self.webshop,
            category=self.category,
            name=self.name,
            price=self.price,
        )
        self.serializer_class = webshops.serializers.ProductSerializer

    @transaction.atomic()
    def test_api_list_view(self):
        ''' Testing webshops.apis.ProductViewSet list view'''
        url = reverse('webshops:api_product-list')
        res = self.apiclient.get(url)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(len(data), 4)
        self.assertEqual(len(data['results']), 1)
        _obj = data['results'][0]

        self.assertEqual(
            _obj['price_excl_vat'],
            '{:.2f}'.format(round(100 * decimal.Decimal(self.price) / decimal.Decimal(100 + 6), 2))
        )
        self.assertEqual(_obj['id'], self.object.id)
        self.assertEqual(_obj['category'], self.object.category.id)
        self.assertEqual(_obj['vat'], 6)
        self.assertEqual(_obj['webshop'], self.object.webshop.id)
        self.assertEqual(_obj['price'], '{:.2f}'.format(round(self.price, 2)))
        self.assertEqual(_obj['name'], self.name)

        # authorization
        res = self.apiclient.login(password='12345', username=self.user)
        self.assertTrue(res)

        res = self.apiclient.get(url)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(len(data), 4)
        self.assertEqual(len(data['results']), 1)
        _obj = data['results'][0]

        self.assertEqual(_obj['id'], self.object.id)
        self.assertEqual(_obj['category'], self.object.category.id)
        self.assertEqual(_obj['vat'], 6)
        self.assertEqual(_obj['webshop'], self.object.webshop.id)
        self.assertEqual(_obj['price'], '{:.2f}'.format(round(self.price, 2)))
        self.assertEqual(_obj['name'], self.name)

        res = self.apiclient.logout()

    @transaction.atomic()
    def test_api_create_view(self):
        ''' Testing webshops.apis.ProductViewSet create view'''
        url = reverse('webshops:api_product-list')
        #res = self.apiclient.post(url, data={})
        #self.assertEqual(res.status_code, 404)

        # authorization
        res = self.apiclient.login(password='12345', username=self.user)
        self.assertTrue(res)

        res = self.apiclient.post(url, data={})
        self.assertEqual(res.status_code, 400)

        data = dict(
            webshop=self.webshop.id,
            category=self.category.id,
            name=self.name,
            price=self.price,
        )
        res = self.apiclient.post(url, data=data)
        self.assertEqual(res.status_code, 201)
        new__obj = json.loads(res.content)

        self.obj_model.objects.filter(id=new__obj['id']).delete()
        res = self.apiclient.logout()

    @transaction.atomic()
    def test_api_detail_view(self):
        ''' Testing webshops.apis.ProductViewSet detail view'''
        url = reverse('webshops:api_product-detail', kwargs=dict(pk=self.object.pk))
        res = self.apiclient.get(url)
        self.assertEqual(res.status_code, 200)

    @transaction.atomic()
    def test_api_update_view(self):
        ''' Testing webshops.apis.ProductViewSet update view'''
        url = reverse('webshops:api_product-detail', kwargs=dict(pk=self.object.pk))
        #res = self.apiclient.put(url)
        #self.assertEqual(res.status_code, 404)

        # authorization
        res = self.apiclient.login(password='12345', username=self.user)
        self.assertTrue(res)

        data = dict(
            webshop=self.webshop.id,
            category=self.category.id,
            name=self.name,
            price=self.price,
        )
        res = self.apiclient.post(reverse('webshops:api_product-list'), data=data)
        self.assertEqual(res.status_code, 201)
        new__obj = json.loads(res.content)

        _webshop2 = webshops.factories.WebshopFactory.create(
        )
        url = reverse('webshops:api_product-detail', kwargs=dict(pk=new__obj['id']))
        res = self.apiclient.put(url, dict(webshop=_webshop2.id, name='New Name'))
        self.assertEqual(res.status_code, 200)
        _webshop_id = self.obj_model.objects.filter(id=new__obj['id']).last().webshop.pk
        self.assertEquals(_webshop_id, _webshop2.pk)
        data = json.loads(res.content)
        self.assertEqual(data['id'], new__obj['id'])
        self.assertEqual(data['webshop'], _webshop2.pk)
        self.assertEqual(data['name'], 'New Name')

        res = self.apiclient.logout()

    @transaction.atomic()
    def test_api_destroy_view(self):
        ''' Testing webshops.apis.ProductViewSet destroy view'''
        url = reverse('webshops:api_product-detail', kwargs=dict(pk=self.object.pk))
        #res = self.apiclient.delete(url)
        #self.assertEqual(res.status_code, 404)

        # authorization
        res = self.apiclient.login(password='12345', username=self.user)
        self.assertTrue(res)

        data = dict(
            webshop=self.webshop.id,
            category=self.category.id,
            name=self.name,
            price=self.price,
        )
        res = self.apiclient.post(reverse('webshops:api_product-list'), data=data)
        self.assertEqual(res.status_code, 201)
        new__obj = json.loads(res.content)

        url = reverse('webshops:api_product-detail', kwargs=dict(pk=new__obj['id']))
        res = self.apiclient.delete(url)

        self.assertEqual(res.status_code, 204)
        self.assertIsNone(self.obj_model.objects.filter(id=new__obj['id']).last())

        res = self.apiclient.logout()


class OrderAPITestCase(APIBaseTestCase):

    def setUp(self):
        super(OrderAPITestCase, self).setUp()
        self.obj_model = webshops.factories.OrderFactory._meta.model
        self.object = webshops.factories.OrderFactory.create(
            customer=self.user
        )
        self.serializer_class = webshops.serializers.OrderSerializer

    @transaction.atomic()
    def test_api_list_view(self):
        ''' Testing webshops.apis.OrderViewSet list view'''
        url = reverse('webshops:api_order-list')
        res = self.apiclient.get(url)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)

        print data

        self.assertEqual(len(data), 1)
        _obj = data[0]
        self.assertEqual(_obj['id'], self.object.id)
        self.assertFalse(_obj['paid'])
        self.assertFalse(_obj['shipped'])

        # authorization
        res = self.apiclient.login(password='12345', username=self.user)
        self.assertTrue(res)

        res = self.apiclient.get(url)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(len(data), 1)
        _obj = data[0]
        self.assertEqual(_obj['id'], self.object.id)
        self.assertFalse(_obj['paid'])
        self.assertFalse(_obj['shipped'])

        res = self.apiclient.logout()

    @transaction.atomic()
    def test_api_create_view(self):
        ''' Testing webshops.apis.OrderViewSet create view'''
        url = reverse('webshops:api_order-list')
        #res = self.apiclient.post(url, data={})
        #self.assertEqual(res.status_code, 404)

        # authorization
        res = self.apiclient.login(password='12345', username=self.user)
        self.assertTrue(res)

        with self.assertRaises(IntegrityError) as cm:
            res = self.apiclient.post(url, data={})
        self.assertEqual(cm.expected, IntegrityError)

    @transaction.atomic()
    def test_api_detail_view(self):
        ''' Testing webshops.apis.OrderViewSet detail view'''
        url = reverse('webshops:api_order-detail', kwargs=dict(pk=self.object.pk))
        res = self.apiclient.get(url)
        self.assertEqual(res.status_code, 200)

    @transaction.atomic()
    def test_api_update_view(self):
        ''' Testing webshops.apis.OrderViewSet update view'''
        url = reverse('webshops:api_order-detail', kwargs=dict(pk=self.object.pk))
        #res = self.apiclient.put(url)
        #self.assertEqual(res.status_code, 404)

        # authorization
        res = self.apiclient.login(password='12345', username=self.user)
        self.assertTrue(res)

        url = reverse('webshops:api_order-detail', kwargs=dict(pk=self.object.pk))
        res = self.apiclient.put(url, dict(paid=True))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertTrue(data['paid'])

        url = reverse('webshops:api_order-detail', kwargs=dict(pk=self.object.pk))
        res = self.apiclient.put(url, dict(paid=False))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertFalse(data['paid'])

        res = self.apiclient.logout()

    @transaction.atomic()
    def test_api_destroy_view(self):
        ''' Testing webshops.apis.OrderViewSet destroy view'''
        url = reverse('webshops:api_order-detail', kwargs=dict(pk=self.object.pk))
        #res = self.apiclient.delete(url)
        #self.assertEqual(res.status_code, 404)

        # authorization
        res = self.apiclient.login(password='12345', username=self.user)
        self.assertTrue(res)

        _object = webshops.factories.OrderFactory.create(
            customer=self.user,
        )
        url = reverse('webshops:api_order-detail', kwargs=dict(pk=_object.pk))
        res = self.apiclient.delete(url)
        self.assertEqual(res.status_code, 204)
        self.assertIsNotNone(self.obj_model.objects.filter(id=_object.pk).last().deleted_at)

        res = self.apiclient.logout()

    def tearDown(self):
        super(OrderAPITestCase, self).tearDown()

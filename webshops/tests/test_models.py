# coding: utf-8
from __future__ import unicode_literals

import decimal
import mock
import random
import string

from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from simpleAPI.testtools import BaseTest
# from webshop.models import Webshop

import webshops.factories

__author__ = 'smirnov.ev'


class WebshopModelTestCase(BaseTest):
    def setUp(self):
        self.obj_model = webshops.factories.WebshopFactory._meta.model
        self.site_id = settings.SITE_ID
        self.name = ''.join(random.choice(string.letters) for _ in range(100))
        self.webshop = webshops.factories.WebshopFactory.create(name=self.name)

    def tearDown(self):
        self.webshop.delete()
        self.assertEqual(self.obj_model.objects.count(), 0)

    @transaction.atomic()
    def test_queryset(self):
        """ Testing webshop.Webshop model queryset """

        # active method
        self.assertEqual(list(self.obj_model.objects.active()), [])

        self.webshop.active = True
        self.webshop.save()

        self.assertEqual(list(self.obj_model.objects.active()), [self.webshop])

        self.webshop.active = False
        self.webshop.save()

    def test_deleted_manager(self):
        """ Testing webshop.Webshop model deleted manager """
        self.checking_deleted_manager(self.webshop)

    def test_unicode_method(self):
        """ Testing webshop.Webshop model __unicode__ method """
        self.assertEqual('{}'.format(self.webshop), self.name)

    @transaction.atomic()
    def test_save_method(self):
        """ Testing webshop.Webshop model save method """
        _obj = webshops.factories.WebshopFactory.create()

        _obj.delete()

    @transaction.atomic()
    def test_num_products_method(self):
        """ Testing webshop.Webshop model num_products method """
        self.assertEqual(self.webshop.num_products(), 0)

        _cat1 = webshops.factories.CategoryFactory.create(webshop=self.webshop)
        _product1 = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=_cat1)
        _product2 = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=_cat1)

        self.assertEqual(self.webshop.num_products(), 2)

        _product1.delete()
        _product2.delete()
        _cat1.delete()

    @transaction.atomic()
    def test_num_categories_method(self):
        """ Testing webshop.Webshop model num_categories method """
        self.assertEqual(self.webshop.num_categories(), 0)

        _cat1 = webshops.factories.CategoryFactory.create(webshop=self.webshop)
        _cat2 = webshops.factories.CategoryFactory.create(webshop=self.webshop)

        self.assertEqual(self.webshop.num_categories(), 2)

        _cat1.delete()
        _cat2.delete()

    @transaction.atomic()
    def test_get_products_method(self):
        """ Testing webshop.Webshop model get_products method """
        self.assertEqual(list(self.webshop.get_products()), [])

        _cat1 = webshops.factories.CategoryFactory.create(webshop=self.webshop)
        _product1 = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=_cat1, active=False)
        _product2 = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=_cat1, active=False)

        self.assertEqual(list(self.webshop.get_products()), [])
        self.assertTrue(
            _product1 in list(self.webshop.get_products(active=False)))
        self.assertTrue(
            _product2 in list(self.webshop.get_products(active=False)))

        _product1.delete()
        _product2.delete()
        _cat1.delete()

    @transaction.atomic()
    def test_get_categories_method(self):
        """ Testing webshop.Webshop model get_categories method """
        self.assertEqual(list(self.webshop.get_categories()), [])

        _cat1 = webshops.factories.CategoryFactory.create(webshop=self.webshop)
        _cat2 = webshops.factories.CategoryFactory.create(webshop=self.webshop)

        self.assertTrue(_cat1 in list(self.webshop.get_categories()))
        self.assertTrue(_cat2 in list(self.webshop.get_categories()))

        _cat1.delete()
        _cat2.delete()


class CategoryModelTestCase(BaseTest):
    def setUp(self):
        self.obj_model = webshops.factories.CategoryFactory._meta.model
        self.name = ''.join(random.choice(string.letters) for _ in range(100))
        self.webshop = webshops.factories.WebshopFactory.create()
        self.category = webshops.factories.CategoryFactory(
            webshop=self.webshop, name=self.name)

    def tearDown(self):
        self.category.delete()
        self.webshop.delete()
        self.assertEqual(self.obj_model.objects.count(), 0)

    def test_initials(self):
        """ Testing webshop.Category model initials """
        fields = ('webshop', 'name')
        self.assertEqualModelFields(self.category, fields)

        self.assertEqual(self.category.description, '')
        self.assertIsNone(self.category.parent)

    def test_deleted_manager(self):
        """ Testing webshop.Category model deleted manager """
        self.checking_deleted_manager(self.category)

    def test_unicode_method(self):
        """ Testing webshop.Category model __unicode__ method """
        self.assertEqual('{}'.format(self.category), self.name)

    @transaction.atomic()
    def test_get_children_method(self):
        """ Testing webshop.Category model get_children method """
        self.assertEqual(list(self.category.get_children()), [])

        _cat2 = webshops.factories.CategoryFactory.create(
            webshop=self.webshop, parent=self.category)

        self.assertEqual(list(self.category.get_children()), [_cat2])
        self.assertTrue(_cat2 in list(self.category.get_children()))

        _cat2.delete()

    @transaction.atomic()
    def test_get_products_method(self):
        """ Testing webshop.Webshop model get_products method """
        self.assertEqual(list(self.category.get_products()), [])

        _cat2 = webshops.factories.CategoryFactory.create(
            webshop=self.webshop, parent=self.category)
        _product1 = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category)
        _product2 = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=_cat2)

        # self.assertEqual(list(self.category.get_products()), [])
        self.assertTrue(
            _product1 in list(self.category.get_products()))
        self.assertTrue(
            _product2 in list(self.category.get_products()))

        _product1.delete()
        _product2.delete()
        _cat2.delete()


class ProductModelTestCase(BaseTest):
    def setUp(self):
        self.obj_model = webshops.factories.ProductFactory._meta.model
        self.name = ''.join(random.choice(string.letters) for _ in range(100))
        self.webshop = webshops.factories.WebshopFactory.create()
        self.category = webshops.factories.CategoryFactory(webshop=self.webshop)
        self.price = decimal.Decimal(99.99)
        self.product = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=self.price)

    def tearDown(self):
        self.product.delete()
        self.category.delete()
        self.webshop.delete()
        self.assertEqual(self.obj_model.objects.count(), 0)

    def test_initials(self):
        """ Testing webshop.Product model initials """
        fields = (
            'webshop', 'name', 'category', 'price'
        )
        self.assertEqualModelFields(self.product, fields)

        self.assertTrue(self.product.active)
        self.assertTrue(self.product.featured)

    def test_deleted_manager(self):
        """ Testing webshop.Product model deleted manager """
        _count = self.obj_model.objects.count()
        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=self.price)
        self.assertEqual(self.obj_model.objects.count(), _count + 1)
        _obj.delete()
        self.assertEqual(self.obj_model.objects.count(), _count)

    @transaction.atomic()
    def test_queryset_manager(self):
        """ Testing webshop.Product model queryset and manager """

        # active method
        self.assertEqual(list(self.obj_model.objects.active()), [self.product])

        self.product.active = False
        self.product.save()

        self.assertEqual(list(self.obj_model.objects.active()), [])

        # default method
        self.assertEqual(list(self.obj_model.objects.default()), [self.product])

        self.product.structure = self.obj_model.CHILD
        self.product.save()
        self.assertEqual(list(self.obj_model.objects.default()), [])

        # featured method
        self.assertEqual(list(self.obj_model.objects.featured()), [self.product])

        self.product.featured = False
        self.product.save()
        self.assertEqual(list(self.obj_model.objects.featured()), [])

        self.product.active = True
        self.product.featured = True
        self.product.structure = self.obj_model.STANDALONE
        self.product.save()

        self.assertEqual(
            list(self.obj_model.objects.active().featured().default()),
            [self.product]
        )

    @transaction.atomic()
    def test_str_method(self):
        """ Testing webshop.Product model __str__ method """
        self.assertEqual('{}'.format(self.product), self.name)

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=self.price,
            parent=self.product,
        )
        self.assertEqual('{}'.format(_obj), '{}'.format(self.product))

        _obj.name = ''
        _obj.attribute = {}
        _obj.save()
        self.assertEqual('{}'.format(_obj), self.product.name)

        _obj.delete()

    @transaction.atomic()
    def test_clean_method(self):
        """ Testing webshop.Product model clean method """
        self.assertIsNone(self.product.clean())

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=0,
            structure=self.obj_model.STANDALONE,
        )
        self.assertIsNone(_obj.clean())

        _obj.structure = self.obj_model.PARENT
        _obj.pcs_in_stock = 0
        _obj.save()
        self.assertIsNone(_obj.clean())

        _obj_child = webshops.factories.ProductFactory.create(
            webshop=self.webshop, name=self.name,
            price=0,
            structure=self.obj_model.CHILD,
            parent=_obj,
            category=None,
        )
        self.assertIsNone(_obj_child.clean())

        _obj_child.delete()
        _obj.delete()

    @transaction.atomic()
    def test_clean_0_method(self):
        """ Testing webshop.Product model _clean_0 method """
        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=0,
            structure=0,
        )
        self.assertIsNone(_obj._clean_0())

        _obj.name = ''
        _obj.save()
        try:
            _obj._clean_0()
        except ValidationError:
            pass
        else:
            raise "Don't raise ValidationError(_('Your product must have a title.'))"

        _obj.name = self.name
        _obj.parent = self.product
        _obj.save()
        try:
            _obj._clean_0()
        except ValidationError:
            pass
        else:
            raise "Don't raise ValidationError(_('Only child products can have a parent.'))"

        _obj.delete()

    @transaction.atomic()
    def test_clean_1_method(self):
        """ Testing webshop.Product model _clean_1 method """
        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=1.0,
            structure=1,
        )
        try:
            _obj._clean_1()
        except ValidationError:
            pass
        else:
            raise "Don't raise ValidationError(_('A parent product can't have stockrecords.'))"

        _obj.price = 0
        _obj.pcs_in_stock = 1
        _obj.save()
        try:
            _obj._clean_1()
        except ValidationError:
            pass
        else:
            raise "Don't raise ValidationError(_('A parent product can't have stockrecords.'))"

        _obj.delete()

    @transaction.atomic()
    def test_clean_2_method(self):
        """ Testing webshop.Product model _clean_2 method """
        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=1.0,
            structure=2,
        )
        try:
            _obj._clean_2()
        except ValidationError:
            pass
        else:
            raise "Don't raise ValidationError(_('A child product needs a parent.'))"

        _obj.parent = self.product
        _obj.save()
        try:
            _obj._clean_2()
        except ValidationError:
            pass
        else:
            raise "Don't raise ValidationError(_('You can only assign child " \
                  "products to parent products.'))"

        _obj.structure = self.obj_model.PARENT
        _obj.save()
        _obj_child = webshops.factories.ProductFactory.create(
            webshop=self.webshop, name=self.name,
            price=0,
            structure=2,
            parent=_obj,
            category=self.category,
        )
        try:
            _obj_child._clean_2()
        except ValidationError:
            pass
        else:
            raise "Don't raise ValidationError(_('A child product can't have a category assigned.'))"

        _obj_child.delete()
        _obj.delete()

    @transaction.atomic()
    def test_save_method(self):
        """ Testing webshop.Product model save method """
        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name='Parent Name',
            price=1.0,
            structure=2,
        )
        self.assertIsNotNone(_obj)
        self.assertEqual(_obj.description, '')

        _obj.description = 'Description'
        _obj.save()
        self.assertEqual(_obj.description, 'Description')

        _obj_child = webshops.factories.ProductFactory.create(
            webshop=self.webshop, name='Chald Name',
            price=self.price,
            parent=_obj,
        )

        _obj = self.obj_model.objects.get(pk=_obj.pk)
        _obj.name = 'New Parent Name'
        _obj.save()
        _obj_child.refresh_from_db()
        self.assertEqual(_obj_child.name, 'New Parent Name')

        _obj.delete()

    @transaction.atomic()
    def test_calculate_prices_method(self):
        """ Testing webshop.Product model calculate_prices method """
        self.assertIsNone(self.product.calculate_prices())

        _webshop = webshops.factories.WebshopFactory.create()
        _obj = webshops.factories.ProductFactory.create(
            webshop=_webshop, category=self.category, name='Parent Name',
            price=0,
            structure=2, price_excl_vat=0, vat=6,
        )
        self.assertIsNone(_obj.calculate_prices())
        self.assertEqual(_obj.price, 0)
        self.assertEqual(_obj.price_excl_vat, 0)

        _obj.price = 1.3456
        self.assertIsNone(_obj.calculate_prices())
        self.assertEqual(_obj.price, 1.3456)
        self.assertEqual(_obj.price_excl_vat, 1.27)
        _obj.delete()
        _webshop.delete()

    @transaction.atomic()
    def test_has_children_method(self):
        """ Testing webshop.Product model has_children method """
        self.assertFalse(self.product.has_children())

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=1.0,
            structure=2,
        )
        _obj_child = webshops.factories.ProductFactory.create(
            webshop=self.webshop, name=self.name,
            price=0,
            structure=2,
            parent=_obj,
            category=self.category,
        )
        _obj.refresh_from_db()
        self.assertTrue(_obj.has_children())

        _obj_child.delete()
        _obj.delete()

    @transaction.atomic()
    def test_is_standalone_property(self):
        """ Testing webshop.Webshop model is_standalone property """
        self.assertTrue(self.product.is_standalone)

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=1.0,
            structure=self.obj_model.CHILD,
        )
        self.assertFalse(_obj.is_standalone)

        _obj.delete()

    @transaction.atomic()
    def test_is_parent_property(self):
        """ Testing webshop.Webshop model is_parent property """
        self.assertFalse(self.product.is_parent)

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=1.0,
            structure=self.obj_model.PARENT,
        )
        self.assertTrue(_obj.is_parent)

        _obj.delete()

    @transaction.atomic()
    def test_is_child_property(self):
        """ Testing webshop.Webshop model is_parent property """
        self.assertFalse(self.product.is_child)

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=1.0,
            structure=self.obj_model.CHILD,
        )
        self.assertTrue(_obj.is_child)

        _obj.delete()

    @transaction.atomic()
    def test_can_be_parent_method(self):
        """ Testing webshop.Product model can_be_parent method """
        self.assertTrue(self.product.can_be_parent())
        self.assertTrue(self.product.can_be_parent(give_reason=True))

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=1.0,
            structure=self.obj_model.CHILD,
        )
        self.assertFalse(_obj.can_be_parent())
        self.assertEquals(_obj.can_be_parent(give_reason=True),
                          (False, _('The specified parent product is a child product.')))

        _obj.structure = self.obj_model.STANDALONE
        _obj.pcs_in_stock = 2
        _obj.save()
        self.assertFalse(_obj.can_be_parent())
        self.assertEquals(
            _obj.can_be_parent(give_reason=True),
            (False, _("One can't add a child product to a product with stock  records."))
        )

        _obj.delete()

    @transaction.atomic()
    def test_get_title_method(self):
        """ Testing webshop.Product model get_title method """
        self.assertEquals(self.product.get_title(), self.name)

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name='',
            parent=self.product,
        )
        self.assertEquals(_obj.get_title(), self.name)

        _obj.delete()

    @transaction.atomic()
    def test_has_stockrecords_property(self):
        """ Testing webshop.Webshop model has_stockrecords property """
        self.assertFalse(self.product.has_stockrecords)

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            structure=self.obj_model.CHILD, pcs_in_stock=2,
        )
        self.assertTrue(_obj.has_stockrecords)

        _obj.delete()

    @transaction.atomic()
    def test_get_is_discountable_method(self):
        """ Testing webshop.Product model get_is_discountable method """
        self.assertTrue(self.product.get_is_discountable())

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category,
            parent=self.product, structure=self.obj_model.CHILD,
            is_discountable=False,
        )
        self.assertTrue(_obj.get_is_discountable())

        _obj.structure = self.obj_model.STANDALONE
        self.assertFalse(_obj.get_is_discountable())

        _obj.delete()

    @transaction.atomic()
    def test_get_category_method(self):
        """ Testing webshop.Product model get_category method """
        self.assertEquals(self.product.get_category(), self.category)

        _category = webshops.factories.CategoryFactory(webshop=self.webshop)
        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=_category,
            parent=self.product, structure=self.obj_model.CHILD,
        )

        self.assertEquals(_obj.get_category(), self.category)
        _obj.structure = self.obj_model.STANDALONE
        _obj.save()
        self.assertEquals(_obj.get_category(), _category)

        _obj.delete()

    @transaction.atomic()
    def test_get_price_method(self):
        """ Testing webshop.Product model get_price method """
        self.assertEquals(self.product.get_price(), self.price)

    @transaction.atomic()
    def test_get_price_wtihout_vat_method(self):
        """ Testing webshop.Product model get_price_wtihout_vat method """
        self.assertEquals(self.product.get_price_wtihout_vat(), 94.33)

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=Decimal(127.44),
            structure=self.obj_model.PARENT,
            vat=0,
        )
        self.assertEquals(_obj.get_price_wtihout_vat(), Decimal(127.44))

        _obj.delete()

    @transaction.atomic()
    def test_get_vat_method(self):
        """ Testing webshop.Product model get_vat method """
        self.assertEquals(self.product.get_vat(), 6)

        _obj = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, name=self.name,
            price=1.15,
            structure=self.obj_model.PARENT,
            vat=11,
        )
        self.assertEquals(_obj.get_vat(), 11)

        _obj_child = webshops.factories.ProductFactory.create(
            webshop=self.webshop, name=self.name,
            price=Decimal(2.23),
            structure=self.obj_model.CHILD,
            category=None,
            vat=19,
        )
        self.assertEquals(_obj_child.get_vat(), 19)

        _obj_child.parent = _obj
        _obj_child.save()
        self.assertEquals(_obj_child.get_vat(), 11)

        _obj_child.delete()
        _obj.delete()

    @transaction.atomic()
    def test_vat_amount_method(self):
        """ Testing webshop.Product model vat_amount method """
        self.assertEqual(self.product.vat_amount(), 6)

        self.product.vat = 0
        self.assertIsNone(self.product.vat_amount())

    @transaction.atomic()
    def test_get_barcode_method(self):
        """ Testing webshop.Product model get_barcode method """
        self.assertEquals('', self.product.get_barcode())

        _obj_parent = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category)
        self.assertEquals(_obj_parent.get_barcode(), '')

        _obj_child = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, parent=_obj_parent)
        self.assertEqual(_obj_child.get_barcode(), '')

        _obj_child.delete()
        _obj_parent.delete()

    @transaction.atomic()
    def test_get_barcode_type_method(self):
        """ Testing webshop.Product model get_barcode_type method """
        self.assertEquals(0, self.product.get_barcode_type())

        _obj_parent = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category)
        self.assertEqual(_obj_parent.get_barcode_type(), 0)

        _obj_child = webshops.factories.ProductFactory.create(
            webshop=self.webshop, category=self.category, parent=_obj_parent)
        self.assertEqual(_obj_child.get_barcode_type(), 0)

        _obj_child.delete()
        _obj_parent.delete()


class OrderModelTestCase(BaseTest):
    def setUp(self):
        self.obj_model = webshops.factories.OrderFactory._meta.model
        self.subtotal = decimal.Decimal(99.01)
        self.vat = decimal.Decimal(0.99)
        self.total = decimal.Decimal(100)
        self.customer = webshops.factories.UserFactory.create()
        self.object = webshops.factories.OrderFactory.create(
            customer=self.customer,
            subtotal=self.subtotal, vat=self.vat, total=self.total)

    def test_initials(self):
        """ Testing webshop.Order model initials """
        fields = ('subtotal', 'vat', 'total', 'customer')
        self.assertEqualModelFields(self.object, fields)

        self.assertIsNone(self.object.phone)
        # self.assertEqual(self.object.phone, '')

        self.assertFalse(self.object.paid)
        self.assertFalse(self.object.shipped)

    def tearDown(self):
        self.object.delete()
        self.customer.delete()
        self.assertEqual(self.obj_model.objects.count(), 1)

    @transaction.atomic()
    def test_save_method(self):
        """ Testing webshop.Order model save method """
        self.object.save()

    @transaction.atomic()
    def test_send_status_changed_email_method(self):
        """ Testing webshop.Order model send_status_changed_email method """
        _webshop = webshops.factories.WebshopFactory.create()
        _object = webshops.factories.OrderFactory.create(
            customer=self.customer,
            subtotal=self.subtotal, vat=self.vat, total=self.total,
            webshop=_webshop,
        )
        #with mock.patch('webshops.models.send_email') as perm_mock:
        #    perm_mock.return_value = 'test send mail ok'
        self.assertIsNone(_object.send_status_changed_email())

        _object.delete()
        _webshop.delete()

    @transaction.atomic()
    def test_get_webshop_method(self):
        """ Testing webshop.Order model get_webshop method """
        self.assertIsNone(self.object.get_webshop())
        _webshop = webshops.factories.WebshopFactory.create()

        _category = webshops.factories.CategoryFactory(webshop=_webshop)
        _product = webshops.factories.ProductFactory.create(
            webshop=_webshop, category=_category)
        _orderproduct = webshops.factories.OrderProductFactory.create(
            order=self.object, product=_product)
        self.assertEqual(self.object.get_webshop(), _webshop)

        _object = webshops.factories.OrderFactory.create(
            customer=self.customer,
            subtotal=self.subtotal, vat=self.vat, total=self.total,
            webshop=_webshop,
        )
        self.assertEqual(_object.get_webshop(), _webshop)

        _object.delete()
        _orderproduct.delete()
        _product.delete()
        _category.delete()
        _webshop.delete()


class OrderProductModelTestCase(BaseTest):
    def setUp(self):
        self.obj_model = webshops.factories.OrderProductFactory._meta.model
        self.webshop = webshops.factories.WebshopFactory.create()
        self.product = webshops.factories.ProductFactory.create(webshop=self.webshop)
        self.order = webshops.factories.OrderFactory.create()
        self.quantity = 1
        self.name = ''.join(random.choice(string.letters) for _ in range(100))
        self.price = decimal.Decimal(99.90)
        if self.product and self.quantity:
            self.price = self.product.price
        self.object = webshops.factories.OrderProductFactory.create(
            order=self.order, product=self.product, quantity=self.quantity,
            name=self.name, price=self.price)

    def test_initials(self):
        """ Testing webshop.OrderProduct model initials """
        fields = ('order', 'product', 'quantity', 'name', 'price')
        self.assertEqualModelFields(self.object, fields)

    def tearDown(self):
        self.object.delete()
        self.order.delete()
        self.product.delete()
        self.webshop.delete()
        self.assertEqual(self.obj_model.objects.count(), 0)

    def test_get_price_method(self):
        """ Testing webshop.OrderProduct model get_price method """
        self.assertEquals(self.object.get_price(), self.product.price)

    @transaction.atomic()
    def test_get_price_wtihout_vat_method(self):
        """ Testing webshop.OrderProduct model get_price_wtihout_vat method """
        _product = webshops.factories.ProductFactory.create(webshop=self.webshop, vat=0)
        _object = webshops.factories.OrderProductFactory.create(
            order=self.order, product=_product, quantity=self.quantity,
            name=self.name, price=decimal.Decimal(87.16))
        self.assertEquals(_object.get_price_wtihout_vat(), 87.16)

        _product.vat = 10
        _product.save()
        self.assertEquals(_object.get_price_wtihout_vat(), 79.24)

        _object.delete()
        _product.delete()

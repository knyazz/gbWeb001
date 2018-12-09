# coding: utf-8
from __future__ import unicode_literals

import decimal
import faker
import factory
import random
import string

from django.conf import settings
from django.contrib.auth import get_user_model

from webshops import models

User = get_user_model()
_faker = faker.Factory.create(locale=settings.LANGUAGE_CODE)

__author__ = 'smirnov.ev'


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.LazyAttribute(lambda o: _faker.first_name()[:30].strip())
    last_name = factory.LazyAttribute(lambda o: _faker.last_name()[:30].strip())

    username = factory.LazyAttribute(lambda o: _faker.user_name()[:30].strip(
        ).replace('.', '_').replace('-', '_'))
    email = factory.LazyAttribute(lambda o: _faker.free_email())

    password = '12345'


class WebshopFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(
        lambda o: ''.join(random.choice(string.letters) for _ in range(100)))

    class Meta:
        model = models.Webshop


class CategoryFactory(factory.DjangoModelFactory):
    webshop = factory.SubFactory(WebshopFactory)
    name = factory.LazyAttribute(
        lambda o: ''.join(random.choice(string.letters) for _ in range(100)))

    class Meta:
        model = models.Category


class ProductFactory(factory.DjangoModelFactory):
    webshop = factory.SubFactory(WebshopFactory)
    category = factory.SubFactory(CategoryFactory)
    name = factory.LazyAttribute(
        lambda o: ''.join(random.choice(string.letters) for _ in range(100)))
    price = factory.LazyAttribute(
        lambda _: decimal.Decimal(random.randrange(10000))/100)

    class Meta:
        model = models.Product


class OrderFactory(factory.DjangoModelFactory):
    customer = factory.SubFactory(UserFactory)
    subtotal = factory.LazyAttribute(
        lambda _: decimal.Decimal(random.randrange(1000000))/100)
    vat = factory.LazyAttribute(
        lambda _: decimal.Decimal(random.randrange(1000000))/100)
    total = factory.LazyAttribute(
        lambda _: decimal.Decimal(random.randrange(1000000))/100)

    class Meta:
        model = models.Order


class OrderProductFactory(factory.DjangoModelFactory):
    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    name = factory.LazyAttribute(
        lambda o: ''.join(random.choice(string.letters) for _ in range(100)))
    price = factory.LazyAttribute(
        lambda _: decimal.Decimal(random.randrange(10000))/100)

    class Meta:
        model = models.OrderProduct

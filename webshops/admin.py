# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from webshops import models as wmodels

admin.site.register(wmodels.Webshop)
admin.site.register(wmodels.Category)
admin.site.register(wmodels.Product)
admin.site.register(wmodels.Order)
admin.site.register(wmodels.OrderProduct)

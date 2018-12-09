# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import pagination


class ProductPagination(pagination.PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'

from __future__ import unicode_literals

from django.db import models


class WebshopQuerySet(models.QuerySet):
    """ queryset manager for models.Webshop """

    def active(self):
        return self.filter(active=True)


class WebshopManager(models.Manager):

    def active(self):
        return self.get_queryset().active()

    def get_queryset(self):
        _qs = WebshopQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)
        return _qs


class CategoryQuerySet(models.QuerySet):
    """ queryset manager for models.Category """

    def active(self):
        return self.filter(active=True)


class CategoryManager(models.Manager):

    def active(self):
        return self.get_queryset().active()

    def get_queryset(self):
        _qs = CategoryQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)
        return _qs


class ProductQuerySet(models.QuerySet):
    """ queryset manager for models.Product """

    def active(self):
        return self.filter(active=True)

    def default(self):
        return self.filter(
            structure__in=(self.model.STANDALONE, self.model.PARENT))

    def featured(self):
        return self.filter(featured=True)


class ProductManager(models.Manager):

    def active(self):
        return self.get_queryset().active()

    def default(self):
        return self.get_queryset().default()

    def featured(self):
        return self.get_queryset().featured()

    def get_queryset(self):
        _qs = ProductQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)
        return _qs

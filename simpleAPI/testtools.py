# coding: utf-8
from __future__ import unicode_literals

from django import test
from django.utils import timezone

__author__ = 'smirnov.ev'


class BaseTest(test.TestCase):

    def checking_deleted_manager(self, obj):
        """ Testing DeletedManager for model object """
        self.assertIsNone(obj.deleted_at)
        self.assertEqual(self.obj_model.objects.count(), 1)

        obj.deleted_at = timezone.now()
        obj.save()
        self.assertEqual(self.obj_model.objects.count(), 0)

        obj.deleted_at = None
        obj.save()

    def assertEqualModelFields(self, obj, model_fields):
        """
            asserts django model object fields & test case object attr

            :param model_fields: django model fields
            :type model_fields: iterable
            :param obj: django model object
            :type obj: Django Model
        """
        for field in model_fields:
            # print field
            self.assertEqual(getattr(obj, field), getattr(self, field))

    def assertEqualValueFields(self, obj, model_fields, value):
        """
            asserts django model object fields & test case object attr

            :param model_fields: django model fields
            :type model_fields: iterable
            :param obj: django model object
            :type obj: Django Model
        """
        for field in model_fields:
            # print field
            self.assertEqual(getattr(obj, field), value)

    def assertIsBlankModelFields(self, obj, model_fields):
        """
            asserts django model object fields are blank

            :param model_fields: django model fields
            :type model_fields: iterable
            :param obj: django model object
            :type obj: Django Model
        """
        for field in model_fields:
            #print field
            self.assertEqual(getattr(obj, field), '')

    def assertIsNoneModelFields(self, obj, model_fields):
        """
            asserts django model object fields are None

            :param model_fields: django model fields
            :type model_fields: iterable
            :param obj: django model object
            :type obj: Django Model
        """
        for field in model_fields:
            #print field
            self.assertIsNone(getattr(obj, field))

    def assertTrueModelFields(self, obj, model_fields):
        """
            asserts django model object fields are True

            :param model_fields: django model fields
            :type model_fields: iterable
            :param obj: django model object
            :type obj: Django Model
        """
        for field in model_fields:
            # print field
            self.assertTrue(getattr(obj, field))

    def assertFalseModelFields(self, obj, model_fields):
        """
            asserts django model object fields are False

            :param model_fields: django model fields
            :type model_fields: iterable
            :param obj: django model object
            :type obj: Django Model
        """
        for field in model_fields:
            # print field
            self.assertFalse(getattr(obj, field))

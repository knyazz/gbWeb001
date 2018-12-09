# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import decimal

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from webshops.tasks import send_email

from webshops.querysets import CategoryManager
from webshops.querysets import ProductManager, WebshopManager


@python_2_unicode_compatible
class Webshop(models.Model):
    site = models.ForeignKey(
        Site, related_name="webshops", db_index=True, default=settings.SITE_ID,
        editable=False)
    active = models.BooleanField(verbose_name=_("Active"), default=False)
    name = models.TextField(verbose_name=_("Name"))

    objects = WebshopManager()

    deleted_at = models.DateTimeField(blank=True, null=True, editable=False)
    added_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('-active', 'name',)

    def __str__(self):
        return self.name

    def num_products(self):
        return self.products.all().count()

    def num_categories(self):
        return self.categories.all().count()

    def get_products(self, active=True):
        products = self.products.default()
        if active:
            products = products.active()
        return products

    def get_categories(self):
        return self.categories.all()


@python_2_unicode_compatible
class Category(models.Model):
    webshop = models.ForeignKey(
        Webshop, editable=False, related_name="categories")
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children')
    name = models.TextField(verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    active = models.BooleanField(verbose_name=_("Active"), default=True)

    objects = CategoryManager()

    deleted_at = models.DateTimeField(blank=True, null=True, editable=False)
    added_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('name', '-pk', '-added_at')

    def __str__(self):
        return self.name

    def get_children(self):
        return self.children.filter(active=True)

    def get_products(self):
        q = models.Q(active=True)
        q &= models.Q(category=self) | models.Q(category__parent=self)
        return self.webshop.products.filter(q)


@python_2_unicode_compatible
class Product(models.Model):
    """
    The base product object

    There's three kinds of products; they're distinguished by the structure
    field.

    - A stand alone product. Regular product that lives by itself.
    - A child product. All child products have a parent product. They're a
      specific version of the parent.
    - A parent product. It essentially represents a set of products.

    An example could be a yoga course, which is a parent product. The different
    times/locations of the courses would be associated with the child products.
    """
    STANDALONE, PARENT, CHILD = 0, 1, 2
    STRUCTURE_CHOICES = (
        (STANDALONE, _('Stand-alone product')),
        (PARENT, _('Parent product')),
        (CHILD, _('Child product'))
    )
    NO_VAT, VAT_LOW, VAT_HIGH = 0, 6, 21
    VAT_CHOICES = (
        (NO_VAT, _('None')),
        (VAT_LOW, _('VAT low (6%)')),
        (VAT_HIGH, _('VAT high (21%)')),
    )
    NO_BARCODE = 0
    CODE128_BARCODE = 1
    EAN_BARCODE = 2
    EAN8_BARCODE = 3
    CODE39_BARCODE = 4
    CODE39VIN_BARCODE = 5
    CODABAR_BARCODE = 6
    UPC_BARCODE = 7
    UPCE_BARCODE = 8
    I2OF5_BARCODE = 9
    TWOOF5_BARCODE = 10
    CODE93_BARCODE = 11
    BARCODE_TYPES_CHOICES = (
        (NO_BARCODE, _('None')),
        (CODE128_BARCODE, _('Code 128')),
        (EAN_BARCODE, _('EAN')),
        (EAN8_BARCODE, _('EAN-8')),
        (CODE39_BARCODE, _('Code 93')),
        (CODE39VIN_BARCODE, _('Code 93 VIN')),
        (CODABAR_BARCODE, _('Codabar')),
        (UPC_BARCODE, _('UPC')),
        (UPCE_BARCODE, _('UPC E')),
        (I2OF5_BARCODE, _('Code 25 – Interleaved 2 of 5')),
        (TWOOF5_BARCODE, _('Code 25 – Non-interleaved 2 of 5')),
        (CODE93_BARCODE, _('Code 93')),
    )

    objects = ProductManager()
    structure = models.PositiveSmallIntegerField(
        _("Product structure"), choices=STRUCTURE_CHOICES, default=STANDALONE)

    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name=_("Parent product"),
        help_text=_(
            "Only choose a parent product if you're creating a child product."
            "  For example if this is a size 4 of a particular t-shirt."
            "  Leave blank if this is a stand-alone product (i.e. there is only"
            " one version of this product)."))

    # Title is mandatory for canonical products but optional for child products
    name = models.TextField(verbose_name=_("Name"))
    description = models.TextField(blank=True)
    webshop = models.ForeignKey(Webshop, related_name="products")
    category = models.ForeignKey(
        'Category', verbose_name=_("Category"), related_name="products",
        null=True, blank=True)
    active = models.BooleanField(verbose_name=_("Active"), default=True)
    featured = models.BooleanField(
        verbose_name=_("Featured"), default=True,
        help_text=_("This product will be displayed on the front page of the shop."))
    barcode_type = models.PositiveSmallIntegerField(
        choices=BARCODE_TYPES_CHOICES, default=0)
    barcode = models.TextField(blank=True)
    pcs_in_stock = models.PositiveIntegerField(
        _("Pieces in stock"), null=True, blank=True)
    price = models.DecimalField(
        decimal_places=2, max_digits=8, verbose_name=_("Price"),
        help_text=_("Price including VAT."), null=True, blank=True)
    price_excl_vat = models.DecimalField(
        decimal_places=2, max_digits=8, verbose_name=_("Price excl VAT"),
        help_text=_("Price excluding VAT."), null=True, blank=True)
    vat = models.PositiveIntegerField(
        verbose_name=_("VAT rate"), default=VAT_LOW, choices=VAT_CHOICES)

    added_at = models.DateTimeField(
        _("Date created"), auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(
        _("Date updated"), auto_now=True, editable=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    #: Determines if a product may be used in an offer. It is illegal to
    #: discount some types of product (e.g. ebooks) and this field helps
    #: merchants from avoiding discounting such products
    #: Note that this flag is ignored for child products; they inherit from
    #: the parent product.
    is_discountable = models.BooleanField(
        _("Is discountable?"), default=True,
        help_text=_("This flag indicates if this product can be used "
                    "in an offer or not")
    )

    class Meta:
        ordering = '-added_at', 'name', 'pk'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.get_title()

    def clean(self):
        """
        Validate a product. Those are the rules:

        +---------------+-------------+--------------+--------------+
        |               | stand alone | parent       | child        |
        +---------------+-------------+--------------+--------------+
        | title         | required    | required     | optional     |
        +---------------+-------------+--------------+--------------+
        | parent        | forbidden   | forbidden    | required     |
        +---------------+-------------+--------------+--------------+
        | stockrecords  | 0 or more   | forbidden    | 0 or more    |
        +---------------+-------------+--------------+--------------+
        | categories    | 1 or more   | 1 or more    | forbidden    |
        +---------------+-------------+--------------+--------------+
        | attributes    | optional    | optional     | optional     |
        +---------------+-------------+--------------+--------------+
        | rec. products | optional    | optional     | unsupported  |
        +---------------+-------------+--------------+--------------+
        | options       | optional    | optional     | forbidden    |
        +---------------+-------------+--------------+--------------+

        Because the validation logic is quite complex, validation is delegated
        to the sub method appropriate for the product's structure.
        """
        getattr(self, '_clean_%s' % self.structure)()

    def _clean_0(self):  # standalone
        """
        Validates a stand-alone product
        """
        if not self.name:
            raise ValidationError(_("Your product must have a title."))
        if self.parent_id:
            raise ValidationError(_("Only child products can have a parent."))

    def _clean_2(self):  # child
        """
        Validates a child product
        """
        if not self.parent_id:
            raise ValidationError(_("A child product needs a parent."))
        if self.parent_id and not self.parent.is_parent:
            raise ValidationError(
                _("You can only assign child products to parent products."))
        #if self.product_class:
        #    raise ValidationError(
        #        _("A child product can't have a product class."))
        if self.pk and self.category:
            raise ValidationError(
                _("A child product can't have a category assigned."))
        # Note that we only forbid options on product level
        #if self.pk and self.options:
        #    raise ValidationError(_("A child product can't have options."))

    def _clean_1(self):  # parent
        """
        Validates a parent product.
        """
        self._clean_0()
        if self.has_stockrecords or self.price:
            raise ValidationError(_("A parent product can't have stockrecords."))

    def save(self, *args, **kwargs):
        _name_changed = not self.pk

        if self.pk:
            _old = self.__class__.objects.filter(pk=self.pk).last()
            _name_changed = _old and _old.name != self.name

        self.calculate_prices()

        super(Product, self).save(*args, **kwargs)

        if _name_changed and self.children.exists():
            self.children.update(name=self.name)

    def calculate_prices(self):
        _vat = self.get_vat()
        if self.price_excl_vat:
            self.price = round(
                decimal.Decimal(self.price_excl_vat) * decimal.Decimal(100 + _vat) / 100, 2)
        elif self.price:
            self.price_excl_vat = round(
                100 * decimal.Decimal(self.price) / decimal.Decimal(100 + _vat), 2)

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=('deleted_at',))

        if self.parent and self.parent.has_children() is False:
                self.parent.structure = self.STANDALONE
                self.parent.save(update_fields=('structure',))

    def has_children(self):
        return self.children.all().exists()

    # Properties

    @property
    def is_standalone(self):
        return self.structure == self.STANDALONE

    @property
    def is_parent(self):
        return self.structure == self.PARENT

    @property
    def is_child(self):
        return self.structure == self.CHILD

    def can_be_parent(self, give_reason=False):
        """
        Helps decide if a the product can be turned into a parent product.
        """
        reason = None
        if self.is_child:
            reason = _('The specified parent product is a child product.')
        if self.has_stockrecords:
            reason = _("One can't add a child product to a product with stock  records.")
        is_valid = reason is None
        if give_reason:
            return is_valid, reason
        else:
            return is_valid

    def get_title(self):
        """
        Return a product's title or it's parent's title if it has no title
        """
        title = self.name
        if not title and self.parent_id:
            title = self.parent.name
        return title
    get_title.short_description = pgettext_lazy("Product title", "Title")

    @property
    def has_stockrecords(self):
        """
        Test if this product has any stockrecords
        """
        return self.pcs_in_stock > 0

    def get_is_discountable(self):
        """
        At the moment, is_discountable can't be set individually for child
        products; they inherit it from their parent.
        """
        if self.is_child:
            return self.parent.is_discountable
        return self.is_discountable

    def get_category(self):
        """
        Return a product's categories or parent's if there is a parent product.
        """
        if self.is_child:
            return self.parent.category
        return self.category
    get_category.short_description = _("Category")

    def get_price(self):
        return self.parent and self.parent.price or self.price

    def get_price_wtihout_vat(self):
        _price = self.get_price()
        _vat = self.get_vat()
        if _vat and _price:
            return round(
                100 * decimal.Decimal(_price) / decimal.Decimal(100 + _vat), 2)
        return _price

    def get_vat(self):
        return self.parent and self.parent.vat or self.vat

    def vat_amount(self):
        _price = self.get_price()
        _vat = self.get_vat()
        if _vat == 0 or not _price:
            return None

        return round(decimal.Decimal(_price) * _vat / 100, 2)

    def get_children_prices(self):
        return [_ch.get_price() or 0 for _ch in self.children.active()]

    def get_children_min_price(self, seq=None):
        _seq = seq or self.get_children_prices()
        if _seq:
            return min(_seq)

    def get_barcode(self):
        return self.barcode or (self.parent and self.parent.barcode) or ''

    def get_barcode_type(self):
        return self.barcode_type or (self.parent and self.parent.barcode_type) or 0


class Order(models.Model):

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("User"),
        on_delete=models.SET_NULL, editable=False, null=True)
    webshop = models.ForeignKey(Webshop, related_name="orders", null=True)
    address = models.TextField(blank=True)
    phone = models.TextField(verbose_name=_("Phone"), blank=True, null=True)
    email = models.EmailField(verbose_name=_("Email"), blank=False, null=True)
    date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    shipped = models.BooleanField(default=False)
    subtotal = models.DecimalField(decimal_places=2, max_digits=8)
    vat = models.DecimalField(decimal_places=2, max_digits=8)
    total = models.DecimalField(decimal_places=2, max_digits=8)

    deleted_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        #_price = self.get_discount_price() or self.total
        #self.total_wd = _price
        #if self.total and self.delivery_cost:
        #    self.total_wd = decimal.Decimal(_price) + decimal.Decimal(self.delivery_cost)
        super(Order, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=('deleted_at',))

    def send_status_changed_email(self, title=None):
        subject = "Order #{}".format(self.pk)
        context = {
            'order': self,
            'subject': title or subject,
        }

        if self.paid:
            _html = 'emails/order_paid.html'
            _txt = 'emails/order_paid.txt'
        elif self.shipped:
            _html = 'emails/order_shipped.html'
            _txt = 'emails/order_shipped.txt'
        else:
            _html = 'emails/order_created.html'
            _txt = 'emails/order_created.txt'

        html_content = render_to_string(_html, context)
        text_content = render_to_string(_txt, context)
        send_email.delay(
            subject, text_content, [self.email], html_content=html_content
        )

    def get_webshop(self):
        if self.webshop:
            return self.webshop
        _op = self.orderproduct_set.first()
        return _op and _op.product.webshop


class OrderProduct(models.Model):
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
    reserved = models.BooleanField(default=False)
    name = models.TextField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    price_excl_vat = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True)
    description = models.TextField(blank=True)

    def get_price(self):
        return self.price

    def get_price_wtihout_vat(self):
        _price = self.get_price()
        _vat = self.product.get_vat()
        if _vat and _price:
            return round(
                100 * decimal.Decimal(_price) / decimal.Decimal(100 + _vat), 2
            )
        return _price

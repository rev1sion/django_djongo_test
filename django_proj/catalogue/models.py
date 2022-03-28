from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from catalogue import managers


class CatalogueBaseModel(models.Model):
    _db = 'catalogue_db'
    objects = managers.CrawlerModelManager()

    source = models.CharField(_('Source'), max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        abstract = True


class Category(CatalogueBaseModel):
    name = models.CharField(_('Name'), max_length=255, unique=True, db_index=True)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='child')
    crumbs = models.CharField(_('Breadcrumbs'), max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _("Categories")
        ordering = ('name',)


class Manufacturer(CatalogueBaseModel):
    name = models.CharField(_('Name'), max_length=255, unique=True, blank=True, null=True, db_index=True)
    related_name = models.CharField(_('Alt name'), max_length=255, blank=True, null=True, db_index=True)

    def __str__(self):
        if not self.related_name:
            return self.name
        return self.related_name

    class Meta:
        verbose_name = _('Manufacturer')
        verbose_name_plural = _("Manufacturers")
        ordering = ('name',)


class Autoparts(CatalogueBaseModel):
    """
    Autoparts model
    """
    category = models.ForeignKey('catalogue.Category', related_name='product',
                                 on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Category'))
    title = models.CharField(_('Name'), max_length=255, db_index=True)
    manufacturer = models.ForeignKey(
        'catalogue.Manufacturer',
        on_delete=models.CASCADE, blank=True, null=True,
        verbose_name=_('Manufacturer')
    )
    article = models.CharField(_('Article'), max_length=255, db_index=True)
    product_number = models.CharField(_('Number'), blank=True, null=True, max_length=255,
                                      help_text=_('Used to link with goods from the main database'))
    url = models.URLField(_('Link'), max_length=255)
    description = models.TextField(_('Description'), blank=True, null=True)
    characteristics = models.ManyToManyField(
        'catalogue.Characteristic',
        through='catalogue.CharacteristicValue',
        verbose_name=_("Characteristic"), blank=True,
        help_text=_("A product attribute is something that this product may "
                    "have, such as a size, as specified by its class"))
    similar_products = models.ManyToManyField(
        'catalogue.Autoparts',
        through='catalogue.SimilarPart',
        blank=True,
        verbose_name=_('Similar parts')
    )

    usedin_key = models.CharField(_('Key to the car (remote source)'), max_length=40, null=True, blank=True)

    # task = models.ForeignKey('manage_tasks.Task', on_delete=models.CASCADE, null=True, blank=True,
    #                          verbose_name=_('Task'))

    def get_absolute_url(self):
        return reverse('catalogue:products', kwargs={'pk': self.id})

    def __str__(self):
        return f'{self.manufacturer.name} : {self.article} - {self.title}'

    class Meta:
        verbose_name = _('Autopart')
        verbose_name_plural = _("Autopart")
        ordering = ('title',)


class SimilarPart(CatalogueBaseModel):
    primary = models.ForeignKey(
        'catalogue.Autoparts',
        on_delete=models.CASCADE, default=None,
        related_name='primary_similars',
        verbose_name=_("Primary product"))
    similar = models.ForeignKey(
        'catalogue.Autoparts',
        on_delete=models.CASCADE, default=None,
        verbose_name=_("Similar product"))
    ranking = models.PositiveSmallIntegerField(
        _('Ranking'), default=0, db_index=True,
        help_text=_('Determines order of the products. A product with a higher'
                    ' value will appear before one with a lower ranking.'))

    class Meta:
        ordering = ['-ranking', 'primary']
        unique_together = ('primary', 'similar')
        verbose_name = _('Similar part')
        verbose_name_plural = _('Similar parts')

    def __str__(self):
        return f'{self.primary.article} -> {self.similar.article}'


class CharacteristicValue(CatalogueBaseModel):
    characteristic_value = models.CharField(_('Characteristic value'), max_length=150)
    product = models.ForeignKey(
        'catalogue.Autoparts',
        on_delete=models.CASCADE, default=None,
        related_name='characteristic_values',
        verbose_name=_('Product')
    )
    characteristic = models.ForeignKey(
        'catalogue.Characteristic',
        on_delete=models.CASCADE,
        verbose_name=_('Product description field')
    )

    def get_absolute_url(self):
        return reverse('catalogue:product-characteristics-view', kwargs={'pk': self.id})

    def __str__(self):
        return f'{self.id}. Product {self.product.article}; {self.characteristic.name}: {self.characteristic_value}'

    class Meta:
        ordering = ('characteristic',)
        verbose_name = _('Characteristic Value')
        verbose_name_plural = _("Characteristic Values")
        unique_together = ('characteristic', 'product')


class Characteristic(CatalogueBaseModel):
    _name = models.CharField(_('Name'), max_length=150, unique=True)
    replacement_name = models.CharField(_('Replacement name'), max_length=150, blank=True, null=True)
    source = models.CharField(_('Author'), max_length=120, unique=False, blank=True, null=True, default='')

    @property
    def name(self):
        if self.replacement_name:
            return self.replacement_name

        return self._name

    def get_absolute_url(self):
        return reverse('catalogue:characteristic-edit', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Crawler Product Characteristic Name')
        verbose_name_plural = _("Crawler Product Characteristic Names")


class ManufacturerCar(CatalogueBaseModel):
    name = models.CharField(_('Model'), max_length=150, unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Car manufacturer')
        verbose_name_plural = _('Car manufacturers')
        ordering = ['name']


class ModelCar(CatalogueBaseModel):
    name = models.CharField(_('Model'), max_length=150, db_index=True)
    manufacturer = models.ForeignKey('ManufacturerCar', on_delete=models.CASCADE, verbose_name=_("Manufacturer"))

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'manufacturer')
        verbose_name = _('Car model')
        verbose_name_plural = _('Car models')


class Car(CatalogueBaseModel):
    model = models.ForeignKey('ModelCar', on_delete=models.CASCADE, verbose_name=_("Model"))
    type = models.CharField(_('Type'), max_length=150, db_index=True)
    construction = models.CharField(_('Construction'), max_length=150, blank=True, null=True)
    volume_cm = models.PositiveSmallIntegerField(_('Volume cm'), blank=True, null=True)
    power_kwt = models.PositiveSmallIntegerField(_('Power kwt'), blank=True, null=True)
    power_hp = models.PositiveSmallIntegerField(_('Power hp'), blank=True, null=True)
    some_key = models.PositiveBigIntegerField(_('Some key'), blank=True, null=True)
    key = models.CharField(_('Key'), max_length=40, blank=True, null=True)

    parts = models.ManyToManyField('CrawlerProductInfo', related_name='cars', verbose_name=_('Parts'))

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = _('Car')
        verbose_name_plural = _('Cars')
        unique_together = ('model', 'type')

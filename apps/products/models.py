# -*- coding: utf-8 -*-
import os, datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User

from pytils.translit import translify
from django.core.urlresolvers import reverse

from sorl.thumbnail import ImageField
from mptt.models import MPTTModel, TreeForeignKey, TreeManager

from apps.utils.managers import PublishedManager
from apps.utils.utils import moneyfmt

def file_path_Category(instance, filename):
    return os.path.join('images','category',  translify(filename).replace(' ', '_') )

def file_path_Product(instance, filename):
    return os.path.join('images','products',  translify(filename).replace(' ', '_') )

class Category(MPTTModel):
    parent = TreeForeignKey('self', verbose_name=u'Категория', related_name='children', blank=True, null=True, on_delete=models.SET_NULL)
    title = models.CharField(verbose_name=u'Название', max_length=100)
    slug = models.CharField(verbose_name=u'Алиас', max_length=100, unique=True)
    image = ImageField(verbose_name=u'Иконка', upload_to=file_path_Category, blank=True)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_footer_menu = models.BooleanField(verbose_name = u'Отображать в меню', help_text=u'внизу страницы', default=False)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    objects = TreeManager()

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name =_(u'category')
        verbose_name_plural =_(u'categories')
        ordering = ['-order', 'title']

    class MPTTMeta:
        order_insertion_by = ['order']

    def get_absolute_url(self):
        if self.parent:
            parent_slug = self.parent.slug
            return reverse('sub_category_detail', kwargs={'slug': '%s' % parent_slug, 'sub_slug': '%s' % self.slug})
        else:
            return reverse('category_detail', kwargs={'slug': '%s' % self.slug})

    def get_children(self):
        return self.children.filter(is_published=True).select_related()

    def get_descend(self):
        return self.get_descendants(include_self=False)

    def get_bread_product(self):
        if self.is_child_node():
            abs_bread = u'<a href="%s">%s</a> / <a href="%s">%s</a>' % (self.parent.get_absolute_url(), self.parent.title, self.get_absolute_url(), self.title)
            return u'%s' % abs_bread
        else:
            return u' <a href="%s">%s</a>' % (self.get_absolute_url(), self.title)

    def get_products(self):
        if self.get_children():
            # развернем для данной все дочерние категории
            descend_ids = self.get_descend().values('id')
            if descend_ids:
                products = Product.objects.filter(is_published=True, category__id__in=descend_ids)
            else:
                products = Product.objects.filter(title="1").filter(title="2")
            return products
        else:
            return self.product_set.published()

class Product(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'Категория', blank=True, null=True)
    title = models.CharField(verbose_name=u'Название', max_length=400)
    art = models.CharField(verbose_name=u'артикул', max_length=50, blank=True)
    price = models.DecimalField(verbose_name=u'Цена', decimal_places=2, max_digits=10, blank=True, null=True)
    description = models.TextField(verbose_name=u'Описание', blank=True)
    image = ImageField(verbose_name=u'Картинка', upload_to=file_path_Product, blank=False)
    video_code = models.TextField(verbose_name=u'Код видеоролика', help_text=u'короткая или полная ссылка на видео с Youtube', blank=True)

    is_new = models.BooleanField(verbose_name = u'Новинка', default=False)
    is_recomended = models.BooleanField(verbose_name = u'отображать в блоке "Рекомендуем"', default=False)
    sale_value = models.CharField(verbose_name=u'Скидка', max_length=50, blank=True)

    xml_id = models.IntegerField(verbose_name=u'Идентификатор из xml файла', blank=True, null=True)
    remainder = models.DecimalField(verbose_name=u'Остаток из xml файла', decimal_places=2, max_digits=10, blank=True, null=True)

    related_products = models.ManyToManyField("self", verbose_name=u'Похожие товары', blank=True, null=True,)

    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    class Meta:
        verbose_name =_(u'product_item')
        verbose_name_plural =_(u'product_items')
        ordering = ['-id',]

    def __unicode__(self):
        return u'%s. Артикул: %s' % (self.title,self.art)

    def get_absolute_url(self):
        return reverse('product_detail',kwargs={'pk': '%s'%self.id})

    def get_str_price(self):
        return moneyfmt(self.price)

    def get_photos(self):
        return self.photo_set.all()

    def get_related_products(self):
        return self.related_products.published()

    def get_feature_values(self):
        return self.featurevalue_set.all()

    def get_short_url(self):
        return u'%s/'% (self.id)

class Photo(models.Model):
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    image = ImageField(verbose_name=u'Картинка', upload_to=file_path_Product)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)

    class Meta:
        verbose_name =_(u'product_photo')
        verbose_name_plural =_(u'product_photos')
        ordering = ['-order',]

    def __unicode__(self):
        return u'Фото товара %s' %self.product.title

class FeatureName(models.Model):
    title = models.CharField(verbose_name=u'название', max_length=400)

    # Managers
    objects = PublishedManager()

    class Meta:
        verbose_name = _(u'featurename_item')
        verbose_name_plural = _(u'featurename_items')

    def __unicode__(self):
        return self.title

class FeatureValue(models.Model):
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    feature_name = models.ForeignKey(FeatureName, verbose_name=u'название характеристики', )
    value = models.CharField(verbose_name=u'значение', max_length=500)
    order = models.IntegerField(verbose_name=u'Порядок сортировки', default=10)

    class Meta:
        verbose_name = _(u'featurevalue_item')
        verbose_name_plural = _(u'featurevalue_items')
        ordering = ['-order', ]

    def __unicode__(self):
        return self.value

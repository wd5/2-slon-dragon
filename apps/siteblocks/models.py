# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
import datetime
import os
from pytils.translit import translify
from django.db.models.signals import post_save
from apps.utils.managers import PublishedManager
from mptt.models import MPTTModel, TreeForeignKey, TreeManager

type_choices = (
    (u'input',u'input'),
    (u'textarea',u'textarea'),
    (u'redactor',u'redactor'),
)

class Settings(models.Model):
    title = models.CharField(
        verbose_name = u'Название',
        max_length = 150,
    )
    name = models.CharField( 
        verbose_name = u'Служебное имя',
        max_length = 250,
    )
    value = models.TextField(
        verbose_name = u'Значение'
    )
    type = models.CharField(
        max_length=20,
        verbose_name=u'Тип значения',
        choices=type_choices
    )
    class Meta:
        verbose_name =_(u'site_setting')
        verbose_name_plural =_(u'site_settings')

    def __unicode__(self):
        return u'%s' % self.name

'''def image_path(self, instance, filename):
    filename = translify(filename).replace(' ', '_')
    return os.path.join('uploads', 'images/menu', filename)

class SiteMenu(MPTTModel):
    title = models.CharField(
        max_length = 150,
        verbose_name = u'Название'
    )
    image = models.ImageField(
        verbose_name=u'Иконка',
        upload_to = image_path,
        blank = True,
        null = True,
    )
    parent = TreeForeignKey(
        'self',
        verbose_name = u'Родительский раздел',
        related_name = 'children',
        blank = True,
        null = True,
    )
    url = models.CharField(
        verbose_name = u'url',
        max_length = 150,
    )
    order = models.IntegerField(
        verbose_name = u'Порядок сортировки',
        default = 10,
        help_text = u'чем больше число, тем выше располагается элемент'
    )
    is_published = models.BooleanField(
        verbose_name=u'Опубликовано',
        default=True,
    )

    objects = TreeManager()

    class Meta:
        verbose_name =_(u'menu_item')
        verbose_name_plural =_(u'menu_items')
        ordering = ['-order']

    class MPTTMeta:
        order_insertion_by = ['order']

    def __unicode__(self):
        return self.title

def strip_url_title(sender, instance, created, **kwargs):
    # remove the first and the last space
    instance.title = instance.title.strip()
    instance.url = instance.url.strip()
    instance.save()

post_save.connect(strip_url_title, sender=SiteMenu)'''

# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django import forms
from apps.utils.widgets import Redactor
from sorl.thumbnail.admin import AdminImageMixin
from mptt.admin import MPTTModelAdmin


from models import *


class CategoryAdminForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Category.objects.filter(parent=None), label='Родительская Категория', required=False)

    class Meta:
        model = Category

    class Media:
        js = (
            '/media/js/jquery.js',
            '/media/js/clientadmin.js',
            '/media/js/jquery.synctranslit.js',
            )

class CategoryAdmin(AdminImageMixin, MPTTModelAdmin):
    list_display = ('id','title','slug','order','is_published',)
    list_display_links = ('id','title',)
    list_editable = ('order','is_published',)
    list_filter = ('parent',)
    form = CategoryAdminForm

admin.site.register(Category, CategoryAdmin)


class FeatureValueInline(admin.TabularInline):
    model = FeatureValue
    extra = 0

class PhotoInline(AdminImageMixin, admin.TabularInline):
    model = Photo

class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(widget=Redactor(attrs={'cols': 110, 'rows': 20}), label=u'Описание', required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(is_published=True).exclude(parent=None),
        label=u'Категория', required=True)

    class Meta:
        model = Product
#--Виджеты jquery Редактора
class ProductAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id','title', 'category','price','art', 'order','is_published',)
    list_display_links = ('id','title',)
    list_editable = ('order','is_published',)
    list_filter = ('is_published','category','is_new','is_recomended',)
    search_fields = ('title', 'description', 'art',)
    filter_horizontal = ('related_products',)
    inlines = [PhotoInline, FeatureValueInline]
    form = ProductAdminForm

admin.site.register(Product, ProductAdmin)

class FeatureNameAdmin(admin.ModelAdmin):
    list_display = ('id','title',)
    list_display_links = ('id','title',)

admin.site.register(FeatureName, FeatureNameAdmin)

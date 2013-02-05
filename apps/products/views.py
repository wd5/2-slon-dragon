# -*- coding: utf-8 -*-
import os,md5
from datetime import datetime, date, timedelta
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.views.generic.simple import direct_to_template

from django.views.generic import ListView, DetailView, DetailView


from models import Category, Product

class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'products/product_detail.html'
    queryset = Product.objects.published()

product_detail = ProductDetail.as_view()

class CategoryDetail(DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'products/category_detail.html'
    queryset = Category.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super(CategoryDetail, self).get_context_data()

        slug = self.kwargs.get('slug', None)
        sub_slug = self.kwargs.get('sub_slug', None)

        all_categories = Category.objects.filter(is_published=True)
        category = False
        if slug or sub_slug:
            if slug == 'all':
                category = False
                context['catalog'] = Product.objects.published()
            else:
                if sub_slug and not category:
                    try:
                        category = all_categories.filter(slug=sub_slug)
                    except:
                        pass
                if slug and not category:
                    try:
                        category = all_categories.filter(slug=slug)
                    except:
                        pass
        else:
            category = False

        if category and category.count() == 1:
            category = category[0]
        elif category and category.count() > 1: # если по slug'у будет найдено несколько категорий
            try:
                category = category.get(parent__slug__in=[slug, sub_slug])
            except:
                category = False

        if category:
            context['parent_category'] = category.get_root()
            context['category'] = category
            products = category.get_products()[:6]
            context['category_products'] = products
        else:
            context['category'] = False
        return context
category_detail = CategoryDetail.as_view()

class NewList(ListView):
    model = Product
    context_object_name = 'new_products'
    template_name = 'products/new_list.html'
    queryset = Product.objects.filter(is_published=True, is_new=True)

new_list = NewList.as_view()

class SaleList(ListView):
    model = Product
    context_object_name = 'sale_products'
    template_name = 'products/sale_list.html'
    queryset = Product.objects.filter(is_published=True).exclude(sale_value=u'')

sale_list = SaleList.as_view()
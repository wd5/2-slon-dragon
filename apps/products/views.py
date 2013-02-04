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


class Products(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'products/product_list.html'
    queryset = Product.items.all()


class ProductsSearch(Products):
    context_object_name = 'products'
    template_name = 'products/product_search_list.html'

    def get_queryset(self):
        request = self.request
        if 'q' in request.GET:
            q = request.GET['q']
        else:
            return HttpResponseRedirect('/')
        if not q:
            return HttpResponseRedirect('/')
        qs = super(ProductsSearch, self).get_queryset().filter(
            Q(name__icontains=q)|
            Q(description__icontains=q)|
            Q(full_description__icontains=q)
        )
        return qs

search_view = ProductsSearch.as_view()


class ProductDetail(DetailView):
    model = Product
    context_object_name = Product
    template_name = 'products/product_detail.html'
    queryset = Product.items.all()

    def get_context_data(self, **kwargs):
        context = super(ProductDetail,self).get_context_data()
        context['photos'] = self.object.get_photos()
        return context

product_view = ProductDetail.as_view()
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import url, patterns, include
from views import *
from django.views.generic.simple import redirect_to


urlpatterns = patterns('',
    #url(r'^search/$',search_view, name='products_search'),
    url(r'^$', redirect_to,  {'url': '/'}),
    url(r'^sale/$', sale_list, name='sale_list'),
    url(r'^new/$', new_list, name='new_list'),
    url(r'^product/(?P<pk>\d+)/$', product_detail, name='product_detail'),
    url(r'^(?P<slug>[^/]+)/$', category_detail, name='category_detail'),
    url(r'^(?P<slug>[^/]+)/(?P<sub_slug>[^/]+)/$', category_detail, name='sub_category_detail'),



)

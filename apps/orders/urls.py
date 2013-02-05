# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('apps.orders.views',
    url(r'^$','view_cart',name='cart'),
    (r'^show_order_form/$','show_order_form'),
    (r'^order_form_step2/$','show_finish_form'),

    # AJAX
    (r'^refresh_cart/$','refresh_cart'),
    (r'^add_product_to_cart/$','add_product_to_cart'),
    (r'^delete_product_from_cart/$','delete_product_from_cart'),
    (r'^restore_product_to_cart/$','restore_product_to_cart'),
    (r'^change_cart_product_count/$','change_cart_product_count'),

    (r'^ems_calculate/$','ems_calculate'),

)

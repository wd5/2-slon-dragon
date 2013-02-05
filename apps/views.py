# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from apps.orders.models import Order, OrderProduct
from apps.products.models import Product



class IndexView(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super(IndexView,self).get_context_data(**kwargs)
        context['recomended_products'] = Product.objects.filter(is_published=True, is_recomended=True)
        last_orders = Order.objects.all()[:3]
        order_ids = [x['id'] for x in last_orders.values('id')]
        product_ids = OrderProduct.objects.filter(order__id__in=order_ids).values('product')
        context['recently_buyed_products'] = Product.objects.filter(id__in=product_ids)
        return context

index = IndexView.as_view()
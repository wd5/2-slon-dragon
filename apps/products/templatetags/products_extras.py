# -*- coding: utf-8 -*-
from django import template
from apps.products.models import *

register = template.Library()

@register.inclusion_tag("products/block_category_menu.html")
def block_category_menu(curr):
    if curr.startswith('/'):
        curr = curr[1:]
    if curr.endswith('/'):
        curr = curr[:-1]
    try:
        current_category = curr.split('/')[1]
    except:
        current_category = False
    menu = Category.objects.filter(parent=None, is_published=True)
    return {'menu': menu, 'current_category': current_category}

@register.inclusion_tag("products/block_footer_menu.html")
def block_footer_menu():
    menu = Category.objects.filter(is_footer_menu=True)
    return {'menu': menu}
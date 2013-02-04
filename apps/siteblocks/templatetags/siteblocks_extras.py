# -*- coding: utf-8 -*-
from decimal import Decimal
from apps.siteblocks.models import Settings
from apps.products.models import Category
from django import template
from apps.utils.utils import moneyfmt

register = template.Library()

@register.inclusion_tag("siteblocks/block_footer_menu.html")
def block_footer_menu():
    menu = Category.objects.filter(is_footer_menu=True)
    return {'menu': menu}


@register.filter
def money_fmt(value):
    value = Decimal(value)
    return moneyfmt(value)

money_fmt.is_safe = True

#def get_active_menu(url, site_menu):
#
#    request_path = url
#
#    for i, menu_item in enumerate(site_menu):
#        setattr(site_menu[i], 'is_active', False)
#        #if request_path.startswith(menu_item.path):
#            #site_menu[i].is_active = True
#
#
#    for i, menu_item in enumerate(site_menu):
#        setattr(site_menu[i], 'is_active', False)
#        if not menu_item.parent:
#            for menu_subitem in site_menu:
#                # highlight parent menu item
#                if menu_subitem.parent == menu_item and menu_subitem.is_active:
#                    site_menu[i].is_active = True
#        elif menu_item.is_active:
#            for menu_subitem in site_menu:
#                # remove redundant sibling highlight
#                if menu_subitem.parent \
#                     and menu_subitem.parent.path == menu_item.parent.path \
#                     and menu_subitem.path.startswith(menu_item.path) \
#                     and len(menu_subitem.path) > len(menu_item.path) \
#                     and menu_subitem.is_active:
#                        site_menu[i].is_active = False
#    return site_menu

#@register.inclusion_tag("siteblocks/block_setting.html")
#def block_static(name):
#    try:
#        setting = Settings.objects.get(name = name)
#    except Settings.DoesNotExist:
#        setting = False
#    return {'block': block,}

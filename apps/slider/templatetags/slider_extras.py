# -*- coding: utf-8 -*-
from apps.slider.models import Photo
from django import template

register = template.Library()

@register.inclusion_tag("slider/block_slider.html")
def block_slider():
    slider_items = Photo.objects.published()
    return {'slider_items': slider_items}
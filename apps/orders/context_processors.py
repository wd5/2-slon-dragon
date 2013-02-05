# -*- coding: utf-8 -*-
from apps.orders.models import EmsCity
from apps.siteblocks.models import Settings
from settings import SITE_NAME

def order_context_proc(request):
    try:
        selfcarting_text = Settings.objects.get(name='selfcarting_text').value
    except:
        selfcarting_text  = False
    try:
        express_text = Settings.objects.get(name='express_text').value
    except:
        express_text  = False
    try:
        express_price = Settings.objects.get(name='express_price').value
    except:
        express_price  = False
    ems_cities = EmsCity.objects.all()


    return {
        'selfcarting_text': selfcarting_text,
        'express_text': express_text,
        'express_price': express_price,
        'ems_cities': ems_cities,
    }
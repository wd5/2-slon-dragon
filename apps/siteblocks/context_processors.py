# -*- coding: utf-8 -*-
from apps.siteblocks.models import Settings
from settings import SITE_NAME

def settings(request):
    try:
        contacts = Settings.objects.get(name='contacts').value
    except Settings.DoesNotExist:
        contacts = False
    try:
        return_text = Settings.objects.get(name='return_text').value
    except Settings.DoesNotExist:
        return_text = False
    try:
        payment_text = Settings.objects.get(name='payment_text').value
    except Settings.DoesNotExist:
        payment_text = False
    try:
        delivery_text = Settings.objects.get(name='delivery_text').value
    except Settings.DoesNotExist:
        delivery_text = False
    try:
        workemail = Settings.objects.get(name='workemail').value
    except Settings.DoesNotExist:
        workemail = False
    try:
        phonenum = Settings.objects.get(name='phonenum').value
    except Settings.DoesNotExist:
        phonenum = False

    return {
        'phonenum': phonenum,
        'workemail': workemail,
        'contacts': contacts,
        'delivery_text': delivery_text,
        'payment_text': payment_text,
        'return_text': return_text,
        'site_name': SITE_NAME,
    }
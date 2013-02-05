# -*- coding: utf-8 -*-
import os, datetime, md5
from django import http
from django.conf import settings
from django.views.generic.simple import direct_to_template
from pytils.translit import translify
from django.views.decorators.csrf import csrf_exempt

try:
    from PIL import Image
except ImportError:
    import Image
from django.contrib.auth.decorators import login_required
from apps.utils.utils import crop_image
from django.db.models import get_model
from decimal import Decimal
from urllib2 import urlopen
from pytils.translit import slugify
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from xml.dom.minidom import *
from apps.products.models import Category, Product, FeatureValue

def handle_uploaded_file(f, filename, folder):
    name, ext = os.path.splitext(translify(filename).replace(' ', '_'))
    hashed_name = md5.md5(name + datetime.datetime.now().strftime("%Y%m%d%H%M%S")).hexdigest()
    path_name = settings.MEDIA_ROOT + '/uploads/' + folder + hashed_name + ext
    destination = open(path_name, 'wb+')

    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return '/media/uploads/' + folder + hashed_name + ext


@csrf_exempt
def upload_img(request):
    if request.user.is_staff:
        if request.method == 'POST':
            url = handle_uploaded_file(request.FILES['file'], request.FILES['file'].name, 'images/')

            #Resizing
            size = 650, 650
            im = Image.open(settings.ROOT_PATH + url)
            imageSize = im.size
            if (imageSize[0] > size[0]) or  (imageSize[1] > size[1]):
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(settings.ROOT_PATH + url, "JPEG", quality=100)
            return http.HttpResponse('{"filelink":"%s"}' % url)

        else:
            return http.HttpResponse('error')
    else:
        return http.HttpResponse('403 Forbidden. Authentication Required!')


@csrf_exempt
def upload_file(request):
    if request.user.is_staff:
        if request.method == 'POST':
            url = handle_uploaded_file(request.FILES['file'], request.FILES['file'].name, 'files/')
            url = '{"filelink":"%s","filename":"%s"}' % (url, request.FILES['file'].name)
            return http.HttpResponse(url)
    else:
        return http.HttpResponse('403 Forbidden. Authentication Required!')


@login_required()
@csrf_exempt
def crop_image_view(request, app_name, model_name, id):
    model = get_model(app_name, model_name)
    output_size = model.crop_size
    if request.method != "POST":
        try:
            image = model.objects.get(pk=id).image
            return direct_to_template(request, 'admin/crop_image.html', locals())
        except model.DoesNotExist:
            raise http.Http404('Object not found')
    else:
        original_img = model.objects.get(pk=id)
        crop_image(request.POST, original_img, output_size)

    next = request.path.replace('crop/', '')
    return http.HttpResponseRedirect(next)


def upload_xml(request):
    if request.user.is_staff:
        if request.method == 'POST':
            f = request.FILES['file']
            filename = request.FILES['file'].name
            name, ext = os.path.splitext(translify(filename).replace(' ', '_'))
            newname = '/uploads/' + 'xml_tmp' + ext
            if ext == '.xsql' or ext == '.xml':
                # удаляем старый файл
                oldfile = 'xml_tmp'
                for root, dirs, files in os.walk(settings.MEDIA_ROOT + '/uploads/', ):
                    for filename in files:
                        name, ext = os.path.splitext(translify(u'%s' % filename).replace(' ', '_'))
                        if name == 'xml_tmp':
                            oldfile = '/uploads/' + filename
                try:
                    os.remove(settings.MEDIA_ROOT + oldfile)
                except OSError:
                    oldfile = False
                    # загружаем новый
                path_name = settings.MEDIA_ROOT + newname
                destination = open(path_name, 'wb+')
                for chunk in f.chunks():
                    destination.write(chunk)
                destination.close()

                # распарсиваем:
                f = parse(path_name)

                rows_array = f.getElementsByTagName('product')
                all_products = Product.objects.all()
                parsed = ''
                if rows_array: # если есть элемент ROW - то проверяем что пришло - товар или категория
                    for z in rows_array:
                        xml_code = z.getElementsByTagName('code')[0].firstChild.nodeValue
                        try:
                            xml_art = z.getElementsByTagName('art')[0].firstChild.nodeValue
                        except:
                            xml_art = u''
                        xml_title = z.getElementsByTagName('title')[0].firstChild.nodeValue
                        try:
                            xml_price = Decimal(z.getElementsByTagName('price')[0].firstChild.nodeValue)
                        except:
                            xml_price = 0
                        try:
                            xml_remainder = Decimal(z.getElementsByTagName('remainder')[0].firstChild.nodeValue)
                        except:
                            xml_remainder = 0

                        try:
                            change = False
                            product = all_products.get(xml_id=xml_code)
                            if product.art != xml_art:
                                product.art = xml_art
                                change = True
                            if product.title != xml_title:
                                product.title = xml_title
                                change = True
                            if product.price != xml_price:
                                product.price = xml_price
                                change = True
                            if product.remainder != xml_remainder:
                                product.remainder = xml_remainder
                                change = True
                            if change:
                                product.save()
                        except:
                            product = Product(title=xml_title, art=xml_art, price=xml_price, xml_id=xml_code,
                                remainder=xml_remainder)
                            product.save()

                    return http.HttpResponseRedirect('/admin/products/product/?')
                else:
                    return http.HttpResponseRedirect('/admin/')
            else:
                return http.HttpResponseRedirect('/admin/')
    else:
        return http.HttpResponse('403 Forbidden. Authentication Required!')
# -*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.mail.message import EmailMessage
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import FormView, TemplateView, View
from django.views.generic.detail import DetailView
from apps.orders.models import Cart, CartProduct, OrderProduct, Order, EmsCity
from apps.orders.forms import RegistrationOrderForm
from apps.products.models import Product
from apps.inheritanceUser.models import CustomUser
from apps.inheritanceUser.forms import RegistrationForm, AddressForm
from apps.siteblocks.models import Settings
from apps.siteblocks.context_processors import settings as settings_context_proc
from context_processors import order_context_proc
from pytils.numeral import choose_plural
import settings, urllib, json

# для кабинета - История заказов
class ShowOrderInfo(DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'users/show_order_info.html'

    def get_context_data(self, **kwargs):
        context = super(ShowOrderInfo, self).get_context_data()
        if self.request.user.is_authenticated and self.request.user.id:
            try:
                profile = CustomUser.objects.get(id=self.request.user.id)
            except:
                profile = False
            if profile:
                try:
                    loaded_count = int(Settings.objects.get(name='loaded_count').value)
                except:
                    loaded_count = 5
                queryset = profile.get_orders()
                result = GetLoadIds(queryset, loaded_count, True)
                splited_result = result.split('!')
                try:
                    remaining_count = int(splited_result[0])
                except:
                    remaining_count = False
                next_id_loaded_items = splited_result[1]
                context['loaded_count'] = remaining_count
                context['orders'] = profile.get_orders()[:loaded_count]
                context['next_id_loaded_items'] = next_id_loaded_items
        return context

show_order_info = ShowOrderInfo.as_view()

class ViewCart(TemplateView):
    template_name = 'orders/cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ViewCart, self).get_context_data()

        cookies = self.request.COOKIES

        cookies_cart_id = False
        if 'slondragon_cart_id' in cookies:
            cookies_cart_id = cookies['slondragon_cart_id']

        if self.request.user.is_authenticated and self.request.user.id:
            profile_id = self.request.user.id
        else:
            profile_id = False

        sessionid = self.request.session.session_key

        try:
            if profile_id:
                cart = Cart.objects.get(profile=profile_id)
            elif cookies_cart_id:
                cart = Cart.objects.get(id=cookies_cart_id)
            else:
                cart = Cart.objects.get(sessionid=sessionid)
            cart_id = cart.id
        except Cart.DoesNotExist:
            cart = False
            cart_id = False

        is_empty = True
        if cart:
            cart_products = cart.get_products_all()
        else:
            cart_products = []

        cart_str_total = u''
        if cart_products:
            is_empty = False
            cart_str_total = cart.get_str_total()

        context['cart_is_empty'] = is_empty
        context['cart_products'] = cart_products
        context['cart_str_total'] = cart_str_total
        context['cart_id'] = cart_id
        return context

view_cart = ViewCart.as_view()

class OrderFromView(FormView):
    form_class = RegistrationOrderForm
    template_name = 'orders/order_form.html'

    def post(self, request, *args, **kwargs):
        response = HttpResponse()
        cookies = self.request.COOKIES
        cookies_cart_id = False
        if 'slondragon_cart_id' in cookies:
            cookies_cart_id = cookies['slondragon_cart_id']

        if self.request.user.is_authenticated and self.request.user.id:
            profile_id = self.request.user.id
        else:
            profile_id = False

        if profile_id:
            try:
                profile = CustomUser.objects.get(pk=int(profile_id))
            except:
                profile = False
        else:
            profile = False

        sessionid = self.request.session.session_key

        try:
            if profile_id:
                cart = Cart.objects.get(profile=profile_id)
            elif cookies_cart_id:
                cart = Cart.objects.get(id=cookies_cart_id)
            else:
                cart = Cart.objects.get(sessionid=sessionid)
        except Cart.DoesNotExist:
            cart = False

        if not cart:
            return HttpResponseRedirect('/cart/')

        cart_products = cart.get_products()
        cart_products_count = cart_products.count()

        if not cart_products_count:
            return HttpResponseRedirect('/cart/')

        data = request.POST.copy()
        order_form = RegistrationOrderForm(data)
        if order_form.is_valid():
            new_order = order_form.save()
            new_order.total_price = cart.get_total()
            if new_order.order_carting == u'carting':
                try:
                    express_price = Settings.objects.get(name='express_price').value
                    new_order.total_price += Decimal(express_price)
                except:
                    pass
            elif new_order.order_carting == u'country':
                try:
                    ems_price = GetEmsPrice('', request.POST['ems_city'], cart.get_products_count())
                    if ems_price:
                        new_order.total_price += Decimal(ems_price)
                except:
                    pass
            new_order.save()

            for cart_product in cart_products:
                ord_prod = OrderProduct(
                    order=new_order,
                    count=cart_product.count,
                    product=cart_product.product,
                    product_price=cart_product.product.price
                )
                ord_prod.save()
            if profile:
                profile.phone = new_order.phone
                if not profile.email:
                    profile.email = new_order.email
                profile.save()

            cart.delete() #Очистка и удаление корзины
            response.delete_cookie('slondragon_cart_id') # todo: ???

            subject = u'Слон-Дракон - Информация по заказу.'
            subject = u''.join(subject.splitlines())
            message = render_to_string(
                'orders/message_template.html',
                    {
                    'order': new_order,
                    'products': new_order.get_products()
                }
            )

            try:
                emailto = Settings.objects.get(name='workemail').value
            except Settings.DoesNotExist:
                emailto = False

            if emailto and new_order.email:
                msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [emailto, new_order.email])
                msg.content_subtype = "html"
                msg.send()

            if not profile_id:
                reg_form = RegistrationForm(initial={'email': new_order.email, })
            else:
                reg_form = False

            context = {'order': new_order, 'request': request, 'user': request.user, 'reg_form': reg_form}
            context.update(csrf(request))
            context.update(order_context_proc(request))
            context.update(settings_context_proc(request))
            return render_to_response('orders/order_form_final.html', context)
        else:
            context = {'order_form': order_form, 'request': request, 'user': request.user,
                       'cart_total': cart.get_str_total()}
            context.update(csrf(request))
            context.update(order_context_proc(request))
            context.update(settings_context_proc(request))
            return render_to_response(self.template_name, context)

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(**kwargs)

        cookies = self.request.COOKIES
        cookies_cart_id = False
        if 'slondragon_cart_id' in cookies:
            cookies_cart_id = cookies['slondragon_cart_id']

        if self.request.user.is_authenticated and self.request.user.id:
            profile_id = self.request.user.id
        else:
            profile_id = False

        sessionid = self.request.session.session_key

        try:
            cart = Cart.objects.get(profile=profile_id)
        except Cart.DoesNotExist:
            try:
                if cookies_cart_id:
                    cart = Cart.objects.get(id=cookies_cart_id)
                else:
                    cart = Cart.objects.get(sessionid=sessionid)
            except:
                cart = False
        if cart:
            cart_total = cart.get_total()
            cart_total_str = cart.get_str_total()
            context['cart_total'] = cart_total_str

            if self.request.user.is_authenticated and self.request.user.id:
                try:
                    profile_set = CustomUser.objects.filter(id=self.request.user.id)
                    profile = CustomUser.objects.get(id=self.request.user.id)
                    form.fields['profile'].queryset = profile_set
                    form.fields['profile'].initial = profile
                    form.fields['first_name'].initial = self.request.user.first_name
                    form.fields['last_name'].initial = self.request.user.last_name
                    form.fields['email'].initial = self.request.user.email
                    form.fields['phone'].initial = profile.phone
                    form.fields['order_carting'].initial = u'country'
                    form.fields['order_payment'].initial = u'cash_on_delivery'
                    try:
                        address = profile.get_addresses()[:1].get()
                        form.fields['index'].initial = address.index
                        form.fields['city'].initial = address.city
                        form.fields['street'].initial = address.street
                        form.fields['house_no'].initial = address.house_no
                        form.fields['apartment'].initial = address.apartment
                        form.fields['note'].initial = address.note
                    except:
                        pass
                except CustomUser.DoesNotExist:
                    return HttpResponseBadRequest()
            else:
                form.fields['profile'].queryset = CustomUser.objects.extra(where=['1=0'])
                form.fields['order_carting'].initial = u'country'
                form.fields['order_payment'].initial = u'cash_on_delivery'
            context['order_form'] = form
        else:
            return HttpResponseRedirect('/')
        context.update(csrf(request))
        context.update(order_context_proc(request))
        context.update(settings_context_proc(request))
        return self.render_to_response(context)

show_order_form = csrf_protect(OrderFromView.as_view())

show_finish_form = csrf_protect(OrderFromView.as_view())

# AJAX

class RefreshCartView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        else:
            try:
                cart_type = request.POST['type']
            except:
                return HttpResponseBadRequest()

            cookies = request.COOKIES
            response = HttpResponse()

            cookies_cart_id = False
            if 'slondragon_cart_id' in cookies:
                cookies_cart_id = cookies['slondragon_cart_id']

            if request.user.is_authenticated and request.user.id:
                profile_id = request.user.id
            else:
                profile_id = False

            sessionid = request.session.session_key

            if profile_id:
                try:
                    cart = Cart.objects.get(profile=profile_id)
                except Cart.DoesNotExist:
                    if cookies_cart_id:
                        try:
                            cart = Cart.objects.get(id=cookies_cart_id)
                            if cart.profile:
                                cart = False
                            else:
                                try:
                                    profile = CustomUser.objects.get(pk=int(profile_id))
                                except:
                                    profile = False
                                if profile:
                                    cart.profile = profile
                                    cart.save()
                        except:
                            cart = False
                    else:
                        cart = False
            elif cookies_cart_id:
                try:
                    cart = Cart.objects.get(id=cookies_cart_id)
                except Cart.DoesNotExist:
                    cart = False
            else:
                try:
                    cart = Cart.objects.get(sessionid=sessionid)
                except Cart.DoesNotExist:
                    cart = False

            is_empty = True
            cart_total = 0
            cart_products_count = 0
            cart_products_text = u''
            if cart:
                cart_products_count = cart.get_products_count()
                if cart_products_count:
                    cart_total = cart.get_str_total()
                    is_empty = False
                    cart_products_text = u'товар%s' % (choose_plural(cart_products_count, (u'', u'а', u'ов')))

            cart_html = render_to_string(
                'orders/block_cart.html',
                    {
                    'is_empty': is_empty,
                    'type': cart_type,
                    'cart': cart,
                    'cart_products_count': cart_products_count,
                    'cart_total': cart_total,
                    'cart_products_text': cart_products_text,
                    }
            )
            response.content = cart_html
            return response

refresh_cart = csrf_exempt(RefreshCartView.as_view())

class AddProductToCartView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'product_id' not in request.POST:
                return HttpResponseBadRequest()

            try:
                product = Product.objects.get(id=int(request.POST['product_id']))
            except:
                return HttpResponseBadRequest()

            cookies = request.COOKIES
            response = HttpResponse()

            cookies_cart_id = False
            if 'slondragon_cart_id' in cookies:
                cookies_cart_id = cookies['slondragon_cart_id']

            if request.user.is_authenticated and request.user.id:
                profile_id = request.user.id
                try:
                    profile = CustomUser.objects.get(pk=int(profile_id))
                except:
                    profile = False
            else:
                profile_id = False
                profile = False

            sessionid = request.session.session_key

            if profile_id:
                try:
                    cart = Cart.objects.get(profile__id=profile_id)
                except Cart.DoesNotExist:
                    if cookies_cart_id:
                        try:
                            cart = Cart.objects.get(id=cookies_cart_id)
                            if cart.profile:
                                if profile:
                                    cart = Cart.objects.create(profile=profile)
                                else:
                                    return HttpResponseBadRequest()
                            else:
                                if profile:
                                    cart.profile = profile
                                    cart.save()
                                else:
                                    return HttpResponseBadRequest()
                        except:
                            if profile:
                                cart = Cart.objects.create(profile=profile)
                            else:
                                return HttpResponseBadRequest()
                    else:
                        cart = Cart.objects.create(profile=profile)
                response.set_cookie('slondragon_cart_id', cart.id, 1209600)
                #if cookies_cart_id: response.delete_cookie('cart_id')
            elif cookies_cart_id:
                try:
                    cart = Cart.objects.get(id=cookies_cart_id)
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(sessionid=sessionid)
                response.set_cookie('slondragon_cart_id', cart.id, 1209600)
            else:
                try:
                    cart = Cart.objects.get(sessionid=sessionid)
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(sessionid=sessionid)
                response.set_cookie('slondragon_cart_id', cart.id, 1209600)
            try:
                cart_product = CartProduct.objects.get(
                    cart=cart,
                    product=product,
                )
                if cart_product.is_deleted:
                    cart_product.is_deleted = False
                else:
                    cart_product.count += 1
                cart_product.save()
            except CartProduct.DoesNotExist:
                CartProduct.objects.create(
                    cart=cart,
                    product=product,
                )
            return HttpResponse('sucess')

add_product_to_cart = csrf_exempt(AddProductToCartView.as_view())

class DeleteProductFromCart(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'cart_product_id' not in request.POST:
                return HttpResponseBadRequest()

            try:
                cart_product = CartProduct.objects.get(id=int(request.POST['cart_product_id']))
            except CartProduct.DoesNotExist:
                return HttpResponseBadRequest()

            cart_product.is_deleted = True
            cart_product.save()
            return HttpResponse('success')

delete_product_from_cart = csrf_exempt(DeleteProductFromCart.as_view())

class RestoreProductToCart(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'cart_product_id' not in request.POST:
                return HttpResponseBadRequest()
            else:
                cart_product_id = request.POST['cart_product_id']
                try:
                    cart_product_id = int(cart_product_id)
                except ValueError:
                    return HttpResponseBadRequest()

            try:
                cart_product = CartProduct.objects.get(id=cart_product_id)
            except CartProduct.DoesNotExist:
                return HttpResponseBadRequest()

            cart_product.is_deleted = False
            cart_product.save()
            return HttpResponse('success')

restore_product_to_cart = csrf_exempt(RestoreProductToCart.as_view())

class ChangeCartCountView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'cart_product_id' not in request.POST or 'new_count' not in request.POST:
                return HttpResponseBadRequest()

            cart_product_id = request.POST['cart_product_id']
            try:
                cart_product_id = int(cart_product_id)
            except ValueError:
                return HttpResponseBadRequest()

            new_count = request.POST['new_count']
            try:
                new_count = int(new_count)
            except ValueError:
                return HttpResponseBadRequest()

            try:
                cart_product = CartProduct.objects.get(id=cart_product_id)
            except CartProduct.DoesNotExist:
                return HttpResponseBadRequest()

            cart_product.count = new_count
            cart_product.save()
            return HttpResponse('success')

change_cart_product_count = csrf_exempt(ChangeCartCountView.as_view())

class EmsCalculateView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'city' not in request.POST:
                return HttpResponseBadRequest()

            city = request.POST['city']

            if city == '':
                return HttpResponseBadRequest()

            cookies = request.COOKIES
            cookies_cart_id = False
            if 'slondragon_cart_id' in cookies:
                cookies_cart_id = cookies['slondragon_cart_id']

            if self.request.user.is_authenticated and self.request.user.id:
                profile_id = self.request.user.id
            else:
                profile_id = False

            sessionid = self.request.session.session_key

            try:
                if profile_id:
                    cart = Cart.objects.get(profile=profile_id)
                elif cookies_cart_id:
                    cart = Cart.objects.get(id=cookies_cart_id)
                else:
                    cart = Cart.objects.get(sessionid=sessionid)
            except Cart.DoesNotExist:
                cart = False

            if cart:
                ems_price = GetEmsPrice(city, False, cart.get_products_count())
                if ems_price:
                    return HttpResponse(ems_price)
                else: # не нашли город или ошибка
                    return HttpResponse('NotFound')
            else:
                return HttpResponseBadRequest()

ems_calculate = csrf_exempt(EmsCalculateView.as_view())

def GetEmsPrice(city, city_code, weight):
    try:
        if city_code:
            pass
        else:
            ems_city = EmsCity.objects.get(name__iexact=city)
            city_code = ems_city.value # из москвы!
        carting_price_data = urllib.urlopen(
            'http://emspost.ru/api/rest?method=ems.calculate&from=city--moskva&to=%s&weight=%s' % (
                city_code, weight))
        json_data = json.load(carting_price_data)
        return json_data["rsp"]["price"]
    except:
        return False



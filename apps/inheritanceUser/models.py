# -*- coding: utf-8 -*-
import datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User, UserManager

class CustomUserManager(UserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given username, e-mail and password.
        """
        now = datetime.datetime.now()

        # Normalize the address by lowercasing the domain part of the email
        # address.
        if email:
            try:
                email_name, domain_part = email.strip().split('@', 1)
            except ValueError:
                pass
            else:
                email = '@'.join([email_name, domain_part.lower()])
        else:
            email = ''

        user = self.model(username=username, email=email, is_staff=False,
                         is_active=True, is_superuser=False, last_login=now,
                         date_joined=now)

        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(User):
    """User with app settings."""
    #third_name = models.CharField(max_length=20, verbose_name=u'отчество', blank=True)
    phone = models.CharField(max_length=20, verbose_name=u'телефон', blank=True)
    discount_card_number = models.CharField(max_length=100, verbose_name=u'номер дисконтной карты', blank=True)
    is_receive_mailer = models.BooleanField(verbose_name = u'получать рассылку на этот e-mail', default=False)


    # Use UserManager to get the create_user method, etc.
    objects = CustomUserManager()

    class Meta:
        verbose_name = u'пользователь'
        verbose_name_plural = u'пользователи'

    def get_addresses(self):
        return self.customuseraddress_set.order_by('city')

    def get_orders(self):
        return self.order_set.all()

    def get_name(self):
        return '%s %s' %(self.first_name, self.last_name)

class CustomUserAddress(models.Model):
    user =  models.ForeignKey(User, verbose_name=u'пользователь')
    index = models.CharField(max_length=50, verbose_name=u'индекс', blank=True)
    city = models.CharField(max_length=50, verbose_name=u'город', blank=True)
    street = models.CharField(max_length=70, verbose_name=u'улица', blank=True)
    house_no = models.CharField(max_length=70, verbose_name=u'дом', blank=True)
    apartment = models.CharField(max_length=20, verbose_name=u'квартира', blank=True)
    note = models.CharField(max_length=255, verbose_name=u'примечание', blank=True)

    class Meta:
        verbose_name =_(u'profile_addres')
        verbose_name_plural =_(u'profile_addreses')

    def __unicode__(self):
        return u'%s %s' % (self.city, self.street)

class DiscountCard(models.Model):
    number = models.CharField(max_length=50, verbose_name=u'индекс', blank=False)

    class Meta:
        verbose_name =_(u'discount_card')
        verbose_name_plural =_(u'discount_cards')

    def __unicode__(self):
        return u'%s' % self.number




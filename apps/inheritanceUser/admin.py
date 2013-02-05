# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from apps.inheritanceUser.models import CustomUser, CustomUserAddress, DiscountCard
#admin.site.unregister(User)

class UserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser

class AddressInlines(admin.TabularInline):
    model = CustomUserAddress

class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    fieldsets = (
            (None, {'fields': ('username', 'password')}),
            (_('Personal info'), {'fields': ('email', 'last_name','first_name', 'phone', 'discount_card_number', 'is_receive_mailer')}),
            (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
            (_('Groups'), {'fields': ('groups',)}),
        )
    list_display = ('id', 'username', 'email', 'is_staff','is_superuser', 'is_active')
    list_display_links = ('id', 'username', )
    list_filter = ('is_staff','is_superuser', 'is_active')
    search_fields = ('username', 'last_name','first_name','third_name', 'email',)
    inlines = [AddressInlines,]

admin.site.register(CustomUser, CustomUserAdmin)

class DiscountCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'number',)
    list_display_links = ('id','number')
    #list_editable = ('number',)

admin.site.register(DiscountCard, DiscountCardAdmin)
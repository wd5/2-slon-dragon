# -*- coding: utf-8 -*-
from django import forms
from apps.orders.models import Order

class RegistrationOrderForm(forms.ModelForm):
    note = forms.CharField(
        widget=forms.Textarea(),
        required=False
    )

    class Meta:
        model = Order
        exclude = ('create_date',)

    def clean(self):
        cleaned_data = super(RegistrationOrderForm, self).clean()
        order_carting = cleaned_data.get("order_carting")
        apartment = cleaned_data.get("apartment")
        house_no = cleaned_data.get("house_no")
        street = cleaned_data.get("street")
        index = cleaned_data.get("index")

        if order_carting == 'country' and (street=='' and index=='' and house_no=='' and apartment==''):
            raise forms.ValidationError("Обязательное поле.")

        return cleaned_data
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from utils.clean_phone_number import clean_phone_number

from .models import Propagation, RequestPandham, InventoryTransaction

class RequestPandhamForm(forms.ModelForm):
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        return clean_phone_number(phone_number)

    class Meta:
        model = RequestPandham
        shipping_address = forms.CharField(
            required=True,
            widget=forms.Textarea,
            help_text=_("Enter the shipping address and receiver contact number.")
        )
        fields = [
            "book_inventory",
            "accept_terms",
            "name",
            "recipient_category",
            "phone_number",
            "shipping_address",
        ]
        labels = {
            "book_inventory": "หนังสือ",
            "accept_terms": "ยอมรับเงื่อนไขการรับหนังสือ",
            "name": "ชื่อ นามสกุล หรือ ฉายา (พระภิกษุ)",
            "recipient_category": "กลุ่ม",
            "phone_number": "หมายเลขโทรศัพท์",
            "shipping_address": "ที่อยู่ในการจัดส่ง",
        }
        widgets = {
            "book_inventory": forms.HiddenInput(),
            "accept_terms": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "recipient_category": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "shipping_address": forms.Textarea(attrs={"class": "form-control"}),
        }


class ContributeForm(forms.ModelForm):
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        return clean_phone_number(phone_number)

    def __init__(self, *args, **kwargs):
        # เอาค่า min และ max contribute ออกจาก kwargs
        min_contribute_value = kwargs.pop('min_contribute_value', 500)
        max_contribute_value = kwargs.pop('max_contribute_value', 500)
        step_contribute_value = kwargs.pop('step_contribute_value', 500)
        # เอาค่า max no_of_book ออกจาก kwargs
        max_number_of_book_value = kwargs.pop('max_number_of_book_value', 500)

        super().__init__(*args, **kwargs)
        # ตั้งค่า attributes ของวิดเจ็ต amount_contributed โดยใช้ค่า min_value และ max_value
        self.fields['amount_contributed'].widget = forms.NumberInput(attrs={
            "class": "form-range", "type": "range",
            "min": str(min_contribute_value), "max": str(max_contribute_value), "step": str(step_contribute_value)
        })
        self.fields['number_of_books'].widget = forms.NumberInput(attrs={
            "class": "form-range", "type": "range",
            "min": 1, "max": str(max_number_of_book_value), "step": 1
        })

    class Meta:
        model = Propagation
        fields = [
            "book_inventory",
            "amount_contributed",
            "number_of_books",
            "donate_books",
            "target_groups",
            "name",
            "phone_number",
            "shipping_address",
        ]
        labels = {
            "book_inventory": "หนังสือ",
            "amount_contributed": "จำนวนเงินสมทบทุนการพิมพ์",
            "number_of_books": "จำนวนหนังสือที่ร่วมสมทบทุน",
            "donate_books": "จำนวนหนังสือที่ร่วมปันธรรม",
            "target_groups": "กลุ่มเป้าหมาย",
            "name": "ชื่อ นามแฝง หรือคำอุทิศ",
            "phone_number":"หมายเลขโทรศัพท์มือถือ",
            "shipping_address": "ที่อยู่ในการจัดส่ง",
        }
        widgets = {
            "book_inventory": forms.HiddenInput(),
            "amount_contributed": forms.NumberInput(attrs={"class": "form-range", "type": "range", "min": "0", "max": "100", "step": "1"}),
            "number_of_books": forms.NumberInput(attrs={"class": "form-range", "type": "range", "min": "0", "max": "100", "step": "1"}),
            "donate_books": forms.NumberInput(attrs={"class": "form-control"}),
            "target_groups": forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "shipping_address": forms.Textarea(attrs={"class": "form-control"}),
        }


class VerifyOTPForm(forms.ModelForm):
    class Meta:
        model = Propagation
        fields = [
            "otp",
        ]
        labels = {
            "otp": _("OTP"),
        }
        widgets = {
            "otp": forms.TextInput(attrs={"class": "form-control"}),
        }




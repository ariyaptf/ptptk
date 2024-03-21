from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

class PhoneNumberWidget(TextInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        # ใช้ super().render เพื่อรับ HTML ของ TextInput
        input_html = super().render(name, value, attrs)
        # กำหนด URL ที่คุณต้องการให้คำขอหากต้องการส่ง OTP ไปยัง
        otp_send_url = "/pandham/send-otp/"
        # HTML สำหรับปุ่ม OTP ที่ใช้ HTMX
        button_html = '<button type="button" hx-get="{}" hx-target="#otp-status" hx-trigger="click" class="btn btn-info btn-send-otp ms-2">{}</button>'.format(otp_send_url, _("Send OTP"))
        # รวม HTML และทำให้เป็น safe string เพื่อไม่ให้ Django escape HTML
        return mark_safe(f'<div class="input-group">{input_html}<div class="input-group-append">{button_html}</div></div>')

import datetime
import os
import pyotp
import requests

from django import forms
from django.db import models
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, FormView

from wagtail.models import Page
from coderedcms.models import ReusableContent

from formtools.wizard.views import SessionWizardView
from dotenv import load_dotenv

from .forms import RequestPandhamForm, ContributeForm, VerifyOTPForm
from .models import (
    BookInventory, PandhamStock, Propagation,
    InventoryTransaction, PandhamTargetGroup, RequestPandham)

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv("API_KEY")
client_id = os.getenv("CLIENT_ID")
send_sms_url = os.getenv("SEND_SMS_URL")


# =============================
# คลาส OtpService
# สำหรับการสร้างและส่ง OTP
# =============================
class OtpService:
    def __init__(self, request):
        self.request = request

    def generate_and_send_otp(self, phone_number):
        totp = pyotp.TOTP(pyotp.random_base32(), interval=180)
        otp = totp.now()
        self.request.session['otp_secret_key'] = totp.secret  # Save the OTP in the session
        valid_date = datetime.datetime.now() + datetime.timedelta(minutes=3)  # Save the OTP valid date in the session
        self.request.session['otp_valid_date'] = str(valid_date)

        message = """รหัส OTP : {otp} กรุณากรอกลงฟอร์มภายใน 3 นาที
        อนุโมทนาครับ/ค่ะ
        """.format(otp=otp)

        url = send_sms_url
        params = {
            "SenderId": "PTF",
            "Is_Unicode": "true",
            "Is_Flash": "false",
            "Message": message,
            "MobileNumbers": phone_number,
            "apiKey": api_key,
            "clientId": client_id
        }
        response = requests.get(url, params=params)
        print(response.json())

    def verify_otp(self, otp_entered):
        otp_secret_key = self.request.session.get('otp_secret_key')
        otp_valid_date = self.request.session.get('otp_valid_date')
        if otp_secret_key and otp_valid_date is not None:
            valid_date = datetime.datetime.fromisoformat(otp_valid_date)

            if valid_date > datetime.datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=180)
                if totp.verify(otp_entered):
                    return True
        return False

    def clear_otp(self):
        if 'otp_secret_key' in self.request.session:
            del self.request.session['otp_secret_key']
        if 'otp_valid_date' in self.request.session:
            del self.request.session['otp_valid_date']


# =============================
# ฟังก์ชัน ResendOTP
# สำหรับการส่ง OTP ใหม่
# =============================
def ResendOTP(request):
    phone_number = request.GET.get('phone_number', None)

    if phone_number:
        # สมมติว่าคุณมี logic สำหรับสร้างและส่ง OTP ที่นี่
        otp_service = OtpService(request)
        otp_service.clear_otp()
        otp_service.generate_and_send_otp(phone_number)
        return JsonResponse({'status': 'success', 'message': 'OTP sent successfully.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Phone number is required.'})


# =============================
# ฟังก์ชัน RequestPandhamView
# สำหรับการกรอกข้อมูลเพื่อขอปันธรรม
# =============================
class RequestPandhamView(FormView):
    template_name = 'pandham/request-pandham.html'
    form_class = RequestPandhamForm
    success_url = reverse_lazy('request_pandham_verify_otp')

    def get_initial(self):
        initial = super().get_initial()
        book_inventory = self.kwargs.get('book_id')
        if book_inventory:
            initial['book_inventory'] = book_inventory
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # สมมติว่า book_id มาจาก URL kwargs หรือ initial data
        book_id = self.kwargs.get('book_id') or self.get_initial().get('book_inventory')
        context['book'] = ''
        context['current_stock'] = 0
        if book_id:
            # ดึงข้อมูล book จากฐานข้อมูล
            book = get_object_or_404(BookInventory, pk=book_id)
            # เพิ่ม book object เข้าไปใน context
            context['book'] = book

            inventory_current_stock = book.current_stock
            pandham = PandhamStock.objects.filter(book_inventory=book).first()
            if pandham:
                pandham_current_stock = pandham.current_stock
            else:
                pandham_current_stock = 0
            # เพิ่ม current_stock เข้าไปใน context
            context['inventory_stock'] = inventory_current_stock
            context['pandham_stock'] = pandham_current_stock
            # เพิ่ม current_stock เข้าไปใน session
            self.request.session['pandham_stock'] = pandham_current_stock

        return context

    def form_valid(self, form):
        # Process the form data here
        # You can access the form data using form.cleaned_data
        # For example, form.cleaned_data['field_name']
        form_cleaned_data = form.cleaned_data
        book_inventory = form_cleaned_data.get('book_inventory')
        phone_number = form_cleaned_data.get('phone_number')
        shipping_address = form_cleaned_data.get('shipping_address')
        # Save the form data in the session
        form_data = {
            "book_inventory": book_inventory.id if book_inventory else None,
            "name": form_cleaned_data.get('name'),
            "phone_number": phone_number,
            "shipping_address": shipping_address,
        }

        requested = RequestPandham.objects.filter(
            phone_number=phone_number,
            book_inventory=book_inventory,
        ).first()

        waiting_list = RequestPandham.objects.filter(
            phone_number=phone_number,
            book_inventory=book_inventory,
            is_waiting=True
        ).first()

        if requested or waiting_list:
            if waiting_list:
                message = "คุณได้ขอรับหนังสือปันธรรมเล่มนี้แล้ว อยู่ในรายการรอการจัดส่ง"
            else:
                message = "คุณได้ขอรับหนังสือปันธรรมเล่มนี้แล้ว"
            context = self.get_context_data()
            context.update({
                'result': message,
                'ref': requested or waiting_list
            })
            return render(self.request, self.template_name, context)

        self.request.session['form_data'] = form_data
        otp_service = OtpService(self.request)
        otp_service.generate_and_send_otp(form_data['phone_number'])
        return HttpResponseRedirect(self.get_success_url())


# =============================
# ฟังก์ชัน RequestPandhamVerifyOTPView
# สำหรับการ Verify OTP หลังจาก submit form และส่ง OTP แล้ว
# =============================
class RequestPandhamVerifyOTPView(FormView):
    template_name = 'pandham/request-pandham-verify-otp.html'
    form_class = VerifyOTPForm
    success_url = reverse_lazy('request_pandham_success')

    def get(self, request, *args, **kwargs):
        # ตรวจสอบว่ามี 'form_data' ใน session หรือไม่
        if 'form_data' not in request.session:
            # หากไม่พบ, redirect ไปยังหน้า pandham
            page = Page.objects.get(slug='pandham')
            return redirect(page.url)
        # หากมี 'form_data' ใน session, ดำเนินการตามปกติ
        return super().get(request, *args, **kwargs)

    def get_success_url(self, request_pandham_id=None):
        return reverse('request_pandham_success', args=[request_pandham_id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phone_number'] = self.request.session['form_data']['phone_number']
        return context

    # ฟังก์ชันสำหรับสร้าง RequestPandham
    def create_request_pandham(self, form_data, otp_entered):
        pandham_stock = self.request.session.get('pandham_stock', False)
        request_pandham = RequestPandham.objects.create(
            book_inventory_id=form_data.get('book_inventory'),
            number_of_books=1,
            recipient_category_id=1,  # ใช้ recipient_category_id สำหรับการกำหนดค่าด้วย id ของ recipient_category
            name=form_data.get('name'),
            phone_number=form_data.get('phone_number'),
            otp=otp_entered,
            shipping_address=form_data.get('shipping_address'),
            is_waiting=not pandham_stock,
        )
        request_pandham.save()
        return request_pandham

    def form_valid(self, form):
        otp_entered = form.cleaned_data.get('otp')
        otp_secret_key = self.request.session.get('otp_secret_key')
        otp_valid_date = self.request.session.get('otp_valid_date')
        if otp_secret_key and otp_valid_date is not None:
            valid_date = datetime.datetime.fromisoformat(otp_valid_date)

            if valid_date > datetime.datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=180)
                if totp.verify(otp_entered):
                    # อัปเดต form_data ใน session ด้วยค่า OTP ที่ได้รับ
                    form_data = self.request.session.get('form_data', {})
                    request_pandham = self.create_request_pandham(form_data, otp_entered)

                    # ลบ 'form_data' และ 'pandham_stock' ออกจาก session
                    self.request.session.pop('form_data', None)

                    # ลบ OTP ออกจาก session
                    otp_service = OtpService(self.request)
                    otp_service.clear_otp()

                    return redirect(self.get_success_url(request_pandham.id))
                else:
                    form.add_error('otp', "รหัส OTP ไม่ถูกต้อง")
            else:
                form.add_error('otp', "รหัส OTP หมดอายุ")
        else:
            form.add_error('otp', "พบปัญหาการยืนยัน OTP, ติดต่อเจ้าหน้าที่")

        # ในกรณีที่มี error ไม่ควรส่งต่อไปยัง success_url ให้ใช้ super().form_valid(form) ให้ใช้ self.form_invalid(form)
        return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


# =============================
# ฟังก์ชัน RequestPandhamSuccessView
# สำหรับการประมวลผลและแสดงข้อความหลังจากทำการขอปันธรรมสำเร็จ
# =============================
class RequestPandhamSuccessView(TemplateView):
    template_name = 'pandham/request-pandham-success.html'

    def get_context_data(self, **kwargs):
        # ให้นำค่า request_pandham_id ที่ได้จาก args มาใช้สำหรับการดึงข้อมูล RequestPandham จากฐานข้อมูล
        # และนำข้อมูลนั้นมาใส่ใน context แล้วส่งต่อไปยัง template
        context = super().get_context_data(**kwargs)
        request_pandham_id = kwargs.get('request_pandham_id')
        request_pandham = get_object_or_404(RequestPandham, pk=request_pandham_id)
        context['request_pandham'] = request_pandham

        # reusable content
        request_pandham_success_message = ReusableContent.objects.filter(name='request_pandham_success_message').first()
        if request_pandham_success_message:
            context['request_pandham_success_message'] = request_pandham_success_message

        return context


# =============================
# ฟังก์ชัน ContributePandhamView
# สำหรับการสมทบทุนการพิมพ์หนังสือ และรับหนังสือหรือปันธรรม
# =============================
class ContributePandhamView(FormView):
    template_name = 'pandham/contribute-pandham.html'
    form_class = ContributeForm
    success_url = reverse_lazy('contribute_pandham_verify_otp')

    def get_initial(self):
        initial = super().get_initial()
        book_inventory = self.kwargs.get('book_id')
        if book_inventory:
            initial['book_inventory'] = book_inventory
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # สมมติว่า book_id มาจาก URL kwargs หรือ initial data
        book_id = self.kwargs.get('book_id') or self.get_initial().get('book_inventory')
        context['book_name'] = ''
        context['current_stock'] = 0
        context['price'] = 0
        if book_id:
            # ดึงข้อมูล book จากฐานข้อมูล
            book = get_object_or_404(BookInventory, pk=book_id)
            # เพิ่ม book object เข้าไปใน context
            context['book_name'] = book.book_name
            context['current_stock'] = book.current_stock
            context['price'] = book.price

        return context
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # ดึงข้อมูล book_id จาก URL kwargs หรือ initial data
        book_id = self.kwargs.get('book_id') or self.request.GET.get('book_inventory')

        if book_id:
            # ดึงข้อมูล book จากฐานข้อมูล
            book = get_object_or_404(BookInventory, pk=book_id)
            kwargs['min_contribute_value'] = book.price
            kwargs['max_contribute_value'] = book.current_stock * book.price
            kwargs['step_contribute_value'] = book.price
            kwargs['max_number_of_book_value'] = book.current_stock
        else:
            # ตั้งค่า max_value เป็นค่าเริ่มต้นหากไม่มี book_id
            kwargs['min_contribute_value'] = 500  # หรือค่าเริ่มต้นอื่นที่เหมาะสม
            kwargs['max_contribute_value'] = 500
            kwargs['step_contribute_value'] = 500
            kwargs['max_number_of_book_value'] = 10

        return kwargs

    def form_valid(self, form):
        # Process the form data here
        # You can access the form data using form.cleaned_data
        # For example, form.cleaned_data['field_name']
        form_cleaned_data = form.cleaned_data
        # แปลง QuerySet ของ target_groups เป็น list ของ ID
        target_groups_ids = list(form_cleaned_data.get('target_groups').values_list('id', flat=True))

        # Save the form data in the session
        form_data = {
            "book_inventory": form_cleaned_data.get('book_inventory').id if form_cleaned_data.get('book_inventory') else None,
            "amount_contributed": int(form_cleaned_data.get('amount_contributed')),
            "number_of_books": form_cleaned_data.get('number_of_books'),
            "receive_books": form_cleaned_data.get('receive_books'),
            "donate_books": form_cleaned_data.get('donate_books'),
            "target_groups": target_groups_ids,  # บันทึก list ของ ID แทน
            "name": form_cleaned_data.get('name'),
            "phone_number": form_cleaned_data.get('phone_number'),
            "shipping_address": form_cleaned_data.get('shipping_address'),
        }

        self.request.session['form_data'] = form_data
        otp_service = OtpService(self.request)
        otp_service.generate_and_send_otp(form_data['phone_number'])
        return HttpResponseRedirect(self.get_success_url())


# =============================
# ฟังก์ชัน ContributePandhamVerifyOTPView
# สำหรับการ Verify OTP หลังจาก submit form และส่ง OTP แล้ว
# =============================
class ContributePandhamVerifyOTPView(FormView):
    template_name = 'pandham/contribute-pandham-verify-otp.html'
    form_class = VerifyOTPForm
    success_url = reverse_lazy('contribute_pandham_success')

    def get(self, request, *args, **kwargs):
        # ตรวจสอบว่ามี 'form_data' ใน session หรือไม่
        if 'form_data' not in request.session:
            # หากไม่พบ, redirect ไปยังหน้า pandham
            page = Page.objects.get(slug='pandham')
            return redirect(page.url)
        # หากมี 'form_data' ใน session, ดำเนินการตามปกติ
        return super().get(request, *args, **kwargs)


    def get_success_url(self, propagation_id=None):
        return reverse('contribute_pandham_success', args=[propagation_id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phone_number'] = self.request.session['form_data']['phone_number']
        return context

    def create_propagation(self, form_data, otp_entered):
        propagation = Propagation.objects.create(
            book_inventory_id=form_data.get('book_inventory'),
            amount_contributed=form_data.get('amount_contributed'),
            number_of_books=form_data.get('number_of_books'),
            receive_books=form_data.get('number_of_books') - form_data.get('donate_books'),
            donate_books=form_data.get('donate_books'),
            name=form_data.get('name'),
            phone_number=form_data.get('phone_number'),
            otp=otp_entered,
            shipping_address=form_data.get('shipping_address')
        )
        target_group_ids = form_data.get('target_groups', [])
        if target_group_ids:
            target_groups = PandhamTargetGroup.objects.filter(id__in=target_group_ids)
            propagation.target_groups.set(target_groups)
        propagation.save()
        return propagation

    def form_valid(self, form):
        # ตรวจสอบค่า OTP ที่กรอกเข้ามา
        otp_entered = form.cleaned_data.get('otp')
        # เปิด session และดึงค่า OTP secret key และ valid date ออกมา
        otp_secret_key = self.request.session.get('otp_secret_key')
        otp_valid_date = self.request.session.get('otp_valid_date')

        if otp_secret_key and otp_valid_date is not None:
            valid_date = datetime.datetime.fromisoformat(otp_valid_date)
            # ตรวจสอบว่า OTP ยังใช้งานได้อยู่หรือไม่
            if valid_date > datetime.datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=180)
                # ตรวจสอบค่า OTP ที่กรอกเข้ามา
                if totp.verify(otp_entered):
                    # เปิด session และดึงค่า form_data ออกมา
                    form_data = self.request.session.get('form_data', {})
                    propagation = self.create_propagation(form_data, otp_entered)
                    self.request.session['propagation_id'] = propagation.id

                    # ลบ 'form_data' ออกจาก session
                    del self.request.session['form_data']

                    # ลบ OTP ออกจาก session
                    otp_service = OtpService(self.request)
                    otp_service.clear_otp()

                    return redirect(self.get_success_url(propagation.id))
                else:
                    form.add_error('otp', "รหัส OTP ไม่ถูกต้อง")
            else:
                form.add_error('otp', "รหัส OTP หมดอายุ")
        else:
            form.add_error('otp', "พบปัญหาการยืนยัน OTP, ติดต่อเจ้าหน้าที่")

        # ในกรณีที่มี error ไม่ควรส่งต่อไปยัง success_url ให้ใช้ super().form_valid(form) ให้ใช้ self.form_invalid(form)
        return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


# =============================
# ฟังก์ชัน ContributePandhamSuccessView
# สำหรับแสดงข้อความหลังจากทำการสมทบทุนสำเร็จ
# =============================
class ContributePandhamSuccessView(TemplateView):
    template_name = 'pandham/contribute-pandham-success.html'

    def get_context_data(self, **kwargs):
        # ให้นำค่า propagation_id ที่ได้จาก args มาใช้สำหรับการดึงข้อมูล Propagation จากฐานข้อมูล
        # และนำข้อมูลนั้นมาใส่ใน context แล้วส่งต่อไปยัง template
        context = super().get_context_data(**kwargs)
        propagation_id = kwargs.get('propagation_id')
        propagation = get_object_or_404(Propagation, pk=propagation_id)
        context['propagation'] = propagation

        # reusable content
        contribution_anumodhana_message = ReusableContent.objects.filter(name='contribution_anumodhana_message').first()
        if contribution_anumodhana_message:
            context['contribution_anumodhana_message'] = contribution_anumodhana_message
        ptf_saving_account = ReusableContent.objects.filter(name='ptf_saving_account').first()
        if ptf_saving_account:
            context['ptf_saving_account'] = ptf_saving_account

        return context



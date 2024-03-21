from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel
from wagtail.images.models import Image

from coderedcms.fields import CoderedStreamField
from coderedcms.blocks import LAYOUT_STREAMBLOCKS

from datetime import datetime


# ====================================
# กลุ่มเป้าหมาย
# ====================================
class PandhamTargetGroup(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Group Name")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True
    )
    priority = models.IntegerField(
        default=0,
        verbose_name=_("Priority")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Target Group")
        verbose_name_plural = _("Target Groups")
        ordering = ['priority', 'name']


# ====================================
# เป้าหมาย (ผู้รับมอบหนังสือปันธรรม)
# ====================================
class PandhamTarget(models.Model):
    pandham_target_group = models.ForeignKey(
        PandhamTargetGroup,
        on_delete=models.CASCADE,
        verbose_name=_("Target Group"),
        related_name="targets"
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name")
    )
    address = models.TextField(
        verbose_name=_("Address")
    )
    requested_books = models.PositiveIntegerField(
        verbose_name=_("Requested Books")
    )
    request_date = models.DateTimeField(
        verbose_name=_("Request Date")
    )
    additional_info = models.TextField(
        verbose_name=_("Additional Information"),
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.group.name}"

    class Meta:
        verbose_name = _("Target")
        verbose_name_plural = _("Targets")


# ====================================
# คลังหนังสือหลัก
# ====================================
class BookInventory(models.Model):
    book_name = models.CharField(
        max_length=255,
        verbose_name="ชื่อหนังสือ",
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="รายละเอียดย่อ",
    )
    cover_image = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True,
        related_name="book_cover",
        verbose_name="ปกหนังสือ",
    )
    description = CoderedStreamField(
        LAYOUT_STREAMBLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name="รายละเอียดเพิ่มเติม",
    )
    prerequisites = CoderedStreamField(
        LAYOUT_STREAMBLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name="คุณสมบัติ",
        help_text="คุณสมบัติเบื้องต้นของผู้สนใจศึกษาที่ควรมีก่อนอ่านหนังสือเล่มนี้"
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="ราคา",
    )
    initial_stock = models.IntegerField(
        default=0,
        verbose_name="จำนวนหนังสือเริ่มต้น",
    )
    minimum_stock_level = models.IntegerField(
        default=0,
        verbose_name="ระดับสต็อกขั้นต่ำ",
    )
    current_stock = models.IntegerField(
        default=0,
        verbose_name="จำนวนหนังสือคงเหลือ",
    )
    sequence_order = models.PositiveIntegerField(
        default=0,
        verbose_name="ลำดับ",
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="พร้อมใช้งาน"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory"
        ordering = ['sequence_order', 'book_name']

    panels = [
        FieldPanel('sequence_order'),
        FieldPanel('book_name'),
        FieldPanel('short_description'),
        FieldPanel('cover_image'),
        FieldPanel('description'),
        FieldPanel('prerequisites'),
        FieldPanel('price'),
        FieldPanel('initial_stock'),
        FieldPanel('minimum_stock_level'),
        FieldPanel('current_stock'),
        FieldPanel('is_available'),
    ]

    def __str__(self):
        return self.book_name


# ====================================
# คลังหนังสือปันธรรม
# ====================================
class PandhamStock(models.Model):
    book_inventory = models.OneToOneField(
        BookInventory,
        on_delete=models.CASCADE,
        verbose_name="หนังสือ",
        related_name="stock"
    )
    initial_stock = models.IntegerField(
        default=0,
        verbose_name="จำนวนหนังสือเริ่มต้น",
    )
    current_stock = models.IntegerField(
        default=0,
        verbose_name="จำนวนหนังสือคงเหลือ",
    )

    panels = [
        FieldPanel('book_inventory'),
        FieldPanel('initial_stock'),
        FieldPanel('current_stock'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Padham Stock"
        verbose_name_plural = "Padham Stock"

    def __str__(self):
        return self.book_inventory.book_name


# ====================================
# รายการปรับปรุงหนังสือ
# ====================================
class InventoryTransaction(models.Model):
    TRANSACTION_CHOICES = [
        ('in', "นำเข้าคลัง"),
        ('pandham', "เพิ่มคลังปันธรรม"),
        ('support', "สนับสนุนการพิมพ์"),
        ('request', "ขอรับปันธรรม"),
        ('donate', "ปันธรรมโดยมูลนิธิฯ"),
        ('adjustment', "ปรับปรุงยอด"),
    ]
    book_inventory = models.ForeignKey(
        BookInventory,
        on_delete=models.CASCADE,
        verbose_name="หนังสือ",
        related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=255,
        choices=TRANSACTION_CHOICES,
        verbose_name="ประเภทธุรกรรม"
    )
    quantity = models.IntegerField(
        verbose_name="จำนวน",
    )
    details = models.TextField(
        blank=True,
        verbose_name="รายละเอียด",
        help_text="ระบุรายละเอียดเฉพาะเกี่ยวกับธุรกรรมนี้"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.quantity} - {self.book_inventory.book_name}"

    def clean(self):
        if self.transaction_type in ['pandham', 'support', 'donate']:
            if not self.book_inventory or self.quantity > self.book_inventory.current_stock:
                raise ValidationError({
                    'quantity': _('มีหนังสือไม่เพียงพอในคลังหลัก')
                })

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.transaction_type == 'in' or self.transaction_type == 'adjustment':
            # สำหรับ 'in' เพิ่มสต็อก, สำหรับ 'adjustment' สามารถเป็นการเพิ่มหรือลดขึ้นอยู่กับค่า quantity
            self.book_inventory.current_stock += self.quantity

        elif self.transaction_type in ['pandham', 'support', 'donate']:
            # ลดสต็อกสำหรับ 'pandham', 'support', 'donate'
            self.book_inventory.current_stock -= self.quantity
            # สำหรับ 'pandham'ให้เพิ่มเข้าสต็อกปันธรรม
            if self.transaction_type == 'pandham':
                pandham_stock, created = PandhamStock.objects.get_or_create(book_inventory=self.book_inventory, defaults={'current_stock': 0})
                pandham_stock.current_stock += self.quantity
                pandham_stock.save()

        elif self.transaction_type == 'request':
            pandham_stock = PandhamStock.objects.get(book_inventory=self.book_inventory)
            if self.quantity > pandham_stock.current_stock:
                raise ValidationError('มีหนังสือไม่เพียงพอในคลังปันธรรม')
            pandham_stock.current_stock -= self.quantity
            pandham_stock.save()

        self.book_inventory.save()
        super().save(*args, **kwargs)


# ====================================
# แบบฟอร์มสำหรับการสนับสนุนการพิมพ์
# ====================================
class Propagation(models.Model):
    # ตัวเลขอ้างอิง (Reference Number)
    reference_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="หมายเลขอ้างอิง",
        help_text="หมายเลขอ้างอิงสำหรับธุรกรรมนี้"
    )
    # หนังสือที่สนับสนุน
    book_inventory = models.ForeignKey(
        BookInventory,
        on_delete=models.CASCADE,
        verbose_name="หนังสือ",
        related_name="Propagation",
    )
    # จำนวนเงินที่สนับสนุน
    amount_contributed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="สมทบทุนการพิมพ์",
        help_text="ร่วมบริจาคเงินสนับสนุนกองทุนการพิมพ์หนังสือ"
    )
    # จำนวนหนังสือที่สนับสนุน
    number_of_books = models.PositiveIntegerField(
        default=0,
        verbose_name="จำนวน",
        help_text="จำนวนหนังสือที่ต้องการสนับสนุนการพิมพ์",
    )
    # สมทบทุนและรับหนังสือ
    receive_books = models.PositiveIntegerField(
        default=0,
        verbose_name="จำนวนเล่มที่ต้องการรับ",
    )
    # บริจาคเข้าคลังปันธรรม
    donate_books = models.PositiveIntegerField(
        default=0,
        verbose_name="จำนวนเล่มที่ต้องการปันธรรม",
        help_text="มอบหนังสือให้กับมูลนิธิฯ ช่วยจัดสรรแก่ผู้รับที่เหมาะสม"
    )
    target_groups = models.ManyToManyField(
        'PandhamTargetGroup',
        blank=True,
        verbose_name="กลุ่มเป้าหมาย",
    )
    # ปันธรรมหนังสือ
    requested = models.PositiveIntegerField(
        default=0,
        verbose_name="จำนวนเล่มที่ปันธรรมแล้ว",
    )
    # ชื่อ ที่อยู่ หมายเลขโทรศัพท์
    name = models.CharField(
        max_length=255,
        verbose_name="ชื่อ",
        default="ไม่ประสงค์ออกนาม",
        help_text="กรุณาระบุชื่อ ฉายา นามแฝง หรือคำอุทิศ"
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name="หมายเลขโทรศัพท์",
        help_text="หมายเลขโทรศัพท์ที่สามารถติดต่อได้ เช่น 0988888888 (ไม่เปิดเผยต่อสาธารณะ)"
    )
    otp = models.CharField(
        max_length=6,
        verbose_name="รหัส OTP",
        help_text="กรอกรหัส OTP"
    )
    shipping_address = models.TextField(
        null=True,
        verbose_name="ที่อยู่ในการจัดส่ง",
        help_text="กรอกที่อยู่ในการจัดส่ง และหมายเลขโทรศัพท์ติดต่อผู้รับ"
    )
    payment_notified = models.BooleanField(
        default=False,
        verbose_name="แจ้งชำระเงิน"
    )
    proof_of_payment = models.ImageField(
        upload_to='proof_of_payment',
        blank=True,
        null=True,
        verbose_name="หลักฐานการชำระเงิน",
        help_text="อัปโหลดหลักฐานการชำระเงิน",
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name="บันทึกหรือโน้ต",
        help_text="บันทึกหรือโน้ตสำหรับธุรกรรมนี้"
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name="ดำเนินการเสร็จสิ้น"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Propagation"
        verbose_name_plural = "Propagation"

    def __str__(self):
        return f"{self.reference_number} {self.name} {self.book_inventory.book_name}"


    def save(self, *args, **kwargs):
        # สร้างตัวเลขอ้างอิง (Reference Number)
        if self.reference_number == '':
            self.reference_number = f"PROP{datetime.now().strftime('%Y%m%d%H%M%S')}"

        if self._state.adding:
            if self.receive_books > 0:
                try:
                    InventoryTransaction.objects.create(
                        book_inventory=self.book_inventory,
                        transaction_type='support',
                        quantity=self.receive_books,
                        details='support propagation : ' + self.reference_number,
                    )
                except Exception as e:
                    print(f"Failed to create InventoryTransaction: {e}")

            if self.donate_books > 0:
                try:
                    InventoryTransaction.objects.create(
                        book_inventory=self.book_inventory,
                        transaction_type='pandham',
                        quantity=self.donate_books,
                        details='donate propagation : ' + self.reference_number,
                    )
                except Exception as e:
                    print(f"Failed to create InventoryTransaction: {e}")

        super().save(*args, **kwargs)

# ====================================
# แบบฟอร์มสำหรับการขอรับปันธรรม
# ====================================
class RequestPandham(models.Model):
    # ตัวเลขอ้างอิง (Reference Number)
    reference_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="หมายเลขอ้างอิง",
        help_text="หมายเลขอ้างอิงสำหรับธุรกรรมนี้"
    )
    # หนังสือที่ขอรับปันธรรม
    book_inventory = models.ForeignKey(
        BookInventory,
        on_delete=models.CASCADE,
        verbose_name="หนังสือ",
        related_name="request_propagation",
    )
    # จำนวนหนังสือที่ขอรับปันธรรม
    number_of_books = models.PositiveIntegerField(
        default=1,
        verbose_name="จำนวน",
    )
    # กลุ่มเป้าหมาย
    recipient_category = models.ForeignKey(
        'PandhamTargetGroup',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="กลุ่ม",
        help_text="กรุณาระบุกลุ่มหรือองค์กรของคุณ"
    )
    # ชื่อ นามสกุล หรือ ฉายา (พระภิกษุ)
    name = models.CharField(
        max_length=255,
        verbose_name="ชื่อ นามสกุล หรือ ฉายา (พระภิกษุ)",
    )
    # หมายเลขโทรศัพท์
    phone_number = models.CharField(
        max_length=20,
        verbose_name="หมายเลขโทรศัพท์",
        help_text="หมายเลขโทรศัพท์ที่สามารถติดต่อได้ เช่น 0988888888 (ไม่เปิดเผยต่อสาธารณะ)"
    )
    # ที่อยู่ในการจัดส่ง
    shipping_address = models.TextField(
        null=True,
        verbose_name="ที่อยู่ในการจัดส่ง",
        help_text="กรอกที่อยู่ในการจัดส่งและหมายเลขติดต่อของผู้รับ"
    )
    # รหัส OTP
    otp = models.CharField(
        max_length=6,
        verbose_name="รหัส OTP",
        help_text="กรอกรหัส OTP"
    )
    # ข้อตกลงการรับปันธรรม
    accept_terms = models.BooleanField(
        verbose_name="ยอมรับเงื่อนไขการรับหนังสือ",
    )
    # อ้างอิงรายการสนับสนุนการพิมพ์
    propagation = models.ForeignKey(
        Propagation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="อ้างอิง",
        related_name="request_propagation",
        help_text="อ้างอิงรายการสนับสนุนการพิมพ์"
    )
    # รอปันธรรม
    is_waiting = models.BooleanField(
        default=False,
        verbose_name="รอปันธรรม"
    )
    # เสร็จสิ้น
    is_completed = models.BooleanField(
        default=False,
        verbose_name="เสร็จสิ้น"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Request Pandham")
        verbose_name_plural = _("Request Pandham")

    def __str__(self):
        return f"{self.reference_number} {self.name} {self.book_inventory.book_name}"

    def clean(self):
        if not self.accept_terms:
            raise ValidationError({
                'accept_terms': "กรุณายอมรับเงื่อนไขการรับหนังสือ"
            })

    def save(self, *args, **kwargs):
        # สร้างตัวเลขอ้างอิง (Reference Number)
        if self.reference_number == '':
            self.reference_number = f"REQP{datetime.now().strftime('%Y%m%d%H%M%S')}"

        def set_waiting_status():
            self.propagation = None
            self.is_waiting = True
            self.is_completed = False

        # ถ้ามีหนังสืออยู่ในคลังหนังสือปันธรรมให้ทำรายการ InventoryTransaction transaction_type=request
        # เงื่อนไขในโค้ดนี้มีสองส่วน:
        # self._state.adding and not self.is_waiting:
            # หมายความว่า ถ้าเป็นการสร้าง instance ใหม่และ is_waiting ไม่เป็น True (หรือเป็น False)
        # not self._state.adding and self.__class__.objects.get(id=self.id).is_waiting and not self.is_waiting:
            # หมายความว่า ถ้าไม่ใช่การสร้าง instance ใหม่ (หรือ instance นี้มีอยู่แล้ว)
            # และ is_waiting ถูกเปลี่ยนจาก True เป็น False
        # ถ้าเงื่อนไขใดเงื่อนไขหนึ่งเป็น True, โค้ดที่อยู่ในบล็อก if จะถูกดำเนินการ.

        if (self._state.adding and not self.is_waiting) or (not self._state.adding and self.__class__.objects.get(id=self.id).is_waiting and not self.is_waiting):
            # ตรวจสอบว่ามีหนังสืออยู่ในคลังหนังสือปันธรรมหรือไม่
            pandham_stock = PandhamStock.objects.get(book_inventory=self.book_inventory)
            still_in_pandham_stock = pandham_stock.current_stock >= self.number_of_books
            # ถ้ามีหนังสืออยู่ในคลังหนังสือปันธรรมให้ทำรายการ InventoryTransaction transaction_type=request
            if still_in_pandham_stock:
                # ตรวจสอบว่า recipient_category นั้นสอดคล้องข้อใดข้อหนึ่งกับรายการ target_group ใน Propagation หรือไม่
                recipient_category = self.recipient_category
                if recipient_category:
                    propagation = None
                    propagations = Propagation.objects.filter(
                        book_inventory=self.book_inventory,
                        target_groups__id=recipient_category.id
                    )
                    if propagations.exists():
                        for each_propagation in propagations:
                            if each_propagation.requested < each_propagation.donate_books:
                                propagation = each_propagation
                                break
                        if propagation:
                            propagation.requested += self.number_of_books
                            propagation.save()
                            self.propagation = propagation

                            # ทำรายการ InventoryTransaction transaction_type=request
                            try:
                                new_inv = InventoryTransaction.objects.create(
                                    book_inventory=self.book_inventory,
                                    transaction_type='request',
                                    quantity=self.number_of_books,
                                    details='request pandham : ' + self.reference_number,
                                )
                                new_inv.details='request pandham : ' + new_inv.pk,
                                new_inv.save()
                            except Exception as e:
                                print(f"Failed to create InventoryTransaction: {e}")
                    else:
                        set_waiting_status()
            else:
                set_waiting_status()

        # บันทึกข้อมูล
        super().save(*args, **kwargs)

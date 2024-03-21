import re
from django.core.exceptions import ValidationError

def clean_phone_number(phone_number):
    # ลบขีด, ช่องว่าง, และสัญลักษณ์อื่นๆ
    phone_number = re.sub('[^0-9]', '', phone_number)

    # ตรวจสอบและตัด country code (66 หรือ +66)
    if phone_number.startswith('66'):
        phone_number = '0' + phone_number[2:]
    elif phone_number.startswith('+66'):
        phone_number = '0' + phone_number[3:]

    # ตรวจสอบความยาวหมายเลขโทรศัพท์
    if len(phone_number) != 10 or not phone_number.startswith('0'):
        raise ValidationError('หมายเลขโทรศัพท์ต้องเริ่มต้นด้วย 0 และมีความยาว 10 ตัวอักษร')

    return phone_number

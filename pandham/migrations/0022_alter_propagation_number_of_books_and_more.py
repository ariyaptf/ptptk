# Generated by Django 5.0.3 on 2024-03-18 07:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pandham', '0021_alter_propagation_target_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propagation',
            name='number_of_books',
            field=models.PositiveIntegerField(default=0, help_text='จำนวนหนังสือที่ต้องการสนับสนุนการพิมพ์', verbose_name='จำนวน'),
        ),
        migrations.AlterField(
            model_name='propagation',
            name='target_groups',
            field=models.ManyToManyField(to='pandham.pandhamtargetgroup', verbose_name='กลุ่มเป้าหมาย'),
        ),
        migrations.RemoveField(
            model_name='requestpandham',
            name='recipient_category',
        ),
        migrations.AddField(
            model_name='requestpandham',
            name='recipient_category',
            field=models.ForeignKey(help_text='กรุณาระบุกลุ่มหรือองค์กรของคุณ', null=True, on_delete=django.db.models.deletion.SET_NULL, to='pandham.pandhamtargetgroup', verbose_name='กลุ่ม'),
        ),
    ]

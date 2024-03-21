# Generated by Django 5.0.3 on 2024-03-13 06:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pandham', '0007_inventorytransaction_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventorytransaction',
            name='user',
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='created_by',
            field=models.ForeignKey(default=1, editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='pandham_targets', to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='updated_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_transactions', to=settings.AUTH_USER_MODEL, verbose_name='Updated By'),
        ),
    ]

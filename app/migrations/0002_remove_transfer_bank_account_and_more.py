# Generated by Django 5.1.6 on 2025-04-04 07:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transfer',
            name='bank_account',
        ),
        migrations.RemoveField(
            model_name='transfer',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='transfer',
            name='recipient_account_number',
        ),
        migrations.AddField(
            model_name='transfer',
            name='recipient_account',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='recipient_account', to='app.bankaccount'),
        ),
        migrations.AddField(
            model_name='transfer',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='sent_transfers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transfer',
            name='wire_recipient',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='app.recipient'),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender_account', to='app.bankaccount'),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='transfer_type',
            field=models.CharField(choices=[('interbank', 'InterBank Transfer'), ('wire', 'Wire Transfer'), ('other', 'Other Bank Transfer')], max_length=20),
        ),
    ]

# Generated by Django 5.1.2 on 2024-11-25 21:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_notfications'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='chat_name',
        ),
        migrations.DeleteModel(
            name='Chat_name',
        ),
    ]
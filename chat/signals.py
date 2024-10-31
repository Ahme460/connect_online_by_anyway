from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import *
user=get_user_model
@receiver(post_save,sender=Customer_user)
def create_Chatname(sender, instance, created, **kwargs):
    if created:
        base_user=instance.id
        users=Customer_user.objects.all().exclude(id=instance.id).values_list('id',flat=True)
        for i in users:
            chat_id=int(i)+int(base_user)
            chat=Chat_name.objects.create(
                name=f"chat_{chat_id}",
                user_1=instance,  # استخدم الكائن بدلاً من id
                user_2=Customer_user.objects.get(id=i)
            )
            
        
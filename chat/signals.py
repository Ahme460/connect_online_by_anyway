from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(post_save, sender=Message)
def send_message_notification(sender, instance, created, **kwargs):
    if created:
        print("hi iam in signal")
        
        receiver = instance.receiver
        channel_layer = get_channel_layer()
        chat = f"chanal_name_{str(receiver.id)}"
        print(f"iam in signal chat is {chat}")
    
        async_to_sync(channel_layer.group_send)(
            chat, 
            {
                "type": "notification",
                "receiver": receiver.id,
                "message": f"New message from {instance.sender.username}",
                "sender": instance.sender.id,
            }
        )
        print("Event sent to channel group.")

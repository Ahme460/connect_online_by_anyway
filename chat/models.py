from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# Create your models here.
class Customer_user(AbstractUser):
    phone=models.CharField( max_length=50)
    status=models.BooleanField(default=False)
    last_seen=models.DateTimeField( null=True)
    

class Message(models.Model):
    type_mess=[
        
        ("disconnect","disconnect"),
        ("connect","connect"),
        ("seen","seen")
    ]
    
    sender = models.ForeignKey(Customer_user, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Customer_user, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    type_message=models.CharField(max_length=20,choices=type_mess,default="disconnect")
    





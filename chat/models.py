from django.db import models
from django.contrib.auth.models import AbstractUser ,BaseUserManager ,PermissionsMixin
from django.utils import timezone
# Create your models here.

class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set.")  
        user = self.model(username=username, **extra_fields) 
        user.set_password(password)  
        user.save(using=self._db) 
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        # يمكنك تعيين extra_fields هنا إذا كنت بحاجة إلى أي حقول إضافية للمشرف
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)  
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)

class Customer_user(AbstractUser):
    phone=models.CharField( max_length=50)
    status=models.BooleanField(default=False)
    last_seen=models.DateTimeField( null=True)
    objects=MyUserManager()
    
    def __str__(self):
        return self.username
    

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
    
    def __str__(self):
        return f'{self.sender} _ {self.receiver}'



class Notfications(models.Model):
    sender = models.ForeignKey(
        Customer_user,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )
    receiver = models.ForeignKey(
        Customer_user,
        on_delete=models.CASCADE,
        related_name="received_notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

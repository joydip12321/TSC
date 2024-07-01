from django.db import models
from django.utils import timezone
from django.conf import settings


class UserProfile(models.Model):
    USER_ROLES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('guest', 'Guest'),
    ]
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES)
    def __str__(self):
        return self.role

class Notice(models.Model):
    title = models.CharField(max_length=200)
    pdf = models.FileField(upload_to='pdfs')
    uploaded_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Room_Type(models.Model):
    roomtype = models.CharField(max_length=100)
    def __str__(self):
        return self.roomtype
    
class Room(models.Model):
    room=models.CharField(max_length=50)
    roomtype = models.ForeignKey(Room_Type, on_delete=models.SET_NULL,null=True,blank=True)
    capacity=models.IntegerField(default=0)
    description=models.TextField(null=True,blank=True)
    img=models.FileField(upload_to='img')
    price=models.IntegerField(default=0)
    def __str__(self) -> str:
        return self.room
    
   
class Booking(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Cash-on'),
        ('ONLINE', 'Online'),
    ]
    booking_id = models.AutoField(primary_key=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    email = models.EmailField() 
    room = models.ForeignKey(Room, on_delete=models.SET_NULL,null=True,blank=True)
    check_in=models.DateField()
    check_out=models.DateField()
    tot_price=models.IntegerField(default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES,default=0)
    confirmed = models.BooleanField(default=False) 
    role=models.CharField(max_length=10,default="Student")



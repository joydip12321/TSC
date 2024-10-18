from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User



class UserProfile(models.Model):
    USER_ROLES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('guest', 'Guest'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES)
    phone = models.CharField(max_length=15, null=True, blank=True)  # Add phone number field

    def __str__(self):
        return self.user.username
    

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
        ('CASH', 'CASH'),
        ('E-Payment', 'E-Payment'),
    ]
    booking_id = models.AutoField(primary_key=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    email = models.EmailField() 
    room = models.ForeignKey(Room, on_delete=models.SET_NULL,null=True,blank=True)
    check_in=models.DateField()
    check_out=models.DateField()
    tot_price=models.IntegerField(default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')
    confirmed = models.BooleanField(default=False) 
    role=models.CharField(max_length=10,default="Student")

class MenuItem(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='img/')
    description=models.CharField(max_length=40)

    def __str__(self):
        return self.name

class Orders(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Change to ForeignKey
    item=models.ForeignKey('MenuItem',on_delete=models.CASCADE,null=True)
    email = models.CharField(max_length=50,null=True)
    role = models.CharField(max_length=20,null=True)
    location = models.CharField(max_length=500,null=True)
    phone = models.CharField(max_length=20,null=True)
    order_time= models.DateTimeField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=0)
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User



class UserProfile(models.Model):
    USER_ROLES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('guest', 'Guest'),
        ('club member','club member'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES)
    phone = models.CharField(max_length=15, null=True, blank=True)  # Add phone number field
    # Fields for guest role
    national_id = models.CharField(max_length=20, null=True, blank=True)  # Reference National ID
    reference_name = models.CharField(max_length=100, null=True, blank=True)  # Reference Name
    ref_contact = models.CharField(max_length=15, null=True, blank=True)  # Reference Contact
    ref_role = models.CharField(max_length=50, null=True, blank=True)  # Reference Role
    ref_dept_name = models.CharField(max_length=100, null=True, blank=True)  # Reference Department Name

    # Fields for student role
    student_id = models.CharField(max_length=20, null=True, blank=True)  # Student ID
    student_dept_name = models.CharField(max_length=100, null=True, blank=True)  # Student Department Name
    student_session = models.CharField(max_length=20, null=True, blank=True)  # Student Session

    # Fields for teacher role
    teacher_id = models.CharField(max_length=20, null=True, blank=True)  # Teacher ID
    teacher_dept_name = models.CharField(max_length=100, null=True, blank=True) 

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
    current_status=[
        ('Available for booking','Available for booking'),
        ('Not available currently','Not available currently'),
        ('Not for Booking','Not for booking'),
        
    ]
    room=models.CharField(max_length=50)
    roomtype = models.ForeignKey(Room_Type, on_delete=models.SET_NULL,null=True,blank=True)
    capacity=models.IntegerField(default=0)
    status = models.CharField(null=True,blank=True,max_length=50, choices=current_status)
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
    check_in=models.DateTimeField()
    check_out=models.DateTimeField()
    tot_price=models.IntegerField(default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')
    confirmed = models.IntegerField(default=0) 
    role=models.CharField(max_length=10,default="Student")
    def __str__(self):
        return self.room.room

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
    items_summary = models.TextField(null=True)  # Add this for order summary
    email = models.CharField(max_length=50,null=True)
    role = models.CharField(max_length=20,null=True)
    location = models.CharField(max_length=500,null=True)
    phone = models.CharField(max_length=20,null=True)
    order_time= models.DateTimeField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.items_summary} ordered by {self.user.username}"
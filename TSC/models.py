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
    phone = models.CharField(max_length=15, null=True, blank=True)  
    national_id = models.CharField(max_length=20, null=True, blank=True) 
    reference_name = models.CharField(max_length=100, null=True, blank=True) 
    ref_contact = models.CharField(max_length=15, null=True, blank=True)  
    ref_role = models.CharField(max_length=50, null=True, blank=True) 
    ref_dept_name = models.CharField(max_length=100, null=True, blank=True) 

    student_id = models.CharField(max_length=20, null=True, blank=True)  
    student_dept_name = models.CharField(max_length=100, null=True, blank=True) 
    student_session = models.CharField(max_length=20, null=True, blank=True) 

    teacher_id = models.CharField(max_length=20, null=True, blank=True)  
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
        ('Check','Check')
    ]
    booking_id = models.AutoField(primary_key=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    email = models.EmailField() 
    room = models.ForeignKey(Room, on_delete=models.SET_NULL,null=True,blank=True)
    check_in=models.DateTimeField()
    check_out=models.DateTimeField()
    tot_price=models.IntegerField(default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')
    check_no = models.CharField(max_length=50, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    confirmed = models.IntegerField(default=0) 
    role=models.CharField(max_length=10,default="Student")
    def __str__(self):
        return self.room.room



class MealTime(models.Model):  
    name = models.CharField(max_length=20, unique=True) 

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2) 
    image = models.ImageField(upload_to='menu_images/')
    description = models.CharField(max_length=255)  
    meal_times = models.ManyToManyField(MealTime, related_name="menu_items") 

    def __str__(self):
        return f"{self.name} ({', '.join(meal.name for meal in self.meal_times.all())})"



class Orders(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    items_summary = models.TextField(null=True)  
    email = models.CharField(max_length=50,null=True)
    role = models.CharField(max_length=20,null=True)
    location = models.CharField(max_length=500,null=True)
    phone = models.CharField(max_length=20,null=True)
    order_time= models.DateTimeField(null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.items_summary} ordered by {self.user.username}"
    

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} at {self.timestamp}"

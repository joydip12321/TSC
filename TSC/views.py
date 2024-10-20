
# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from TSC.models import*
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import user_passes_test,login_required
from datetime import datetime
from django.contrib.auth.models import User
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.utils.dateparse import parse_date
from django.core.mail import send_mail
import re,json
from django.contrib.auth.views import LoginView,LogoutView
from .forms import *
from datetime import datetime,timedelta
from functools import wraps
from django.views.decorators.csrf import csrf_exempt



def custom_login_required(function=None, redirect_field_name='next', login_url=None):
    @wraps(function)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "You need to log in first to access this page.")
            return redirect('login')
        return function(request, *args, **kwargs)
    return _wrapped_view

def is_admin(user):
    return user.is_authenticated and user.is_staff

def AdminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request,user)
            
            return redirect('home')
        else:
            messages.success(request, "Invalid username or password")
        return redirect('/AdminLogin/')
    return render(request, 'AdminLogin.html')

@user_passes_test(is_admin, login_url='/')
def AdminLogout(request):
    logout(request)
    return redirect('/AdminLogin/')

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Registration successful")
            return redirect('login')  # Redirect to a success page
        else:
            for error in user_form.errors.values():
                messages.error(request, error.as_text())
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})

def LogIn(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        
        if not User.objects.filter(username=username).exists():
            messages.info(request, "Invalid Username")
            return redirect('login')
        user=authenticate(request,username=username,password=password)
        if user is None :
            messages.error(request, "Invalid Username or Password")
        else:
            login(request,user)
            return redirect('home')
    return render(request,"login.html")

login_required(login_url="/login/")
def Logout(request):
    logout(request)
    return redirect('/login/')

def Home(request):
    return render(request,"home.html")

@user_passes_test(is_admin, login_url='/')
def AddNotice(request):
    if request.method == "POST":
        title = request.POST.get("title")
        pdf = request.FILES.get("pdf")
         
        if title and pdf:
            uploaded_at = datetime.now().date()
            Notice.objects.create(
                title=title,
                pdf=pdf,
                uploaded_at=uploaded_at,
            )
            messages.success(request, f'File added successfully.')
    return render(request, "Add_notice.html")

def Notices(request):
    notices = Notice.objects.all().order_by('-id')
    paginator=Paginator(notices,10)
    page_no=request.GET.get('page')
    try:
        notices = paginator.page(page_no)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        notices = paginator.page('1')  
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        notices = paginator.page(paginator.num_pages)
    return render(request, "notice.html", {'notices': notices,'page_name':"NOTICES"})

@user_passes_test(is_admin, login_url='/')
def AddRoom(request):
    roomt=Room_Type.objects.all()
    if(request.method=="POST"):
        room=request.POST.get('room')
        roomtype_id=request.POST.get('roomtype')
        description=request.POST.get('description')
        img=request.FILES.get('img')
        status=request.POST.get('status')
        price=request.POST.get('price')
        roomtype= Room_Type.objects.get(pk=roomtype_id)  # Assuming the select field is named 'category'

        existing_room = Room.objects.filter(room=room).first()
        if existing_room:
            messages.success(request, "Room already exists")
        else:
            Room.objects.create(
            room=room ,
            roomtype=roomtype,
            description=description,
            status=status,
            img=img,
            price=price,
            ) 
            messages.success(request, f'Room {room} added successfully.')
        return redirect('AddRoom')
    context={
        'roomt':roomt ,
             }
    return render(request,"AddRoom.html",context)

def AllRoom(request):
        room=Room.objects.all().order_by('-id')
        paginator = Paginator(room, 6)
        page_no = request.GET.get('page')
        try:
            room = paginator.page(page_no)
        except PageNotAnInteger:
            room = paginator.page(1)
        except EmptyPage:
            room = paginator.page(paginator.num_pages)
        return render(request, "AllRoom.html",{'room':room})

def GuestRoom(request):
    available_room = Room.objects.filter(roomtype__roomtype="GuestRooms").order_by('-id')  # or any other field
    room_type = Room_Type.objects.all()
    
    if request.method == "POST":
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        if check_in and not check_out:
            messages.error(request, 'Please provide both check-in and check-out dates.')
        if not check_in and check_out:
            messages.error(request, 'Please provide both check-in and check-out dates.')
  
        if check_in and check_out:
            today = datetime.now().date()

            if parse_date(check_in) >= parse_date(check_out):
                messages.error(request, 'Check-out date must be after the check-in date.')
            elif parse_date(check_in) < today or parse_date(check_out) < today:
                messages.error(request, 'Check-in and check-out dates cannot be in the past.') 
            else:
                qs = Booking.objects.filter(
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                )
                available_room = available_room.exclude(booking__in=qs)
            
    paginator = Paginator(available_room, 6)
    page_no = request.GET.get('page')
    try:
        available_room = paginator.page(page_no)
    except PageNotAnInteger:
        available_room = paginator.page(1)
    except EmptyPage:
        available_room = paginator.page(paginator.num_pages)

    context = {
        'room': available_room,
        'page_name': "ROOMS",
        'room_type': room_type,
    }
    return render(request, "Room_list.html", context)


def EventRoom(request):
    available_room = Room.objects.filter(roomtype__roomtype="EventSpaces").order_by('-id')
    room_type = Room_Type.objects.all()
    
    if request.method == "POST":
        check_date = request.POST.get('check_date')  # Assume this is the date input
        start_hour = request.POST.get('start_time')
        end_hour = request.POST.get('end_time')

        if not check_date or not start_hour or not end_hour:
            messages.error(request, 'Please provide date and both start and end times.')
        else:
            today = datetime.now().date()

            # Combine date with hours to create datetime objects
            check_in = datetime.combine(parse_date(check_date), datetime.min.time()).replace(hour=int(start_hour))
            check_out = datetime.combine(parse_date(check_date), datetime.min.time()).replace(hour=int(end_hour))

            # Validation for check-in and check-out
            if check_in >= check_out:
                messages.error(request, 'Check-out time must be after the check-in time.')
            elif check_in.date() < today or check_out.date() < today:
                messages.error(request, 'Check-in and check-out dates cannot be in the past.') 
            else:
                # Query to filter out overlapping bookings
                qs = Booking.objects.filter(
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                )
                available_room = available_room.exclude(booking__in=qs)
    
    paginator = Paginator(available_room, 6)
    page_no = request.GET.get('page')
    try:
        available_room = paginator.page(page_no)
    except PageNotAnInteger:
        available_room = paginator.page(1)
    except EmptyPage:
        available_room = paginator.page(paginator.num_pages)

    hours = list(range(9, 24))  # 9 AM to 11 PM (for start and end times)

    context = {
        'room': available_room,
        'page_name': "ROOMS",
        'room_type': room_type,
        'hours': hours,
    }
    return render(request, "Event_room.html", context)

@custom_login_required
def EventBooking(request,room_no):
    hours = list(range(9, 24))  # 9 AM to 11 PM (for start and end times)

    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        role = user_profile.role
    except UserProfile.DoesNotExist:
        role = "admin"
        
    room = get_object_or_404(Room, room=room_no)  # Fetch the room based on room number
    room_price = room.price  # Get the price of the room

    if request.method == 'POST':
        check_date = request.POST.get('check_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        today = timezone.now().date()

        if not check_date or not start_time or not end_time:
            messages.error(request, 'Please provide all required fields.')
        elif start_time >= end_time:
            messages.error(request, 'End hour must be after the start hour.')
        elif datetime.strptime(check_date, '%Y-%m-%d').date() < today:
            messages.error(request, 'Provide a future date to book the room.')
        else:
            # Calculate check-in and check-out datetime
            check_in = datetime.strptime(check_date, '%Y-%m-%d') + timedelta(hours=int(start_time))
            check_out = datetime.strptime(check_date, '%Y-%m-%d') + timedelta(hours=int(end_time))
            
            qs = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            
            if qs.exists():
                messages.error(request, 'Room is not available for the selected time.')
            else:
                total_price = (check_out - check_in).total_seconds() / 3600 * room_price  # Calculate total price based on hours
                
                last_booking = Booking.objects.last()
                booking_id = 1 if last_booking is None else last_booking.booking_id + 1
                email = request.user.email
                
                Booking.objects.create(
                    booking_id=booking_id,
                    email=email,
                    user=user,
                    room=room,
                    check_in=check_in,
                    check_out=check_out,
                    tot_price=total_price,
                    payment_method='Cash',
                    role=role,
                )

                messages.success(request, 'Booking request done successfully. Wait for the confirmation email from us.')
                return redirect('event_room')

    return render(request, 'Event_booking.html', {'room': room, 'room_price': room_price,'hours':hours})

def ClubRoom(request):
    available_room = Room.objects.filter(roomtype__roomtype="ClubSocieties").order_by('-id')
    room_type = Room_Type.objects.all()
    
    if request.method == "POST":
        room_name = request.POST.get('room')  # Get the room name input
        status = request.POST.get('status')  # Get the status input

        # Filter by room name if provided
        if room_name:
            available_room = available_room.filter(room__icontains=room_name)

        # Filter by status if provided
        if status:
            available_room = available_room.filter(status=status)
    
    paginator = Paginator(available_room, 6)
    page_no = request.GET.get('page')
    try:
        available_room = paginator.page(page_no)
    except PageNotAnInteger:
        available_room = paginator.page(1)
    except EmptyPage:
        available_room = paginator.page(paginator.num_pages)
  
    context = {
        'room': available_room,
        'page_name': "ROOMS",
        'room_type': room_type,
    }
    return render(request, "Club_room.html", context)

@custom_login_required
def ClubBooking(request, room_name):
    room = get_object_or_404(Room, room=room_name)

    # Check if room is available for booking
    if room.status != 'Available for booking':
        messages.error(request, 'The room is not available for booking.')
        return redirect('room_list')

    # Create a new booking with check-in date as today
    check_in_date = timezone.now().date()
    check_out_date = check_in_date + timedelta(days=365)
    # Assuming the user is logged in and we get user ID and email from the request
    Booking.objects.create(
        user=request.user,
        email=request.user.email,
        room=room,
        check_in=check_in_date,
        check_out=check_out_date,
        tot_price=room.price,  # You can calculate total price if needed
        payment_method='CASH',  # Default to CASH or let the user choose later
        role='Club',  # Adjust the role as necessary
    )


    messages.success(request, 'Room requested successfully.')
    return redirect('club_room')

def OfficeRoom(request):
    available_room = Room.objects.filter(roomtype__roomtype="ClubSocieties").order_by('-id')
    room_type = Room_Type.objects.all()
    
    
    paginator = Paginator(available_room, 6)
    page_no = request.GET.get('page')
    try:
        available_room = paginator.page(page_no)
    except PageNotAnInteger:
        available_room = paginator.page(1)
    except EmptyPage:
        available_room = paginator.page(paginator.num_pages)
  
    context = {
        'room': available_room,
        'page_name': "ROOMS",
        'room_type': room_type,
    }
    return render(request, "Office_room.html", context)

def OtherRoom(request):
    available_room = Room.objects.filter(roomtype__roomtype="Other").order_by('-id')
    room_type = Room_Type.objects.all()
    
    
    paginator = Paginator(available_room, 6)
    page_no = request.GET.get('page')
    try:
        available_room = paginator.page(page_no)
    except PageNotAnInteger:
        available_room = paginator.page(1)
    except EmptyPage:
        available_room = paginator.page(paginator.num_pages)
  
    context = {
        'room': available_room,
        'page_name': "ROOMS",
        'room_type': room_type,
    }
    return render(request, "Other_room.html", context)
# Booking funtionality
@custom_login_required
def Bookin(request,room_no):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        role = user_profile.role
    except UserProfile.DoesNotExist:
        role = "admin"
    room = get_object_or_404(Room, room=room_no)  # Fetch the room based on room number
    room_price = room.price  # Get the price of the room

    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        # check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        payment_method = request.POST.get('payment_method')
        today = timezone.now().date()

        if not check_in or not check_out or not payment_method:
            messages.error(request, 'Please provide all')
        elif parse_date(check_in) >= parse_date(check_out):
            messages.error(request, 'Check-out date must be after the check-in date.')
        elif check_in_date <= today:
            messages.error(request, 'Provide future date to book room')
        else:
            qs = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            
            if qs.exists():
                messages.error(request, 'Room is not available for the selected dates.')
            else:
                room_price = room.price
                total_price = (parse_date(check_out) - parse_date(check_in)).days * room_price
                
                last_booking = Booking.objects.last()
                booking_id = 1 if last_booking is None else last_booking.booking_id + 1
                email=request.user.email
                Booking.objects.create(
                    booking_id=booking_id,
                    email=email,
                    user=user,
                    room=room,
                    check_in=check_in,
                    check_out=check_out,
                    tot_price=total_price,
                    payment_method=payment_method,
                    role=role,
                )
                messages.success(request, f'Booking request done successfully,Wait for the confirmation e-mail from us')
                return redirect('room_list')
    return render(request,'Booking.html',{'room':room,'room_price':room_price,'page_name':"BOOKING"})

@user_passes_test(is_admin, login_url='/')
def Booking_list(request):
    booking_list=Booking.objects.all()
    return render(request,'Booking_list.html',{'booking_list':booking_list,'page_name':"BOOKING LIST"})

@user_passes_test(is_admin, login_url='/')
def reject_booking(request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        user_email = booking.email
        subject = 'Booking Rejection Notification'
        message = (
        f"Dear {booking.user},\n\n"
        f"We regret to inform you that your booking request (Booking ID: {booking_id}) has been rejected .\n\n"
        "If you have any questions, please feel free to contact us.\n\n"
        "Best regards,\nJUST TSC "
    )
        from_email = settings.EMAIL_HOST_USER
        to_email = [user_email]
        send_mail(subject, message, from_email, to_email)
        booking.delete() 
        return redirect('/Booking_list/')

@user_passes_test(is_admin, login_url='/')
def approve_booking(request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        user_email = booking.email
        subject = 'Booking Approval Notification'
        message = (
        f"Dear {booking.user},\n\n"
        f"We are happy to inform you that your booking request (Booking ID: {booking_id}) has been accepted .\n\n"
        "If you have any questions, please feel free to contact us.Please arrive before the check-in date.\n\n"
        "Best regards,\nJUST TSC "
    )
        from_email = settings.EMAIL_HOST_USER
        to_email = [user_email]
        send_mail(subject, message, from_email, to_email)
        booking.confirmed = True  # Set the confirmed field to True

        booking.save()        
        return redirect('/Booking_list/')

@user_passes_test(is_admin, login_url='/')
def AddItem(request):
    itemForm=ItemForm()
    if request.method=='POST':
        itemForm=ItemForm(request.POST, request.FILES)
        if itemForm.is_valid():
            itemForm.save()

            messages.success(request, f'Item added successfully.')

        return redirect('/addItem/')
    return render(request,'Add_item.html',{'itemForm':ItemForm})

def Item(request):
    item=MenuItem.objects.all()
    return render(request,'item.html',{'item':item})

def Dinning(request):
    return render(request,"dinning.html")

@custom_login_required
def AddCart(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    
    # Check if the cart exists in the session
    cart = request.session.get('cart', {})
    
    # Add item to cart
    if str(pk) in cart:
        messages.info(request, f'Item already added to cart')

    else:
        cart[str(pk)] = {
            'name': item.name,
            'price': str(item.price),
            'quantity': 1,
            'image': item.image.url,
        }
        messages.success(request, f'Item added to cart successfully.')

    
    # Save the updated cart back to the session
    request.session['cart'] = cart
    return redirect('/item/')

@custom_login_required
def ViewCart(request):
    cart = request.session.get('cart', {})
    user=request.user

    try:
        user_profile = UserProfile.objects.get(user=user)
        role = user_profile.role
        phone=user_profile.phone
    except UserProfile.DoesNotExist:
        role = "admin"
        phone="0000000000"
    # Prepare a list of cart items for rendering
    cart_items = []

    total_price = 0
    # user=request.user
    for item_id, item_details in cart.items():
        cart_items.append(item_details)

    if request.method == 'POST':
            cart = request.session.get('cart', {})
            location = request.POST.get('location')

            # Loop through cart items to create order records
            for item_id, item_details in cart.items():
                product = MenuItem.objects.get(id=item_id)
                quantity=int(request.POST.get(f'quantity_',0)) # Use item_id directly
                # Calculate total price for each item
                item_total_price = product.price * quantity
                # Create Order instance
                if quantity >0:
                    order_item=Orders(
                        user=user,
                        item=product,
                        email=user.email,
                        location=location,
                        phone=phone,
                        role=role,
                        quantity=quantity,
                        price=item_total_price,
                        status='Pending',

                    )
                    order_item.save()  # Save each order item
                    messages.success(request, f'Order Request send successfully,wait for confirmation')



            # Clear the cart after order is placed
            request.session['cart'] = {}

    return render(request, 'cart.html', {'cart_items': cart_items})
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
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
from django.utils.timezone import now
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse 
from django.utils.encoding import force_str
from django.core.mail import EmailMessage
from decimal import Decimal
import requests
from django.utils.dateparse import parse_date


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
            user = user_form.save(commit=False)
            user.is_active = False
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
            activation_url = f'http://{current_site.domain}{activation_link}'
            message = render_to_string('activation_email.html', {
                'user': user,
                'activation_url': activation_url,
            })
            email = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER, [user.email])
            email.content_subtype = 'html'
            email.send()

            messages.success(request, "Registration successful. Please confirm your email address to activate your account.")
            return redirect('login')
        else:
            for error in user_form.errors.values():
                messages.error(request, error.as_text())
            for error in profile_form.errors.values():
                messages.error(request, error.as_text())
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()

    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated successfully!")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect('register')

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

def about_view(request):
    return render(request, 'about_us.html')

@user_passes_test(is_admin, login_url='/')
def AddNotice(request):
    notice_id = request.POST.get("notice_id") 
    notices = Notice.objects.all().order_by('-uploaded_at')

    if request.method == "POST":
        title = request.POST.get("title")
        pdf = request.FILES.get("pdf")

        if notice_id:
            notice = get_object_or_404(Notice, id=notice_id)
            notice.title = title
            if pdf:
                notice.pdf = pdf  
            notice.save()
            messages.success(request, "Notice updated successfully.")
        else: 
            if title and pdf:
                Notice.objects.create(title=title, pdf=pdf, uploaded_at=now().date())
                messages.success(request, "File added successfully.")

        return redirect("AddNotice") 

    return render(request, "Add_notice.html", {"notices": notices})

@user_passes_test(is_admin, login_url='/')
def delete_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    notice.delete()
    messages.success(request, "Notice deleted successfully.")
    return redirect("AddNotice") 

def Notices(request):
    notices = Notice.objects.all().order_by('-id')
    paginator=Paginator(notices,10)
    page_no=request.GET.get('page')
    try:
        notices = paginator.page(page_no)
    except PageNotAnInteger:
        notices = paginator.page('1')  
    except EmptyPage:
        notices = paginator.page(paginator.num_pages)
    return render(request, "notice.html", {'notices': notices,'page_name':"NOTICES"})

@user_passes_test(is_admin, login_url='/')
def AddRoom(request):
    roomt = Room_Type.objects.all()  

    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES) 

        if form.is_valid():
            room = form.cleaned_data['room']
            if Room.objects.filter(room=room).exists():
                messages.error(request, "Room already exists")
            else:
                form.save()
                messages.success(request, f'Room {room} added successfully.')
                return redirect('AddRoom')  

        else:
            for error in form.errors.values():
                messages.error(request, error)

    else:
        form = RoomForm() 

    context = {
        'roomt': roomt,
        'form': form, 
    }
    return render(request, "AddRoom.html", context)

@user_passes_test(is_admin, login_url='/')
def AdminRoom(request):
    room_form = RoomForm()
    rooms = Room.objects.all().order_by('-id')  

    if request.method == "POST":
        roomtype = request.POST.get('roomtype')
        status = request.POST.get('status')

        if roomtype:
            rooms = rooms.filter(roomtype=roomtype)
        if status:
            rooms = rooms.filter(status=status)

    return render(request, "adminRoom.html", {'rooms': rooms, 'room_form': room_form})

@user_passes_test(is_admin, login_url='/')
def UpdateRoom(request, room_id):
    room = get_object_or_404(Room, id=room_id)  
    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES, instance=room)  
        if form.is_valid():
            form.save()
            messages.success(request, f'Room {room.room} updated successfully.')
            return redirect('adminRoom') 
    else:
        form = RoomForm(instance=room) 

    context = {
        'form': form,
        'room': room,
    }
    return render(request, "update_room.html", context)  

@user_passes_test(is_admin, login_url='/')
def DeleteRoom(request, room_id):
    room = get_object_or_404(Room, id=room_id)  
    room.delete() 
    messages.success(request, f'Room {room.room} deleted successfully.')
    return redirect('adminRoom')  



def AllRoom(request):
    floor = request.GET.get('floor')
    if floor and floor.isdigit():  
        floor = int(floor)
        room = Room.objects.filter(room__gte=100 * (floor + 1), room__lt=100 * (floor + 2)).order_by('-id')
    else:
        room = Room.objects.all().order_by('-id')

    paginator = Paginator(room, 12)
    page_no = request.GET.get('page') 
    try:
        room = paginator.page(page_no)
    except PageNotAnInteger:
        room = paginator.page(1)  
    except EmptyPage:
        room = paginator.page(paginator.num_pages)  

    return render(request, "AllRoom.html", {'room': room, 'selected_floor': floor})

def GuestRoom(request):
    available_room = Room.objects.filter(roomtype__roomtype="Guest Room").order_by('-id')  
    room_type = Room_Type.objects.all()
    check_in=""
    check_out=""
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
                    confirmed=1,
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
        'check_in': check_in,
        'check_out': check_out,
    }
    return render(request, "Room_list.html", context)


def EventRoom(request):
    available_room = Room.objects.filter(roomtype__roomtype="Event Space").order_by('-id')
    room_type = Room_Type.objects.all()
    check_date=""
    start_hour = None
    end_hour = None
    if request.method == "POST":
        check_date = request.POST.get('check_date') 
        start_hour = request.POST.get('start_time')
        end_hour = request.POST.get('end_time')

        if not check_date or not start_hour or not end_hour:
            messages.error(request, 'Please provide date and both start and end times.')
        else:
            today = datetime.now().date()

            check_in = timezone.make_aware(
            datetime.combine(parse_date(check_date), datetime.min.time()).replace(hour=int(start_hour))
            )
            check_out = timezone.make_aware(
            datetime.combine(parse_date(check_date), datetime.min.time()).replace(hour=int(end_hour))
                )

            if check_in >= check_out:
                messages.error(request, 'Check-out time must be after the check-in time.')
            elif check_in.date() < today or check_out.date() < today:
                messages.error(request, 'Check-in and check-out dates cannot be in the past.') 
            else:
                qs = Booking.objects.filter(
                    confirmed=1,
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

    hours = list(range(9, 23)) 

    context = {
        'room': available_room,
        'page_name': "ROOMS",
        'room_type': room_type,
        'hours': hours,
        'check_date': check_date,
        'start_hour': start_hour,
        'end_hour': end_hour,
    }
    return render(request, "Event_room.html", context)

@custom_login_required
def EventBooking(request, room_no):
    hours = list(range(9, 23))
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        role = user_profile.role
    except UserProfile.DoesNotExist:
        role = "admin"

    room = get_object_or_404(Room, room=room_no)
    room_price = room.price

    if request.method == 'POST':
        check_date = request.POST.get('check_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        payment_method = request.POST.get('payment_method')
        check_no = request.POST.get('check_no')
        bank_name = request.POST.get('bank_name')

        today = timezone.now().date()

        if not check_date or not start_time or not end_time or not payment_method:
            messages.error(request, 'Please provide all required fields.')
        elif int(start_time) >= int(end_time):
            messages.error(request, 'End hour must be after start hour.')
        elif datetime.strptime(check_date, '%Y-%m-%d').date() < today:
            messages.error(request, 'Choose a future date for booking.')
        elif payment_method == 'Check' and (not check_no or not bank_name):
            messages.error(request, 'Check number and bank name are required for Check payment.')
            return redirect(request.path)
        else:
            check_in = datetime.strptime(check_date, '%Y-%m-%d') + timedelta(hours=int(start_time))
            check_out = datetime.strptime(check_date, '%Y-%m-%d') + timedelta(hours=int(end_time))

            qs = Booking.objects.exclude(confirmed=0).filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            if qs.exists():
                messages.error(request, 'Room is not available at that time.')
            else:
                duration_hours = (check_out - check_in).total_seconds() / 3600
                total_price = Decimal(duration_hours * room_price)
                last_booking = Booking.objects.last()
                booking_id = last_booking.booking_id + 1 if last_booking else 1

                if payment_method == 'E-Payment':
                    success_url = request.build_absolute_uri(
                        reverse('payment_success') +
                        f"?booking_id={booking_id}"
                        f"&user_id={user.id}"
                        f"&email={user.email}"
                        f"&room_no={room.room}"
                        f"&check_in={check_in}"
                        f"&check_out={check_out}"
                        f"&total_price={total_price}"
                        f"&role={role}"
                        f"&check_no={f'BOOK{booking_id}'}"

                    )

                    payload = {
                        'store_id': 'jasho6806716e772ee',
                        'store_passwd': 'jasho6806716e772ee@ssl',
                        'total_amount': str(total_price),
                        'currency': 'BDT',
                        'tran_id': f'BOOK{booking_id}',
                        'success_url': success_url,
                        'fail_url': request.build_absolute_uri(reverse('payment_fail')),
                        'cancel_url': request.build_absolute_uri(reverse('payment_cancel')),
                        'cus_name': user.get_full_name(),
                        'cus_email': user.email,
                        'cus_add1': 'TSC, Jashore',
                        'cus_phone': '01995140040',
                        'shipping_method': 'NO',
                        'product_name': f'Event Room {room.room}',
                        'product_category': 'Event Booking',
                        'product_profile': 'general',
                    }

                    response = requests.post("https://sandbox.sslcommerz.com/gwprocess/v3/api.php", data=payload)
                    res_data = response.json()

                    if res_data.get('status') == 'SUCCESS':
                        return redirect(res_data['GatewayPageURL'])
                    else:
                        messages.error(request, 'Payment gateway error.')
                else:
                    Booking.objects.create(
                        booking_id=booking_id,
                        email=user.email,
                        user=user,
                        room=room,
                        check_in=check_in,
                        check_out=check_out,
                        tot_price=total_price,
                        confirmed=0,
                        payment_method=payment_method,
                        check_no=check_no if payment_method == "Check" else None,
                        bank_name=bank_name if payment_method == "Check" else None,
                        role=role,
                    )
                    messages.success(request, 'Event booking request submitted successfully.')
                    return redirect('user_booking_list')

    return render(request, 'Event_booking.html', {
        'room': room,
        'room_price': room_price,
        'hours': hours,
        'page_name': "EVENT BOOKING"
    })

def ClubRoom(request):
    available_room = Room.objects.filter(roomtype__roomtype="Club Society").order_by('-id')
    room_type = Room_Type.objects.all()
    room_name=""
    status=""
    if request.method == "POST":
        room_name = request.POST.get('room')  
        status = request.POST.get('status') 

        if room_name:
            available_room = available_room.filter(room__icontains=room_name)

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
        'room_name':room_name,
        'status':status,
    }
    return render(request, "Club_room.html", context)

@custom_login_required
def ClubBooking(request, room_name):
    room = get_object_or_404(Room, room=room_name)

    if room.status != 'Available for booking':
        messages.error(request, 'The room is not available for booking.')
        return redirect('room_list')

    check_in_date = timezone.now().date()
    check_out_date = check_in_date + timedelta(days=365)
    Booking.objects.create(
        user=request.user,
        email=request.user.email,
        room=room,
        check_in=check_in_date,
        check_out=check_out_date,
        tot_price=Decimal(room.price),  
        payment_method='CASH',  
        role='Club', 
    )


    messages.success(request, 'Room requested successfully.')
    return redirect('club_room')

def OfficeRoom(request):
    available_room = Room.objects.filter(roomtype__roomtype="Office Room").order_by('-id')
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
    available_room = Room.objects.filter(roomtype__roomtype="Other Room").order_by('-id')
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


@custom_login_required
def Bookin(request, room_no):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        role = user_profile.role
    except UserProfile.DoesNotExist:
        role = "admin"

    room = get_object_or_404(Room, room=room_no)
    room_price = room.price

    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        payment_method = request.POST.get('payment_method')
        check_no = request.POST.get('check_no')
        bank_name = request.POST.get('bank_name')

        today = timezone.now().date()

        if not check_in or not check_out or not payment_method:
            messages.error(request, 'Please provide all fields')
        elif parse_date(check_in) >= parse_date(check_out):
            messages.error(request, 'Check-out date must be after check-in date')
        elif parse_date(check_in) < today:
            messages.error(request, 'Check-in must be in the future')
        elif payment_method == 'Check' and (not check_no or not bank_name):
            messages.error(request, 'Please provide check number and bank name for Check payment.')
            return redirect(request.path)
        else:
            qs = Booking.objects.exclude(confirmed=0).filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            if qs.exists():
                messages.error(request, 'Room not available for selected dates.')
            else:
                total_days = (parse_date(check_out) - parse_date(check_in)).days
                total_price = total_days * room_price
                last_booking = Booking.objects.last()
                booking_id = last_booking.booking_id + 1 if last_booking else 1

                if payment_method == 'E-Payment':
                    request.session.modified = True 
                    print("Pending booking stored:", request.session.get('pending_booking'))  
                    success_url = request.build_absolute_uri(
                        reverse('payment_success') +
                        f"?booking_id={booking_id}"
                        f"&user_id={user.id}"
                        f"&email={user.email}"
                        f"&room_no={room.room}"
                        f"&check_in={check_in}"
                        f"&check_out={check_out}"
                        f"&total_price={total_price}"
                        f"&role={role}"
                        f"&check_no={f'BOOK{booking_id}'}"
                    )


                    payload = {
                        'store_id': 'jasho6806716e772ee',
                        'store_passwd': 'jasho6806716e772ee@ssl',
                        'total_amount': str(total_price),
                        'currency': 'BDT',
                        'tran_id': f'BOOK{booking_id}',
                        'success_url': success_url,

                        'fail_url': request.build_absolute_uri(reverse('payment_fail')),
                        'cancel_url': request.build_absolute_uri(reverse('payment_cancel')),
                        'cus_name': user.get_full_name(),
                        'cus_email': user.email,
                        'cus_add1': 'TSC, Jashore',
                        'cus_phone': '01995140040',
                        'shipping_method': 'NO',
                        'product_name': f'Room {room.room}',
                        'product_category': 'Room Booking',
                        'product_profile': 'general',
                    }

                    response = requests.post("https://sandbox.sslcommerz.com/gwprocess/v3/api.php", data=payload)
                    res_data = response.json()

                    if res_data.get('status') == 'SUCCESS':
                        print("Redirecting to URL:", res_data['GatewayPageURL']) 
                        return redirect(res_data['GatewayPageURL'])
                    else:
                        messages.error(request, 'Payment gateway error.')

                else:
                    Booking.objects.create(
                        booking_id=booking_id,
                        email=user.email,
                        user=user,
                        room=room,
                        check_in=check_in,
                        check_out=check_out,
                        tot_price=total_price,
                        confirmed=0,
                        payment_method=payment_method,
                        check_no=check_no if payment_method == "Check" else None,
                        bank_name=bank_name if payment_method == "Check" else None,
                        role=role,
                    )
                    messages.success(request, 'Booking placed successfully. Wait for confirmation.')
                    return redirect('user_booking_list')

    return render(request, 'Booking.html', {
        'room': room,
        'room_price': room_price,
        'page_name': "BOOKING",

    })



@csrf_exempt
def payment_success(request):
    booking_id = request.GET.get('booking_id')
    user_id = request.GET.get('user_id')
    email = request.GET.get('email')
    room_no = request.GET.get('room_no')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    total_price = request.GET.get('total_price')
    role = request.GET.get('role')
    check_no = request.GET.get('check_no')


    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "❌ User not found.")
        return redirect('login')

    room = Room.objects.filter(room=room_no).first()
    if not room:
        messages.error(request, "❌ Room not found.")
        return redirect('room_list')

    if Booking.objects.filter(booking_id=booking_id).exists():
        messages.info(request, "ℹ️ Booking already confirmed.")
        return redirect('user_booking_list')

    Booking.objects.create(
        booking_id=booking_id,
        email=email,
        user=user,
        room=room,
        check_in=(check_in),
        check_out=(check_out),
        tot_price=total_price,
        confirmed=0,
        payment_method='E-Payment',
        role=role,
        check_no=check_no,
    )

    messages.success(request, '✅ Payment successful and Booking placed successfully. Wait for confirmation.')
    return redirect('user_booking_list')


@csrf_exempt
def payment_fail(request):
    messages.error(request, '❌ Payment failed.')
    return redirect('room_list')


@csrf_exempt
def payment_cancel(request):
    messages.warning(request, '⚠️ Payment cancelled by user.')
    return redirect('room_list')

@custom_login_required
def UserBookingList(request):
    booking_list = Booking.objects.filter(user=request.user).order_by('-booking_id')
    return render(request, 'user_booking_list.html', {'booking_list': booking_list})


@user_passes_test(is_admin, login_url='/')
def Booking_list(request):
    booking_list=Booking.objects.all().order_by('-booking_id')
    return render(request,'Booking_list.html',{'booking_list':booking_list,'page_name':"BOOKING LIST"})

@user_passes_test(is_admin, login_url='/')
def reject_booking(request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        user=booking.user
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
        booking.confirmed = 2 

        booking.save() 
        messages.success(request, f"The booking has been rejected and the notification has been sent to {user_email}.")
        Notification.objects.create(user=user, message=message)

        return redirect('/Booking_list/')

@user_passes_test(is_admin, login_url='/')
def approve_booking(request, booking_id):

        booking = get_object_or_404(Booking, pk=booking_id)
        user=booking.user
        room = booking.room  
        room.status = 'Not available currently' 
        room.save()

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
        booking.confirmed = 1 

        booking.save()  
        messages.success(request, f"The booking has been approved and the notification has been sent to {user_email}.")
        Notification.objects.create(user=user, message=message)

        return redirect('/Booking_list/')

@user_passes_test(is_admin, login_url='/')
def booking_report(request):
    bookings = Booking.objects.filter(confirmed=1).order_by('-booking_id')

    room_id = request.GET.get('room')
    user_id = request.GET.get('user')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if room_id:
        bookings = bookings.filter(room__id=room_id)
    if user_id:
        bookings = bookings.filter(user__id=user_id)
    if from_date:
        bookings = bookings.filter(check_in__date__gte=parse_date(from_date))
    if to_date:
        bookings = bookings.filter(check_out__date__lte=parse_date(to_date))

    context = {
        'bookings': bookings,
        'rooms': Room.objects.all(),
        'users': User.objects.all()
    }
    return render(request, 'booking_report.html', context)

@user_passes_test(is_admin, login_url='/')
def AddItem(request):
    itemForm = ItemForm()
    
    if request.method == 'POST':
        itemForm = ItemForm(request.POST, request.FILES)
        if itemForm.is_valid():
            item = itemForm.save(commit=False) 
            item.save()  

            itemForm.save_m2m()  

            messages.success(request, 'Item added successfully.')
            return redirect('adminItem') 

    return render(request, 'Add_item.html', {'itemForm': itemForm})

@user_passes_test(is_admin, login_url='/')
def AdminItem(request):
    menu_items = MenuItem.objects.all().order_by('-id')
    return render(request, 'adminItem.html', {'menu_items': menu_items})

@user_passes_test(is_admin, login_url='/')
def UpdateItem(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            form.save_m2m() 
            messages.success(request, 'Menu item updated successfully!')
            return redirect('adminItem')

    else:
        form = ItemForm(instance=item)

    return render(request, "update_item.html", {'form': form, 'item': item})

@user_passes_test(is_admin, login_url='/')
def DeleteItem(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.delete()
    messages.success(request, f'Item {item.name} deleted successfully.')
    return redirect('adminItem')

 

def Item(request):
    """Filter menu items by exact meal time selection."""
    
    meal_times = MealTime.objects.all() 
    selected_meal_times = request.GET.getlist('meal_time') 

    if selected_meal_times:
        item = MenuItem.objects.filter(meal_times__name__in=selected_meal_times).distinct()
        for meal_time in selected_meal_times:
            item = item.filter(meal_times__name=meal_time)
    else:
        item = MenuItem.objects.all() 

    return render(request, 'item.html', {
        'item': item,
        'meal_times': meal_times,
        'selected_meal_times': selected_meal_times
    })



def Dinning(request):
    return render(request, "dinning.html")


@custom_login_required
def AddCart(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    
    cart = request.session.get('cart', {})
    
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

    
    request.session['cart'] = cart
    
    return redirect('/item/')


@custom_login_required
def ViewCart(request):
    cart = request.session.get('cart', {})
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=user)
        role = user_profile.role
        phone = user_profile.phone
    except UserProfile.DoesNotExist:
        role = "admin"
        phone = "0000000000"

    cart_items = []
    for item_id, item_details in cart.items():
        item_details['id'] = item_id  
        cart_items.append(item_details)

    if request.method == 'POST':
        location = request.POST.get('location')
        order_time = request.POST.get('order_time')
        items_summary = []
        total_price = 0
        tot_quantity=0

        for item_id, item_details in cart.items():
            product = MenuItem.objects.get(id=item_id)
            q=f'quantity_{item_id}'
            quantity = int(request.POST.get(q, 0))
            tot_quantity+=quantity
            if quantity > 0:
                item_total_price = product.price * quantity
                total_price += item_total_price
                items_summary.append(f"{product.name} = {quantity}  ")

        items_summary_text = ", ".join(items_summary)

        order = Orders(
            user=user,
            items_summary=items_summary_text,
            email=user.email,
            location=location,
            phone=phone,
            role=role,
            order_time=order_time,
            quantity=tot_quantity,
            price=total_price,
            status='Pending',
        )
        order.save()
        messages.success(request, "Order request sent successfully. Wait for confirmation e-mail from us.")
        request.session['cart'] = {}

        return redirect('my_orders')

    return render(request, 'cart.html', {'cart_items': cart_items})

@custom_login_required
def CustomOrder(request):
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=user)
        role = user_profile.role
        phone = user_profile.phone
    except UserProfile.DoesNotExist:
        role = "admin"
        phone = "0000000000"

    if request.method == 'POST':
        location = request.POST.get('location')
        order_time = request.POST.get('order_time')
        order_items_json = request.POST.get('order_items') 

        if not order_items_json:
            messages.error(request, "No items added to the order!")
            return redirect('custom_order')

        try:
            order_items = json.loads(order_items_json)  
        except json.JSONDecodeError:
            messages.error(request, "Invalid order format. Please try again.")
            return redirect('custom_order')

        items_summary = []
        tot_quantity = 0

        for item in order_items:
            item_name = item.get("name")
            quantity = int(item.get("quantity", 0))

            if quantity > 0:
                tot_quantity += quantity
                items_summary.append(f"{item_name} = {quantity}")

        if not items_summary:
            messages.error(request, "Please add at least one valid item.")
            return redirect('custom_order')

        items_summary_text = ", ".join(items_summary)

        order = Orders(
            user=user,
            items_summary=items_summary_text,
            email=user.email,
            location=location,
            phone=phone,
            role=role,
            order_time=order_time,
            quantity=tot_quantity,
            price=0,  
            status='Pending',
        )
        order.save()
        messages.success(request, "Custom order request sent successfully.")
        return redirect('my_orders')

    return render(request, 'custom_order.html')
@user_passes_test(is_admin, login_url='/')
def AdminOrder(request):
    orders = Orders.objects.all().order_by('-order_time') 
    return render(request, 'admin_order.html', {'orders': orders})
@user_passes_test(is_admin, login_url='/')
def reject_order(request, order_id):
    order = get_object_or_404(Orders, pk=order_id)
    user=order.user
    user_email = order.email
    subject = 'Order Rejection Notification'
    message = (
        f"Dear {order.user},\n\n"
        f"We regret to inform you that your order (Order ID: {order_id}) has been rejected.\n\n"
        "If you have any questions, please feel free to contact us.\n\n"
        "Best regards,\nJUST TSC"
    )
    from_email = settings.EMAIL_HOST_USER
    to_email = [user_email]
    send_mail(subject, message, from_email, to_email)
    order.status = 'Out for Delivery'  

    order.save() 
    messages.success(request, f"The order has been rejected and the notification has been sent to {user_email}.")
    Notification.objects.create(user=user, message=message)

    return redirect('admin_order') 

@user_passes_test(is_admin, login_url='/')
def approve_order(request, order_id):
    order = get_object_or_404(Orders, pk=order_id)
    user=order.user
    user_email = order.email
    subject = 'Order Approval Notification'
    message = (
        f"Dear {order.user},\n\n"
        f"We are happy to inform you that your order (Order ID: {order_id}) has been accepted.\n\n"
        "If you have any questions, please feel free to contact us.\n\n"
        "Best regards,\nJUST TSC"
    )
    from_email = settings.EMAIL_HOST_USER
    to_email = [user_email]
    send_mail(subject, message, from_email, to_email)
    order.status = 'Order Confirmed'
    messages.success(request, f"The order has been approved and the notification has been sent to {user_email}.")
    Notification.objects.create(user=user, message=message)

    order.save()        
    return redirect('admin_order') 

@custom_login_required
def UserOrderList(request):
    user = request.user

    orders = Orders.objects.filter(user=user).order_by('-id') 

    return render(request, 'user_order_list.html', {'orders': orders})




@custom_login_required
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')

    notifications.update(read=True) 

    return render(request, 'user_notifications.html', {
        'notifications': notifications,
    })
from django.http import JsonResponse

def get_unread_notification_count(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, read=False).count()
        return JsonResponse({'unread_count': unread_count})
    return JsonResponse({'unread_count': 0})

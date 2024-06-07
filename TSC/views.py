
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
import re

# Create your views here.

def Home(request):
    return render(request,"home.html")
def Notices(request):
    notices = Notice.objects.all()
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



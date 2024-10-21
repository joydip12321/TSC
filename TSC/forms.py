from django import forms
from django.contrib.auth.models import User
from .models import *
import re

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords don't match")
        if password:
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError("Password must contain at least one uppercase letter.")
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError("Password must contain at least one lowercase letter.")
            if not re.search(r'[0-9]', password):
                raise forms.ValidationError("Password must contain at least one digit.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise forms.ValidationError("Password must contain at least one special character.")

        return cleaned_data
        

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'role', 'phone',
            'reference_name', 'ref_contact', 'ref_role', 'ref_dept_name', 'national_id',
            'student_id', 'student_dept_name', 'student_session',
            'teacher_id', 'teacher_dept_name'
        ]
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        if role == 'guest':
            # Ensure these fields are filled in for guests
            reference_name = cleaned_data.get('reference_name')
            ref_contact = cleaned_data.get('ref_contact')
            ref_role = cleaned_data.get('ref_role')
            ref_dept_name = cleaned_data.get('ref_dept_name')
            national_id = cleaned_data.get('national_id')

            if not reference_name or not ref_contact or not ref_role or not ref_dept_name or not national_id:
                raise forms.ValidationError("All reference fields are required for guests.")

        elif role == 'student':
            # Ensure these fields are filled in for students
            student_id = cleaned_data.get('student_id')
            student_dept_name = cleaned_data.get('student_dept_name')
            student_session = cleaned_data.get('student_session')

            if not student_id or not student_dept_name or not student_session:
                raise forms.ValidationError("All student fields are required for students.")

        elif role == 'teacher':
            # Ensure these fields are filled in for teachers
            teacher_id = cleaned_data.get('teacher_id')
            teacher_dept_name = cleaned_data.get('teacher_dept_name')

            if not teacher_id or not teacher_dept_name:
                raise forms.ValidationError("All teacher fields are required for teachers.")

class ItemForm(forms.ModelForm):
    class Meta:
        model=MenuItem
        fields=['name','price','description','image']

class RoomForm(forms.ModelForm):
    class Meta:
        model=Room
        fields=['room','roomtype','capacity','status','description','img','price',]

class BookingForm(forms.ModelForm):
    class Meta:
        model=Booking
        fields=['booking_id','user','email','room','check_in','check_out','tot_price','payment_method','confirmed','role',]

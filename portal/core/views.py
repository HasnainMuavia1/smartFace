from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Role

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Automatically redirect based on user role
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.role == Role.FACULTY:
                return redirect('faculty_dashboard')
            elif user.role == Role.STUDENT:
                return redirect('student_dashboard')
            else:
                messages.error(request, 'Invalid user role.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')

@login_required
def home(request):
    """
    Redirect to appropriate dashboard based on user role
    """
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.is_faculty():
        return redirect('faculty_dashboard')
    else:
        return redirect('student_dashboard')

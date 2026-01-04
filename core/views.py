from django.shortcuts import render, redirect
from complains.models import Complaint
from django.db.models import Count, Q
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser


def home_view(request):
    # Redirect authenticated admins to admin dashboard
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard')
    
    # Get complaint statistics
    total_complaints = Complaint.objects.count()
    resolved_complaints = Complaint.objects.filter(status='RESOLVED').count()
    under_review_complaints = Complaint.objects.filter(
        Q(status='PENDING') | Q(status='IN_PROGRESS')
    ).count()
    
    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'under_review_complaints': under_review_complaints,
    }
    
    # Otherwise show home page
    return render(request, 'index.html', context)


def user_login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not (user.is_staff or user.is_superuser):
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Please use admin login.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'user_login.html')


def user_register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        district = request.POST.get('district')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    phone_number=phone_number,
                    district=district,
                    is_citizen=True
                )
                user.set_password(password1)
                user.save()
                login(request, user)
                messages.success(request, f'Welcome {user.username}! Your account has been created.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'user_register.html')


@login_required(login_url='user_login')
def dashboard_view(request):
    """User dashboard view"""
    # Get user's complaint statistics
    user_complaints = Complaint.objects.filter(citizen=request.user)
    total_complaints = user_complaints.count()
    resolved_complaints = user_complaints.filter(status='RESOLVED').count()
    pending_complaints = user_complaints.filter(status='PENDING').count()
    in_progress_complaints = user_complaints.filter(status='IN_PROGRESS').count()
    
    # Get recent complaints
    recent_complaints = user_complaints.order_by('-created_at')[:5]
    
    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'recent_complaints': recent_complaints,
    }
    
    return render(request, 'dashboard.html', context)


def user_logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

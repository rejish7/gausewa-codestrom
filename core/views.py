from django.shortcuts import render, redirect
from complains.models import Complaint
from django.db.models import Count, Q
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser, OTP
from accounts.otp_service import OTPService
from django.http import JsonResponse
from django.views.decorators.http import require_POST


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
    """User login view - Step 1: Enter phone number"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'user_login.html')


def otp_verify_view(request):
    """OTP verification page - Step 2: Enter OTP"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Get phone number from session
    phone_number = request.session.get('otp_phone_number', '')
    if not phone_number:
        messages.error(request, 'Please enter your phone number first.')
        return redirect('user_login')
    
    return render(request, 'otp.html', {'phone_number': phone_number})


@require_POST
def send_otp_view(request):
    """Send OTP to user's phone number"""
    phone_number = request.POST.get('phone_number', '').strip()
    
    if not phone_number:
        return JsonResponse({'success': False, 'message': 'Phone number is required.'}, status=400)
    
    # Check if user with this phone number exists
    try:
        user = CustomUser.objects.get(phone_number=phone_number)
        
        # Check if user is a regular citizen (not admin)
        if user.is_staff or user.is_superuser:
            return JsonResponse({'success': False, 'message': 'Please use admin login.'}, status=400)
        
        # Create OTP
        otp = OTP.create_otp(phone_number)
        
        # Send OTP via SMS
        if OTPService.send_otp(phone_number, otp.otp_code):
            # Store phone number in session for OTP verification page
            request.session['otp_phone_number'] = phone_number
            return JsonResponse({
                'success': True, 
                'message': f'OTP sent to {phone_number}. Valid for 5 minutes.',
                'redirect_url': '/otp-verify/'
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'Failed to send OTP. Please try again.'
            }, status=500)
            
    except CustomUser.DoesNotExist:
        # Store phone number in session for pre-filling registration form
        request.session['registration_phone_number'] = phone_number
        return JsonResponse({
            'success': False, 
            'message': 'No account found with this phone number.',
            'redirect_to_register': True,
            'redirect_url': '/register/'
        })


@require_POST
def verify_otp_view(request):
    """Verify OTP and log user in"""
    phone_number = request.POST.get('phone_number', '').strip()
    otp_code = request.POST.get('otp_code', '').strip()
    
    if not phone_number or not otp_code:
        return JsonResponse({
            'success': False, 
            'message': 'Phone number and OTP are required.'
        }, status=400)
    
    # Get the latest OTP for this phone number
    try:
        otp = OTP.objects.filter(
            phone_number=phone_number, 
            is_verified=False
        ).latest('created_at')
        
        if otp.verify(otp_code):
            # OTP is valid, log user in
            user = CustomUser.objects.get(phone_number=phone_number)
            login(request, user)
            return JsonResponse({
                'success': True, 
                'message': f'Welcome back, {user.username}!',
                'redirect_url': '/dashboard/'
            })
        else:
            if otp.attempts >= 3:
                return JsonResponse({
                    'success': False, 
                    'message': 'Too many failed attempts. Please request a new OTP.'
                }, status=400)
            else:
                return JsonResponse({
                    'success': False, 
                    'message': 'Invalid OTP. Please try again.'
                }, status=400)
                
    except OTP.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'No valid OTP found. Please request a new one.'
        }, status=404)
    except CustomUser.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'User not found.'
        }, status=404)


def user_register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Get phone number from session if redirected from login
    prefill_phone = request.session.get('registration_phone_number', '')
    
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
        elif CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already registered.')
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
                
                # Clear the session phone number
                if 'registration_phone_number' in request.session:
                    del request.session['registration_phone_number']
                
                login(request, user)
                messages.success(request, f'Welcome {user.username}! Your account has been created.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
    
    context = {
        'prefill_phone': prefill_phone
    }
    return render(request, 'user_register.html', context)


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

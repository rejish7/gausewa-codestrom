from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django import forms


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address'
    }))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone number (optional)'
    }))
    district = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'District (optional)'
    }))
    preferred_language = forms.ChoiceField(
        choices=CustomUser.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'district', 'preferred_language', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })


# Admin Views
def admin_register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        messages.warning(request, 'Please contact administrator for access.')
        logout(request)
        return redirect('admin_login')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Make the user staff and superuser by default for admin registration
            user.is_staff = True
            user.is_superuser = True
            user.save()
            login(request, user)
            messages.success(request, f'Welcome Admin {user.username}! Your admin account has been created.')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/admin_register.html', {'form': form})


def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        messages.warning(request, 'You do not have admin privileges.')
        logout(request)
        return redirect('admin_login')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f'Welcome Admin {user.username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'You do not have admin privileges.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/admin_login.html')


@login_required(login_url='admin_login')
def admin_dashboard_view(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        logout(request)
        return redirect('admin_login')
    
    # Get statistics
    from complains.models import Complaint
    from django.db.models import Count, Q
    
    try:
        total_users = CustomUser.objects.count()
        total_complaints = Complaint.objects.count()
        pending_complaints = Complaint.objects.filter(status='PENDING').count()
        resolved_complaints = Complaint.objects.filter(status='RESOLVED').count()
    except:
        total_users = CustomUser.objects.count()
        total_complaints = 0
        pending_complaints = 0
        resolved_complaints = 0
    
    # Get recent users
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    
    context = {
        'total_users': total_users,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'recent_users': recent_users,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


def admin_logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')

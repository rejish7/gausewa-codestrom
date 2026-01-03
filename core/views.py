from django.shortcuts import render, redirect


def home_view(request):
    # Redirect authenticated admins to admin dashboard
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard')
    
    # Otherwise show home page
    return render(request, 'core/home.html')

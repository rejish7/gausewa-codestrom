from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Complaint, ComplainsCategory
from accounts.models import CustomUser
import json
from datetime import datetime


@login_required
def submit_complaint_view(request):
    """Page to submit a new complaint"""
    categories = ComplainsCategory.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            category_id = request.POST.get('category')
            title = request.POST.get('title')
            description = request.POST.get('description')
            location_text = request.POST.get('location_text')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            image = request.FILES.get('image')
            voice_note = request.FILES.get('voice_note')
            
            complaint = Complaint.objects.create(
                citizen=request.user,
                category_id=category_id,
                title=title,
                description=description,
                location_text=location_text,
                latitude=latitude if latitude else None,
                longitude=longitude if longitude else None,
                image=image,
                voice_note=voice_note,
                status='PENDING'
            )
            
            messages.success(request, f'Your complaint #{str(complaint.complaint_id)[:8]} has been submitted successfully!')
            return redirect('my_complaints')
        except Exception as e:
            messages.error(request, f'Error submitting complaint: {str(e)}')
    
    context = {
        'categories': categories,
    }
    return render(request, 'complains/submit_complaint.html', context)


@login_required
def my_complaints_view(request):
    """View user's own complaints"""
    complaints = Complaint.objects.filter(citizen=request.user).order_by('-created_at')
    
    context = {
        'complaints': complaints,
    }
    return render(request, 'complains/my_complaints.html', context)


@login_required
def complaint_detail_view(request, complaint_id):
    """View details of a single complaint"""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id, citizen=request.user)
    
    context = {
        'complaint': complaint,
    }
    return render(request, 'complains/complaint_detail.html', context)


# API endpoints for offline sync
@csrf_exempt
@require_http_methods(["POST"])
def sync_offline_complaint(request):
    """
    Sync offline complaint - register user if needed by phone number
    """
    try:
        data = json.loads(request.body)
        
        phone_number = data.get('phone_number')
        category_id = data.get('category_id')
        title = data.get('title', '')
        description = data.get('description', '')
        location_text = data.get('location_text', '')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        client_created_at = data.get('client_created_at')
        
        if not phone_number or not category_id:
            return JsonResponse({'error': 'Phone number and category are required'}, status=400)
        
        # Check if user exists or create new user
        user = None
        created = False
        
        # Try to find user by phone number
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            # Create new user with phone number as username
            username = f"user_{phone_number}"
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"user_{phone_number}_{counter}"
                counter += 1
            
            user = CustomUser.objects.create_user(
                username=username,
                phone_number=phone_number,
                is_citizen=True
            )
            created = True
        
        # Create the complaint
        complaint = Complaint.objects.create(
            citizen=user,
            citizen_phone=phone_number,
            category_id=category_id,
            title=title,
            description=description,
            location_text=location_text,
            latitude=latitude if latitude else None,
            longitude=longitude if longitude else None,
            status='PENDING',
            is_offline_submission=True,
            client_created_at=client_created_at if client_created_at else None,
            synced_at=datetime.now()
        )
        
        return JsonResponse({
            'success': True,
            'complaint_id': str(complaint.complaint_id),
            'user_created': created,
            'message': 'Complaint synced successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_categories_api(request):
    """Get all active complaint categories"""
    categories = ComplainsCategory.objects.filter(is_active=True).values(
        'id', 'name_en', 'name_np', 'icon_name'
    )
    return JsonResponse({'categories': list(categories)})


@csrf_exempt
@require_http_methods(["POST"])
def check_user_exists(request):
    """Check if user exists by phone number"""
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return JsonResponse({'error': 'Phone number is required'}, status=400)
        
        exists = CustomUser.objects.filter(phone_number=phone_number).exists()
        
        return JsonResponse({
            'exists': exists,
            'phone_number': phone_number
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

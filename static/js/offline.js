/**
 * Offline Complaint Submission System
 * Handles offline data storage and sync when online
 */

// Configuration
const STORAGE_KEY = 'gausewa_offline_complaints';
const API_SYNC_URL = '/complaints/api/sync/';
const API_CHECK_USER_URL = '/complaints/api/check-user/';

// Check if online
function isOnline() {
    return navigator.onLine;
}

// Update UI based on connection status
function updateConnectionStatus() {
    const indicator = document.getElementById('offlineIndicator');
    if (indicator) {
        if (isOnline()) {
            indicator.classList.remove('show');
            syncOfflineComplaints();
        } else {
            indicator.classList.add('show');
        }
    }
}

// Get offline complaints from localStorage
function getOfflineComplaints() {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
}

// Save complaint to localStorage
function saveOfflineComplaint(complaint) {
    const complaints = getOfflineComplaints();
    complaints.push({
        ...complaint,
        id: Date.now(),
        timestamp: new Date().toISOString(),
        synced: false
    });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(complaints));
    console.log('Complaint saved offline:', complaint);
}

// Remove synced complaint from localStorage
function removeOfflineComplaint(id) {
    let complaints = getOfflineComplaints();
    complaints = complaints.filter(c => c.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(complaints));
}

// Sync offline complaints to server
async function syncOfflineComplaints() {
    const complaints = getOfflineComplaints();
    const unsynced = complaints.filter(c => !c.synced);
    
    if (unsynced.length === 0) {
        return;
    }
    
    console.log(`Syncing ${unsynced.length} offline complaints...`);
    
    for (const complaint of unsynced) {
        try {
            const response = await fetch(API_SYNC_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    phone_number: complaint.phone_number,
                    category_id: complaint.category_id,
                    title: complaint.title,
                    description: complaint.description,
                    location_text: complaint.location_text,
                    latitude: complaint.latitude,
                    longitude: complaint.longitude,
                    client_created_at: complaint.timestamp
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Complaint synced successfully:', result);
                removeOfflineComplaint(complaint.id);
                
                // Show success notification
                if (typeof showNotification === 'function') {
                    showNotification('Complaint synced successfully!', 'success');
                }
            } else {
                console.error('Failed to sync complaint:', response.statusText);
            }
        } catch (error) {
            console.error('Error syncing complaint:', error);
        }
    }
}

// Handle form submission
function handleComplaintSubmit(event) {
    const form = event.target;
    
    // If offline, save to localStorage
    if (!isOnline()) {
        event.preventDefault();
        
        const formData = new FormData(form);
        const complaint = {
            phone_number: formData.get('phone_number'),
            category_id: formData.get('category'),
            title: formData.get('title') || '',
            description: formData.get('description'),
            location_text: formData.get('location_text') || '',
            latitude: formData.get('latitude') || null,
            longitude: formData.get('longitude') || null
        };
        
        saveOfflineComplaint(complaint);
        
        alert('You are offline. Your complaint has been saved and will be submitted when you reconnect to the internet.');
        form.reset();
        return false;
    }
    
    // If online, proceed with normal submission
    return true;
}

// Initialize offline support
function initOfflineSupport() {
    // Update connection status on load
    updateConnectionStatus();
    
    // Listen for connection changes
    window.addEventListener('online', () => {
        console.log('Connection restored');
        updateConnectionStatus();
        syncOfflineComplaints();
    });
    
    window.addEventListener('offline', () => {
        console.log('Connection lost');
        updateConnectionStatus();
    });
    
    // Attach to complaint form if it exists
    const complaintForm = document.getElementById('complaintForm');
    if (complaintForm) {
        complaintForm.addEventListener('submit', handleComplaintSubmit);
    }
    
    if (isOnline()) {
        setTimeout(syncOfflineComplaints, 2000);
    }
    

    displayOfflineComplaintsCount();
}

// Display count of offline complaints
function displayOfflineComplaintsCount() {
    const complaints = getOfflineComplaints();
    const unsynced = complaints.filter(c => !c.synced);
    
    if (unsynced.length > 0) {
        console.log(`You have ${unsynced.length} complaint(s) waiting to be synced.`);
        
        // Create a badge or notification
        const badge = document.createElement('div');
        badge.id = 'offlineComplaintsBadge';
        badge.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #f59e0b;
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            font-weight: 600;
            cursor: pointer;
            z-index: 1000;
        `;
        badge.innerHTML = `<i class="fas fa-sync"></i> ${unsynced.length} complaint(s) pending sync`;
        badge.onclick = syncOfflineComplaints;
        
        document.body.appendChild(badge);
    }
}

// Show notification helper
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1001;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initOfflineSupport);
} else {
    initOfflineSupport();
}

// Register Service Worker for offline support
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    });
}
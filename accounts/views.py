from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm

# ══════════════════════════════
# AUTH VIEWS
# ══════════════════════════════

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Akun berhasil dibuat!')
        return redirect('dashboard')
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        # Kalau sudah login, arahkan sesuai role
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        # Redirect sesuai role setelah login
        if user.is_staff or user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


# ══════════════════════════════
# USER VIEWS
# ══════════════════════════════

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import User


@login_required
def profile_view(request):
    from surplus.models import Transaction, Review
    transactions = Transaction.objects.filter(buyer=request.user).order_by('-transaction_date')[:5]
    listings = request.user.listings.all().order_by('-created_at')[:5]
    reviews = Review.objects.filter(reviewee=request.user).order_by('-created_at')[:5]
    return render(request, 'accounts/profile.html', {
        'transactions': transactions,
        'listings': listings,
        'reviews': reviews,
    })


@login_required
def profile_edit_view(request):
    from .forms import ProfileEditForm
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profil berhasil diupdate!')
        return redirect('profile')
    return render(request, 'accounts/profile_edit.html', {'form': form})


def public_profile_view(request, username):
    from surplus.models import Review
    profile_user = get_object_or_404(User, username=username)
    listings = profile_user.listings.filter(status='aktif').order_by('-created_at')[:5]
    reviews = Review.objects.filter(reviewee=profile_user).order_by('-created_at')[:5]
    return render(request, 'accounts/public_profile.html', {
        'profile_user': profile_user,
        'listings': listings,
        'reviews': reviews,
    })


# ══════════════════════════════
# ADMIN VIEWS
# ══════════════════════════════

from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def admin_dashboard_view(request):
    from surplus.models import SurplusListing, Transaction, Review
    from food.models import FoodItem
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    import json

    total_users = User.objects.filter(is_superuser=False).count()
    total_listings = SurplusListing.objects.count()
    active_listings = SurplusListing.objects.filter(status='aktif').count()
    total_transactions = Transaction.objects.count()
    completed_transactions = Transaction.objects.filter(status='completed').count()
    total_donasi = SurplusListing.objects.filter(type='donasi').count()
    donasi_pct = round((total_donasi / total_listings * 100) if total_listings > 0 else 0)

    # 5 listing terbaru (aktif + pending)
    recent_listings = SurplusListing.objects.order_by('-created_at')[:5]
    total_all_listings = SurplusListing.objects.count()
    makanan_selamat = Transaction.objects.filter(status='completed').count()

    all_users = User.objects.filter(is_superuser=False).order_by('-date_joined')[:8]

    # Chart 7 hari terakhir
    today = timezone.now().date()
    chart_labels = []
    chart_data = []
    days_id = ['Sen','Sel','Rab','Kam','Jum','Sab','Min']
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Transaction.objects.filter(transaction_date__date=day).count()
        chart_labels.append(days_id[day.weekday()])
        chart_data.append(count)

    return render(request, 'accounts/admin_dashboard.html', {
        'total_users': total_users,
        'total_listings': total_listings,
        'active_listings': active_listings,
        'total_transactions': total_transactions,
        'completed_transactions': completed_transactions,
        'recent_listings': recent_listings,
        'total_all_listings': total_all_listings,
        'all_users': all_users,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'donasi_pct': donasi_pct,
        'makanan_selamat': makanan_selamat,
        'total_donasi': total_donasi,
    })


@staff_member_required
def admin_user_ban_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        status = 'diaktifkan' if user.is_active else 'dinonaktifkan'
        messages.success(request, f'User {user.username} berhasil {status}!')
    return redirect('admin_dashboard')


@staff_member_required
def admin_listing_action_view(request, pk):
    from surplus.models import SurplusListing
    listing = get_object_or_404(SurplusListing, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'tolak':
            listing.status = 'dibatalkan'
            listing.save()
            messages.success(request, f'Listing {listing.title} berhasil ditolak!')
        elif action == 'setujui':
            listing.status = 'aktif'
            listing.save()
            messages.success(request, f'Listing {listing.title} disetujui!')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

@staff_member_required
def admin_all_listings_view(request):
    from surplus.models import SurplusListing
    listings = SurplusListing.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        listings = listings.filter(status=status_filter)
    return render(request, 'accounts/admin_listings.html', {
        'listings': listings,
        'status_filter': status_filter,
    })

@staff_member_required  
def admin_all_users_view(request):
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'accounts/admin_users.html', {'users': users})

@staff_member_required
def admin_all_transactions_view(request):
    from surplus.models import Transaction
    transactions = Transaction.objects.all().order_by('-transaction_date')
    status_filter = request.GET.get('status', '')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    return render(request, 'accounts/admin_transactions.html', {
        'transactions': transactions,
        'status_filter': status_filter,
    })
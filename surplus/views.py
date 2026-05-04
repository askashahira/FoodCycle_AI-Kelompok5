from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SurplusListing, Transaction, Review
from .forms import SurplusListingForm, ReviewForm

# Create your views here.
def surplus_list_view(request):
    listings = SurplusListing.objects.filter(status='aktif').order_by('-created_at')
    type_filter = request.GET.get('type', '')
    if type_filter:
        listings = listings.filter(type=type_filter)

    # Filter radius kalau user login dan punya koordinat
    user_lat = None
    user_lon = None
    listings_with_distance = []

    if request.user.is_authenticated and request.user.latitude and request.user.longitude:
        user_lat = float(request.user.latitude)
        user_lon = float(request.user.longitude)
        for listing in listings:
            if listing.latitude and listing.longitude:
                distance = haversine(user_lat, user_lon, listing.latitude, listing.longitude)
                if distance <= float(listing.radius_km):
                    listings_with_distance.append({
                        'listing': listing,
                        'distance': round(distance, 2)
                    })
            else:
                listings_with_distance.append({
                    'listing': listing,
                    'distance': None
                })
    else:
        listings_with_distance = [{'listing': l, 'distance': None} for l in listings]

    # Data untuk peta (semua listing yang punya koordinat)
    map_listings = []
    for item in listings_with_distance:
        l = item['listing']
        if l.latitude and l.longitude:
            map_listings.append({
                'id': l.pk,
                'title': l.title,
                'type': l.type,
                'price': str(l.price) if l.price else 'Gratis',
                'lat': float(l.latitude),
                'lon': float(l.longitude),
                'url': f'/surplus/{l.pk}/',
                'distance': item['distance'],
            })

    import json
    return render(request, 'surplus/list.html', {
        'listings_with_distance': listings_with_distance,
        'type_filter': type_filter,
        'user_lat': user_lat,
        'user_lon': user_lon,
        'map_listings_json': json.dumps(map_listings),
        'has_location': bool(user_lat and user_lon),
    })

def surplus_detail_view(request, pk):
    listing = get_object_or_404(SurplusListing, pk=pk)
    return render(request, 'surplus/detail.html', {'listing': listing})

@login_required
def surplus_create_view(request):
    form = SurplusListingForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        listing = form.save(commit=False)
        listing.user = request.user
        # Ambil koordinat dari user
        if request.user.latitude and request.user.longitude:
            listing.latitude = request.user.latitude
            listing.longitude = request.user.longitude
        listing.save()
        messages.success(request, 'Listing berhasil dibuat!')
        return redirect('surplus_list')
    return render(request, 'surplus/form.html', {'form': form, 'title': 'Buat Listing Surplus'})

@login_required
def surplus_edit_view(request, pk):
    listing = get_object_or_404(SurplusListing, pk=pk, user=request.user)
    form = SurplusListingForm(request.POST or None, request.FILES or None, instance=listing)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Listing berhasil diupdate!')
        return redirect('surplus_list')
    return render(request, 'surplus/form.html', {'form': form, 'title': 'Edit Listing'})

@login_required
def surplus_delete_view(request, pk):
    listing = get_object_or_404(SurplusListing, pk=pk, user=request.user)
    if request.method == 'POST':
        listing.status = 'dibatalkan'
        listing.save()
        messages.success(request, 'Listing berhasil dibatalkan!')
        return redirect('my_listings')
    return render(request, 'surplus/confirm_delete.html', {'listing': listing})

@login_required
def my_listings_view(request):
    listings = SurplusListing.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'surplus/my_listings.html', {'listings': listings})

@login_required
def order_view(request, pk):
    listing = get_object_or_404(SurplusListing, pk=pk, status='aktif')
    if listing.user == request.user:
        messages.error(request, 'Kamu tidak bisa memesan listing milikmu sendiri!')
        return redirect('surplus_detail', pk=pk)
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        Transaction.objects.create(
            listing=listing,
            buyer=request.user,
            notes=notes,
        )
        listing.status = 'terjual'
        listing.save()
        messages.success(request, 'Pesanan berhasil dibuat!')
        return redirect('my_purchases')
    return render(request, 'surplus/order.html', {'listing': listing})

@login_required
def my_purchases_view(request):
    purchases = Transaction.objects.filter(buyer=request.user).order_by('-transaction_date')
    return render(request, 'surplus/my_purchases.html', {'purchases': purchases})

@login_required
def give_review_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, buyer=request.user)
    if hasattr(transaction, 'review'):
        messages.error(request, 'Kamu sudah memberikan review!')
        return redirect('my_purchases')
    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.transaction = transaction
        review.reviewer = request.user
        review.reviewee = transaction.listing.user
        review.save()
        # Update avg_rating penjual
        reviewee = transaction.listing.user
        all_reviews = Review.objects.filter(reviewee=reviewee)
        reviewee.avg_rating = sum(r.rating for r in all_reviews) / all_reviews.count()
        reviewee.save()
        messages.success(request, 'Review berhasil diberikan!')
        return redirect('my_purchases')
    return render(request, 'surplus/review_form.html', {'form': form, 'transaction': transaction})

import math

def haversine(lat1, lon1, lat2, lon2):
    """Hitung jarak antara 2 koordinat dalam km"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

@login_required
def my_orders_view(request):
    """Pesanan masuk untuk penjual"""
    incoming = Transaction.objects.filter(
        listing__user=request.user
    ).order_by('-transaction_date')
    return render(request, 'surplus/my_orders.html', {'incoming': incoming})

@login_required
def order_action_view(request, pk):
    """Penjual accept/reject pesanan"""
    transaction = get_object_or_404(Transaction, pk=pk, listing__user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            transaction.status = 'confirmed'
            transaction.save()
            messages.success(request, 'Pesanan berhasil diterima!')
        elif action == 'reject':
            transaction.status = 'cancelled'
            transaction.save()
            # Aktifkan kembali listing
            transaction.listing.status = 'aktif'
            transaction.listing.save()
            messages.success(request, 'Pesanan ditolak.')
        elif action == 'complete':
            transaction.status = 'completed'
            transaction.save()
            messages.success(request, 'Transaksi selesai!')
    return redirect('my_orders')
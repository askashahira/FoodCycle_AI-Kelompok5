from django import forms
from .models import SurplusListing, Review

class SurplusListingForm(forms.ModelForm):
    expired_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Batas Waktu Listing'
    )

    class Meta:
        model = SurplusListing
        fields = ['title', 'description', 'type', 'price', 'photo', 'radius_km', 'expired_at']
        labels = {
            'title': 'Judul Listing',
            'description': 'Deskripsi Makanan',
            'type': 'Tipe',
            'price': 'Harga (kosongkan jika donasi)',
            'photo': 'Foto Makanan',
            'radius_km': 'Radius Distribusi (km)',
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Rating (1-5)',
            'comment': 'Komentar',
        }
from django import forms
from .models import SurplusListing, Review

class SurplusListingForm(forms.ModelForm):
    expired_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Batas Waktu Listing'
    )

    class Meta:
        model = SurplusListing
        fields = ['title', 'description', 'type', 'price', 'photo',
                  'quantity', 'unit', 'radius_km', 'expired_at']
        labels = {
            'title': 'Judul Listing',
            'description': 'Deskripsi Makanan',
            'type': 'Tipe',
            'price': 'Harga per unit (kosongkan jika donasi)',
            'photo': 'Foto Makanan',
            'quantity': 'Jumlah Tersedia',
            'unit': 'Satuan',
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
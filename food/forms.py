from django import forms
from .models import FoodItem

class FoodItemForm(forms.ModelForm):
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Estimasi Tanggal Kedaluwarsa'
    )
    
    class Meta:
        model = FoodItem
        fields = ['name', 'category', 'quantity', 'unit', 'expiry_date', 'notes']
        labels = {
            'name': 'Nama Bahan Makanan',
            'category': 'Kategori',
            'quantity': 'Jumlah',
            'unit': 'Satuan (kg, gram, pcs, liter)',
            'notes': 'Catatan',
        }
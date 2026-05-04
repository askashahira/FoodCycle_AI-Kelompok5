from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from surplus.models import SurplusListing
import random

class Command(BaseCommand):
    help = 'Seed dummy data'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # buat user dummy
        user, _ = User.objects.get_or_create(
            username='user_demo',
            defaults={'email': 'demo@gmail.com'}
        )
        user.set_password('123456')
        user.save()

        # lokasi Banda Aceh
        locations = [
            (5.5483, 95.3238),
            (5.5520, 95.3200),
            (5.5450, 95.3300),
            (5.5500, 95.3150),
            (5.5530, 95.3250),
        ]

        titles = [
            "Nasi Goreng Sisa",
            "Roti Belum Terjual",
            "Ayam Geprek Sisa",
            "Sayur Gratis",
            "Donat Hari Ini",
        ]

        descriptions = [
            "Masih hangat dan layak konsumsi",
            "Segera diambil sebelum basi",
            "Baru dimasak pagi ini",
            "Sisa event, masih banyak",
            "Fresh hari ini",
        ]

        for i in range(5):
            lat, lon = locations[i]

            # random type
            listing_type = random.choice(['jual', 'donasi'])

            # harga hanya kalau jual
            price = random.randint(3000, 25000) if listing_type == 'jual' else 0

            if not SurplusListing.objects.filter(title=titles[i]).exists():
                SurplusListing.objects.create(
                    user=user,
                    title=titles[i],
                    description=random.choice(descriptions),
                    type=listing_type,
                    price=price,
                    quantity=random.choice([1, 2, 3, 5, 10]),
                    unit='porsi',
                    latitude=lat,
                    longitude=lon,
                )

        self.stdout.write(self.style.SUCCESS('Dummy data created!'))
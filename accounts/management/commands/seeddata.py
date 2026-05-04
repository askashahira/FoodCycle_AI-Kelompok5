from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from surplus.models import SurplusListing
import random


class Command(BaseCommand):
    help = 'Seed dummy data untuk demo'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # ✅ Buat / ambil user demo
        user, created = User.objects.get_or_create(
            username='user_demo',
            defaults={'email': 'demo@gmail.com'}
        )

        if created:
            user.set_password('123456')
            user.save()
            self.stdout.write(self.style.SUCCESS('User demo dibuat'))
        else:
            self.stdout.write('User demo sudah ada')

        # 📍 Lokasi sekitar Banda Aceh
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
            "Masih hangat, ambil cepat ya!",
            "Sisa jual hari ini, masih fresh",
            "Gratis untuk yang membutuhkan 🙏",
            "Baru dimasak, tidak habis terjual",
            "Masih layak konsumsi, sayang dibuang",
        ]

        created_count = 0

        for i in range(len(locations)):
            lat, lon = locations[i]

            # ⛔ Hindari duplikat
            if SurplusListing.objects.filter(title=titles[i]).exists():
                continue

            listing_type = random.choice(['jual', 'donasi'])

            SurplusListing.objects.create(
                user=user,
                title=titles[i],
                description=random.choice(descriptions),

                # 🔥 Random type
                type=listing_type,

                # 🔥 Harga hanya kalau jual
                price=random.randint(3000, 25000) if listing_type == 'jual' else 0,

                quantity=random.choice([1, 2, 3, 5, 10]),
                unit='porsi',

                latitude=lat,
                longitude=lon,

                # 🔥 WAJIB (fix error kamu)
                expired_at=timezone.now() + timedelta(hours=random.randint(6, 48)),
            )

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'{created_count} data berhasil ditambahkan!'))
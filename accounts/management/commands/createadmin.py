from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create or update default admin user'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@gmail.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        # 🔥 INI KUNCINYA
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS('Admin created'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin updated (password reset)'))
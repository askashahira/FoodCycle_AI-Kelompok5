from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [('user', 'User'), ('admin', 'Admin')]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    @property
    def display_role(self):
        if self.is_staff or self.is_superuser:
            return 'Admin'
        return 'Pengguna'

    def __str__(self):
        return self.email
    
    
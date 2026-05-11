from django.db import models
from django.conf import settings

# Create your models here.
class FoodItem(models.Model):
    CATEGORY_CHOICES = [
        ('sayuran', 'Sayuran'),
        ('buah', 'Buah'),
        ('protein', 'Protein'),
        ('dairy', 'Dairy'),
        ('bumbu', 'Bumbu'),
        ('karbohidrat', 'Karbohidrat'),
        ('lainnya', 'Lainnya'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)  # kg, gram, pcs, liter
    expiry_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def is_near_expiry(self):
        from datetime import date, timedelta
        return self.expiry_date <= date.today() + timedelta(days=3)

    def is_expired(self):
        from datetime import date
        return self.expiry_date < date.today()
    
class AIRecommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipe_name = models.CharField(max_length=200)
    ingredients_used = models.TextField()
    instructions = models.TextField()
    nutrition_estimate = models.TextField()
    price_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    servings = models.IntegerField(default=2)
    servings_description = models.CharField(max_length=200, blank=True)
    leftover_potential = models.CharField(max_length=300, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipe_name} ({self.user.username})"
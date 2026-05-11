from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .models import FoodItem
from .forms import FoodItemForm
from .services import get_recipe_recommendations
from .models import FoodItem, AIRecommendation

# Create your views here.
def home_view(request):
    return render(request, 'home.html')

@login_required
def dashboard_view(request):
    from surplus.models import Transaction, SurplusListing, Review
    from django.utils import timezone
    from datetime import timedelta

    items = FoodItem.objects.filter(user=request.user)
    near_expiry = [i for i in items if i.is_near_expiry() and not i.is_expired()]
    expired = [i for i in items if i.is_expired()]

    # ── Aktivitas Terbaru ──────────────────────────────────────────
    # Gabungkan beberapa sumber aktivitas, urutkan by waktu
    activities = []

    # Resep AI yang pernah di-generate
    recent_recipes = AIRecommendation.objects.filter(
        user=request.user
    ).order_by('-generated_at')[:3]
    for r in recent_recipes:
        activities.append({
            'icon': '🤖',
            'title': r.recipe_name,
            'meta': f'Resep AI · {r.generated_at.strftime("%d %b, %H:%M")}',
            'badge': None,
            'badge_class': '',
            'time': r.generated_at,
        })

    # Listing surplus yang dibuat user
    recent_listings = SurplusListing.objects.filter(
        user=request.user
    ).order_by('-created_at')[:3]
    for l in recent_listings:
        badge = 'Jual' if l.type == 'jual' else 'Donasi'
        badge_class = 'type-jual' if l.type == 'jual' else 'type-donasi'
        activities.append({
            'icon': '📝',
            'title': l.title,
            'meta': f'Surplus Listing · {l.created_at.strftime("%d %b, %H:%M")}',
            'badge': badge,
            'badge_class': badge_class,
            'time': l.created_at,
        })

    # Transaksi selesai sebagai pembeli
    recent_purchases = Transaction.objects.filter(
        buyer=request.user,
        status='completed'
    ).order_by('-transaction_date')[:3]
    for t in recent_purchases:
        activities.append({
            'icon': '🛍️',
            'title': t.listing.title,
            'meta': f'Pembelian Selesai · {t.transaction_date.strftime("%d %b, %H:%M")}',
            'badge': 'Selesai',
            'badge_class': 'expiry-ok',
            'time': t.transaction_date,
        })

    # Urutkan semua aktivitas by waktu terbaru, ambil 5
    activities.sort(key=lambda x: x['time'], reverse=True)
    activities = activities[:5]

    # ── Dampak Lingkungan ──────────────────────────────────────────
    # Hitung dari transaksi completed (sebagai penjual maupun pembeli)
    completed_as_seller = Transaction.objects.filter(
        listing__user=request.user,
        status='completed'
    ).count()
    completed_as_buyer = Transaction.objects.filter(
        buyer=request.user,
        status='completed'
    ).count()
    total_saved = completed_as_seller + completed_as_buyer

    # Estimasi dampak per transaksi (rata-rata 0.5kg makanan per transaksi)
    food_saved_kg = round(total_saved * 0.5, 1)
    co2_avoided_kg = round(food_saved_kg * 2.5, 1)   # ~2.5 kg CO2 per kg makanan
    water_avoided_l = round(food_saved_kg * 50, 0)    # ~50 liter air per kg makanan

    # Progress bar max (target bulanan)
    co2_max = max(co2_avoided_kg, 10)
    water_max = max(water_avoided_l, 500)
    food_max = max(food_saved_kg, 5)

    # ── Rating ────────────────────────────────────────────────────
    avg_rating = getattr(request.user, 'avg_rating', None)
    if avg_rating:
        avg_rating = round(float(avg_rating), 1)

    context = {
        'total_items': items.count(),
        'near_expiry': near_expiry,
        'expired': expired,
        'near_expiry_count': len(near_expiry),
        'avg_rating': avg_rating or '—',
        # Aktivitas
        'activities': activities,
        # Dampak lingkungan
        'food_saved_kg': food_saved_kg,
        'co2_avoided_kg': co2_avoided_kg,
        'water_avoided_l': int(water_avoided_l),
        'co2_pct': min(int(co2_avoided_kg / co2_max * 100), 100),
        'water_pct': min(int(water_avoided_l / water_max * 100), 100),
        'food_pct': min(int(food_saved_kg / food_max * 100), 100),
    }
    return render(request, 'dashboard.html', context)

@login_required
def food_list_view(request):
    items = FoodItem.objects.filter(user=request.user).order_by('expiry_date')
    return render(request, 'food/list.html', {'items': items})

@login_required
def food_add_view(request):
    form = FoodItemForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        item.save()
        messages.success(request, f'{item.name} berhasil ditambahkan!')
        return redirect('food_list')
    return render(request, 'food/form.html', {'form': form, 'title': 'Tambah Bahan Makanan'})

@login_required
def food_edit_view(request, pk):
    item = get_object_or_404(FoodItem, pk=pk, user=request.user)
    form = FoodItemForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{item.name} berhasil diupdate!')
        return redirect('food_list')
    return render(request, 'food/form.html', {'form': form, 'title': 'Edit Bahan Makanan'})

@login_required
def food_delete_view(request, pk):
    item = get_object_or_404(FoodItem, pk=pk, user=request.user)
    if request.method == 'POST':
        name = item.name
        item.delete()
        messages.success(request, f'{name} berhasil dihapus!')
        return redirect('food_list')
    return render(request, 'food/confirm_delete.html', {'item': item})

@login_required
def recipe_view(request):
    # Ambil semua bahan user, near-expiry duluan
    all_items = FoodItem.objects.filter(user=request.user).order_by('expiry_date')
    near_expiry = [i for i in all_items if i.is_near_expiry() and not i.is_expired()]
    other_items = [i for i in all_items if not i.is_near_expiry() and not i.is_expired()]
    
    recipes = []
    error = None

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_items')
        
        if not selected_ids:
            error = 'Pilih minimal 1 bahan makanan!'
        else:
            selected_items = FoodItem.objects.filter(pk__in=selected_ids, user=request.user)
            ingredients = [
                {
                    'name': item.name,
                    'quantity': str(item.quantity),
                    'unit': item.unit,
                }
                for item in selected_items
            ]
            
            recipes = get_recipe_recommendations(ingredients)
            
            if recipes:
                saved_recipes = []
                for recipe in recipes:
                    saved = AIRecommendation.objects.create(
                        user=request.user,
                        recipe_name=recipe.get('recipe_name', ''),
                        ingredients_used=recipe.get('ingredients_used', ''),
                        instructions=recipe.get('instructions', ''),
                        nutrition_estimate=recipe.get('nutrition_estimate', ''),
                        price_estimate=recipe.get('price_estimate', 0),
                        servings=recipe.get('servings', 2),
                        servings_description=recipe.get('servings_description', ''),
                        leftover_potential=recipe.get('leftover_potential', ''),
                    )
                    saved_recipes.append(saved)
                recipes = saved_recipes
            else:
                error = 'Gagal generate resep. Coba lagi!'

    return render(request, 'food/recipe.html', {
        'near_expiry': near_expiry,
        'other_items': other_items,
        'recipes': recipes,
        'error': error,
    })

@login_required  
def recipe_history_view(request):
    history = AIRecommendation.objects.filter(user=request.user).order_by('-generated_at')[:20]
    return render(request, 'food/recipe_history.html', {'history': history})

@login_required
def recipe_detail_view(request, pk):
    from .models import AIRecommendation
    recipe = get_object_or_404(AIRecommendation, pk=pk, user=request.user)
    
    # Parse langkah masak di views, bukan di template
    steps = []
    if recipe.instructions:
        parts = recipe.instructions.split('Langkah')
        for part in parts:
            part = part.strip()
            if part:
                # Hapus angka di depan seperti "1:" atau "1 :"
                import re
                clean = re.sub(r'^\d+\s*[:.]?\s*', '', part).strip()
                if clean:
                    steps.append(clean)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_stock':
            import re
            ingredient_names = [i.strip().lower() for i in recipe.ingredients_used.split(',')]
            updated = []
            for name in ingredient_names:
                clean_name = re.sub(r'\(.*?\)', '', name).strip()
                items = FoodItem.objects.filter(user=request.user, name__icontains=clean_name)
                for item in items:
                    item.quantity = max(0, float(item.quantity) - 1)
                    item.save()
                    updated.append(item.name)
            messages.success(request, f'✅ Stok berhasil diperbarui! Sekarang kamu bisa jual sisa masakan.')
            return redirect('recipe_detail', pk=pk)  # ← tetap di halaman ini
    
    return render(request, 'food/recipe_detail.html', {
        'recipe': recipe,
        'steps': steps,
    })
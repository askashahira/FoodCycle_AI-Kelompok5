from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('stok/', views.food_list_view, name='food_list'),
    path('stok/tambah/', views.food_add_view, name='food_add'),
    path('stok/edit/<int:pk>/', views.food_edit_view, name='food_edit'),
    path('stok/hapus/<int:pk>/', views.food_delete_view, name='food_delete'),
    path('resep/', views.recipe_view, name='recipe'),
    path('resep/riwayat/', views.recipe_history_view, name='recipe_history'),
    path('resep/detail/<int:pk>/', views.recipe_detail_view, name='recipe_detail'),

]
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),
    path('profil/edit/', views.profile_edit_view, name='profile_edit'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/ban/<int:pk>/', views.admin_user_ban_view, name='admin_user_ban'),
    path('admin-dashboard/listing/<int:pk>/', views.admin_listing_action_view, name='admin_listing_action'),
    path('admin-dashboard/semua-listing/', views.admin_all_listings_view, name='admin_all_listings'),
    path('admin-dashboard/semua-pengguna/', views.admin_all_users_view, name='admin_all_users'),
    path('pengguna/<str:username>/', views.public_profile_view, name='public_profile'),
    path('admin-dashboard/transaksi/', views.admin_all_transactions_view, name='admin_all_transactions'),
    
]
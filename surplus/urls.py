from django.urls import path
from . import views

urlpatterns = [
    path('', views.surplus_list_view, name='surplus_list'),
    path('buat/', views.surplus_create_view, name='surplus_create'),
    path('<int:pk>/', views.surplus_detail_view, name='surplus_detail'),
    path('<int:pk>/edit/', views.surplus_edit_view, name='surplus_edit'),
    path('<int:pk>/hapus/', views.surplus_delete_view, name='surplus_delete'),
    path('<int:pk>/pesan/', views.order_view, name='order'),
    path('listing-saya/', views.my_listings_view, name='my_listings'),
    path('pembelian-saya/', views.my_purchases_view, name='my_purchases'),
    path('review/<int:pk>/', views.give_review_view, name='give_review'),
    path('pesanan-masuk/', views.my_orders_view, name='my_orders'),
    path('pesanan-masuk/<int:pk>/aksi/', views.order_action_view, name='order_action'),
]
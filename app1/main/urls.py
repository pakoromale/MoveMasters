from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart, name='cart'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('checkout/', views.checkout, name='checkout'),
]
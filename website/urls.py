from django.urls import path
from. import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('branches/', views.branches, name='branches'),
    path('contact/', views.contact, name='contact'),
    path('products/' , views.products, name= 'products'),
    path('privacy/', views.privacy, name= 'privacy'),
]

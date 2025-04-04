from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home,name ="home" ),
    path('register/',views.register, name="register"),
    path('login/',views.loginPage, name="login"),
    path('search/',views.search, name="search"),
    path('logout/',views.logoutPage, name="logout"),
    path('cart/',views.cart, name="cart"),
    path('checkout/',views.checkout, name="checkout"),
    path('update_item/',views.updateItem, name="update_item"),
    path('tenant/',views.tenant, name="tenant"),
    path('tenant_landing/',views.tenant_landing, name="tenant_landing"),
    path('tenant_landing/<int:tenant_id>/', views.tenant_landing, name="tenant_landing"),
]

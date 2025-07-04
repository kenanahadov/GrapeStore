from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from store import views as store_views

urlpatterns=[
    path('admin/',admin.site.urls),
    path('login/',auth_views.LoginView.as_view(template_name='registration/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    path('register/',store_views.register,name='register'),
    path('dashboard/',store_views.dashboard,name='dashboard'),
    path('',include('store.urls')),
]

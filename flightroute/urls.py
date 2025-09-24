"""
URL configuration for flightroute project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from aiport import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.HomeView.as_view(),name='home'),
    path('route/',views.RoutView.as_view(),name='route'),
    path('nthnode/', views.Nhroute.as_view(), name='nthnode'),
    path('longest_route/', views.longest_route_view, name='longest_route'),
]

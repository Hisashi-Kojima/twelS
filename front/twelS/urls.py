# -*- coding: utf-8 -*-
"""twelS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # superuserを作っていないが，一応adminのpathを推測できないものにする
    path('4KkEH5XsLQRC/', admin.site.urls),
    path('', include('search.urls')),
    path('login', include('login.urls')), # login

# ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # this line is executed when DEBUG is set to True.
]

# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

from django.urls import path

from .views import index, robots_txt, coming_soon, privacy_policy

urlpatterns = [
    path('', coming_soon),
    path('314159265358979/', index),
    path('privacypolicy/', privacy_policy, name='privacy_policy'),
    path('robots.txt', robots_txt),
]

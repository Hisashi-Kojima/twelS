# -*- coding: utf-8 -*-
"""module description
"""

from django.urls import path

from front.search.views import index, robots_txt, coming_soon, privacy_policy

app_name='search'

urlpatterns = [
    path('', coming_soon),
    path('314159265358979/', index, name='index'),
    path('privacypolicy/', privacy_policy, name='privacy_policy'),
    path('robots.txt', robots_txt),
]

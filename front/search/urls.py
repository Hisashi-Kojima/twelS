# -*- coding: utf-8 -*-
"""module description
"""

from django.urls import path

from front.search.views import index, robots_txt, privacy_policy, feedback, report

app_name='search'

urlpatterns = [
    path('', index, name='index'),
    path('privacypolicy/', privacy_policy, name='privacy_policy'),
    path('feedback/', feedback, name='feedback'),
    path('report/', report, name='report'),
    path('robots.txt', robots_txt),
]

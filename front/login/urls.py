from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('/', views.Top.as_view(), name='top'),
    path('/login/', views.Login.as_view(), name='login'),
    path('/logout/', views.Logout.as_view(), name='logout'),
    path('/user_create/', views.UserCreate.as_view(), name='user_create'),
    path('/user_create/done', views.UserCreateDone.as_view(), name='user_create_done'),
    path('/user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('/try/', views.Try.as_view(), name='try'),
]

from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('user/<int:pk>/', views.UserPage.as_view(), name='user'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('email_login/', views.EmailLogin.as_view(), name='email_login'),
    path('email_login/sent', views.EmailLoginSent.as_view(), name="email_login_sent"),
    path('email_login/complete/<token>/', views.EmailLoginComplete.as_view(), name='email_login_complete'),
    path('token_error/', views.TokenErrorView.as_view(), name='token_error')
]

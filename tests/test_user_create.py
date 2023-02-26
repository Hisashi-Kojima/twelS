# import os
# import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'front.twelS.settings')

# django.setup()

from django.contrib.auth import get_user_model
from front.login.forms import CustomUserCreateForm
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.core.signing import loads

User = get_user_model()


class UserCreateTest(TestCase):
    def setUp(self) -> None:
        url = reverse('login:user_create')
        self.response = self.client.get(url)
    
    def test_user_create_status_code(self):
        """ステータスコード200を確認"""
        self.assertEquals(self.response.status_code, 200)
    
    def test_csrf(self):
        """csrfトークンを含むこと"""
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    
    def test_contains_form(self):
        """フォームの確認"""
        form = self.response.context.get('form')
        self.assertIsInstance(form, CustomUserCreateForm)
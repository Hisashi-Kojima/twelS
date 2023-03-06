import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'front.twelS.settings')

django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.core.signing import loads

User = get_user_model()


class UserCreateTest(TestCase):
    def setUp(self) -> None:
        self.response = self.client.get(reverse('login:user_create'))

    def test_user_create_status_code(self):
        """ステータスコード200を確認"""
        self.assertEquals(self.response.status_code, 200)

    def test_csrf(self):
        """csrfトークンを含むこと"""
        self.assertContains(self.response, 'csrfmiddlewaretoken')


class SuccessfulUserCreateTests(TestCase):
    """ユーザー登録成功時のテスト"""
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')  # メールのテストのために上書き
    def setUp(self):
        url = reverse('login:user_create')
        data = {
            'email': 'test@edu.cc.saga-u.ac.jp',
            'password': 'TestPass1',
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する
        self.response = self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000/')

    def test_redirection(self):
        '''リダイレクトURLのテスト'''
        self.home_url = reverse('login:user_create_done')
        self.assertRedirects(self.response, self.home_url)

    def test_mail(self):
        """メールテスト"""
        self.assertEqual(len(mail.outbox), 1)  # 1通のメールが送信されていること
        self.assertEqual(mail.outbox[0].from_email, '22801001@edu.cc.saga-u.ac.jp')  # 送信元
        self.assertEqual(mail.outbox[0].to, ['test@edu.cc.saga-u.ac.jp'])  # 宛先

        body_lines = mail.outbox[0].body.split('\n')
        url = body_lines[6]  # メール本文から認証urlを取得
        redirect(url)

    def test_usercreate_complete_redirect(self):
        """認証URLに正しくアクセスできるかテスト"""
        self.assertEqual(self.response.status_code, 302)

    def test_usercreate_complete(self):
        """登録内容のテスト"""
        self.assertTrue(User.objects.get(email='test@edu.cc.saga-u.ac.jp'))

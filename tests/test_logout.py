from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from login.models import EmailUser

User = get_user_model()


class UserLogoutTests(TestCase):
    """Userのログアウトをテスト"""
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')  # メールのテストのために上書き
    def setUp(self):
        """ユーザーを作成"""
        url = reverse('login:user_create')
        self.test_email = 'test@edu.cc.saga-u.ac.jp'
        data = {
            'email': self.test_email,
            'password': 'TestPass1',
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する
        self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000')
        body_lines = mail.outbox[0].body.split('\n')
        auth_url = body_lines[8]  # メール本文から認証urlを取得
        self.response = self.client.get(auth_url)

        self.assertTrue(User.objects.get(email=self.test_email))
        self.assertRedirects(self.response, reverse('search:index'))  # ユーザー登録時に自動的にログインされる

    def test_user_logout(self):
        self.response = self.client.get(reverse('login:logout'))
        self.assertEqual(self.response.status_code, 302)
        self.assertRedirects(self.response, reverse('login:login'))


class EmailuserLogoutTests(TestCase):
    """Emailuserのログアウトをテスト"""
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')  # メールのテストのために上書き
    def setUp(self):
        self.test_email = 'test@edu.cc.saga-u.ac.jp'
        emailuser = EmailUser.objects.filter(email=self.test_email)
        self.assertQuerysetEqual(emailuser, [])

        url = reverse('login:email_login')
        data = {
            'email': self.test_email,
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する
        self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000')

        self.assertEqual(len(mail.outbox), 1)  # 1通のメールが送信されていること
        self.assertEqual(mail.outbox[0].from_email, '22801001@edu.cc.saga-u.ac.jp')  # 送信元
        self.assertEqual(mail.outbox[0].to, [self.test_email])  # 宛先

        body_lines = mail.outbox[0].body.split('\n')
        auth_url = body_lines[7]  # メール本文から認証urlを取得
        self.response = self.client.get(auth_url)

        # ログインできているか確認
        self.assertTrue(EmailUser.objects.get(email=self.test_email).is_active)
        self.assertRedirects(self.response, reverse('search:index'))

    def test_emailuser_logout(self):
        self.response = self.client.get(reverse('login:logout'))
        self.assertEqual(self.response.status_code, 302)
        self.assertRedirects(self.response, reverse('login:login'))

        self.assertFalse(EmailUser.objects.get(email=self.test_email).is_active)

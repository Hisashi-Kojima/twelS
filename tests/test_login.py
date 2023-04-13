from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.test.utils import override_settings

User = get_user_model()


class LoginTest(TestCase):
    def setUp(self) -> None:
        self.response = self.client.get(reverse('search:index'))
        self.assertEqual(self.response.status_code, 302)
        self.response = self.client.get(reverse('login:login'))

    def test_user_create_status_code(self):
        """ステータスコード200を確認"""
        self.assertEqual(self.response.status_code, 200)

    def test_csrf(self):
        """csrfトークンを含むこと"""
        self.assertContains(self.response, 'csrfmiddlewaretoken')


class SuccessfulLoginTests(TestCase):
    """ログイン成功時のテスト"""
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')  # メールのテストのために上書き
    def setUp(self):
        """ログインするユーザーを作成"""
        url = reverse('login:user_create')
        data = {
            'email': 'test@edu.cc.saga-u.ac.jp',
            'password': 'TestPass1',
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する
        self.response = self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000')
        body_lines = mail.outbox[0].body.split('\n')
        url = body_lines[6]  # メール本文から認証urlを取得
        self.response = self.client.get(url)

        self.assertTrue(User.objects.get(email='test@edu.cc.saga-u.ac.jp'))

    def test_login(self):
        self.response = self.client.get(reverse('login:login'))
        self.assertEqual(self.response.status_code, 200)

        url = reverse('login:login')
        data = {
            'username': 'test@edu.cc.saga-u.ac.jp',
            'password': 'TestPass1',
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する\
        self.response = self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000')

        self.assertRedirects(self.response, reverse('search:index'))
        self.assertEqual(self.response.status_code, 302)

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

User = get_user_model()


class LoginTest(TestCase):
    def setUp(self) -> None:
        self.response = self.client.get(reverse('search:index'))
        self.assertEqual(self.response.status_code, 302)  # ログインしていないユーザーが数式検索ページにアクセスするとログインページにリダイレクトされる
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
        auth_url = body_lines[8]  # メール本文から認証urlを取得
        self.response = self.client.get(auth_url)

        self.assertTrue(User.objects.get(email='test@edu.cc.saga-u.ac.jp'))
        self.client.get(reverse('login:logout'))  # ユーザー登録時に自動的にログインされるのでログアウト

    def test_login(self):
        login_url = reverse('login:login')
        self.response = self.client.get(login_url)
        self.assertEqual(self.response.status_code, 200)

        data = {
            'username': 'test@edu.cc.saga-u.ac.jp',
            'password': 'TestPass1',
        }
        self.response = self.client.post(login_url, data)

        self.assertRedirects(self.response, reverse('search:index'))  # ログインしたら数式検索ページにリダイレクト
        self.assertEqual(self.response.status_code, 302)

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

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
    def setUp(self):
        user = User.objects.filter(email="test@edu.cc.saga-u.ac.jp")
        self.assertQuerysetEqual(user, [])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')  # メールのテストのために上書き
    def test_user_create(self):
        url = reverse('login:user_create')
        data = {
            'email': 'test@edu.cc.saga-u.ac.jp',
            'password': 'TestPass1',
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する
        self.response = self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000')

        self.assertEqual(self.response.status_code, 200)  # URLは変わらずにページを変更するのでstatus_code=200

        self.assertEqual(len(mail.outbox), 1)  # 1通のメールが送信されていること
        self.assertEqual(mail.outbox[0].from_email, '22801001@edu.cc.saga-u.ac.jp')  # 送信元
        self.assertEqual(mail.outbox[0].to, ['test@edu.cc.saga-u.ac.jp'])  # 宛先

        body_lines = mail.outbox[0].body.split('\n')
        auth_url = body_lines[8]  # メール本文から認証urlを取得

        self.assertIn('http://127.0.0.1:8000/login/user_create/complete/', auth_url)

        self.response = self.client.get(auth_url)

        self.assertRedirects(self.response, reverse('search:index'))  # ユーザー登録したら数式検索ページにリダイレクト
        self.assertEqual(self.response.status_code, 302)
        self.assertTrue(User.objects.get(email='test@edu.cc.saga-u.ac.jp', is_active=True))


class AfterUserCreateTests(TestCase):
    """ユーザー登録後のテスト"""
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')  # メールのテストのために上書き
    def setUp(self):
        """ログインするユーザーを作成"""
        self.user_create_url = reverse('login:user_create')
        self.data = {
            'email': 'test@edu.cc.saga-u.ac.jp',
            'password': 'TestPass1',
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する
        self.response = self.client.post(self.user_create_url, self.data, HTTP_ORIGIN='http://127.0.0.1:8000')
        body_lines = mail.outbox[0].body.split('\n')
        auth_url = body_lines[8]  # メール本文から認証urlを取得
        self.response = self.client.get(auth_url)

        self.assertTrue(User.objects.get(email='test@edu.cc.saga-u.ac.jp'))
        self.client.get(reverse('login:logout'))  # ユーザー登録時に自動的にログインされるのでログアウト

    def test_existing_user(self):
        "登録したユーザーを再度登録しようとしたときのテスト"
        self.response = self.client.post(self.user_create_url, self.data)
        self.assertRegex(self.response.request['PATH_INFO'], self.user_create_url)  # 現在のページがユーザー登録ページであることを確認
        self.assertContains(self.response, 'User with this Email address already exists.')  # エラーメッセージを確認

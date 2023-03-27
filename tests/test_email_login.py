from login.models import EmailUser
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.test.utils import override_settings


class EmailLoginTest(TestCase):
    def setUp(self) -> None:
        self.response = self.client.get(reverse('search:index'))
        self.assertEqual(self.response.status_code, 302)
        self.response = self.client.get(reverse('login:email_login'))

    def test_user_create_status_code(self):
        """ステータスコード200を確認"""
        self.assertEqual(self.response.status_code, 200)

    def test_csrf(self):
        """csrfトークンを含むこと"""
        self.assertContains(self.response, 'csrfmiddlewaretoken')


class SuccessfulEmailLoginTests(TestCase):
    """メールアドレスログイン成功時のテスト"""
    def setUp(self):
        emailuser = EmailUser.objects.filter(email="test@edu.cc.saga-u.ac.jp")
        self.assertQuerysetEqual(emailuser, [])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')  # メールのテストのために上書き
    def test_email_login(self):
        url = reverse('login:email_login')
        data = {
            'email': 'test@edu.cc.saga-u.ac.jp',
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する\
        self.response = self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000')

        self.assertEqual(self.response.status_code, 302)
        self.home_url = reverse('login:email_login_sent')
        self.assertRedirects(self.response, self.home_url)

        self.assertEqual(len(mail.outbox), 1)  # 1通のメールが送信されていること
        self.assertEqual(mail.outbox[0].from_email, '22801001@edu.cc.saga-u.ac.jp')  # 送信元
        self.assertEqual(mail.outbox[0].to, ['test@edu.cc.saga-u.ac.jp'])  # 宛先

        body_lines = mail.outbox[0].body.split('\n')
        url = body_lines[5]  # メール本文から認証urlを取得

        self.assertIn('http://127.0.0.1:8000/login/email_login/complete/', url)

        self.response = self.client.get(url)

        self.assertEqual(self.response.status_code, 200)

        self.response = self.client.get(reverse('search:index'))

        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(EmailUser.objects.get(email="test@edu.cc.saga-u.ac.jp").is_active)

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.test.utils import override_settings
from login.models import IPAddress
from datetime import datetime


User = get_user_model()


class IPTests(TestCase):
    """IPアドレス警告のテスト"""
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
        self.response = self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000', REMOTE_ADDR='127.0.0.1')
        body_lines = mail.outbox[0].body.split('\n')
        url = body_lines[6]  # メール本文から認証urlを取得
        self.response = self.client.get(url)
        self.assertTrue(User.objects.get(email='test@edu.cc.saga-u.ac.jp'))

        user = User.objects.get(email='test@edu.cc.saga-u.ac.jp')
        user_ip = IPAddress.objects.get(user=user, ip_address='127.0.0.1')
        self.assertTrue(user_ip)

    def test_known_ip(self):
        """既知のIPでログインしたときのテスト
        IPAdressのデータが更新されることを確認"""
        self.response = self.client.get(reverse('login:login'))
        self.assertEqual(self.response.status_code, 200)

        url = reverse('login:login')
        data = {
            'username': 'test@edu.cc.saga-u.ac.jp',
            'password': 'TestPass1',
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する\
        self.response = self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000', REMOTE_ADDR='127.0.0.1')

        user = User.objects.get(email='test@edu.cc.saga-u.ac.jp')
        self.assertEqual(len(IPAddress.objects.filter(user=user, ip_address='127.0.0.1')), 1)  # 同じメールアドレス・IPのデータが複数作られないか確認

        user_ip = IPAddress.objects.get(user=user, ip_address='127.0.0.1')
        now_str: str = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        now: datetime = datetime.strptime(now_str, '%Y/%m/%d %H:%M:%S')
        user_date_str: str = user_ip.last_access.strftime('%Y/%m/%d %H:%M:%S')
        user_date: datetime = datetime.strptime(user_date_str, '%Y/%m/%d %H:%M:%S')

        elapsed_time: datetime.timedelta = abs(now - user_date)
        elapsed_time_seconds: int = int(elapsed_time.total_seconds())
        self.assertLess(elapsed_time_seconds, 1)  # 最後のアクセスが現在から1秒未満であることを確認

    def test_unknown_ip(self):
        """未知のIPでログインしたときのテスト
        警告メールが送信されることを確認する"""
        self.response = self.client.get(reverse('login:login'))
        self.assertEqual(self.response.status_code, 200)

        url = reverse('login:login')
        data = {
            'username': 'test@edu.cc.saga-u.ac.jp',
            'password': 'TestPass1',
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する\
        self.response = self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000', REMOTE_ADDR='127.0.0.2')

        user = User.objects.get(email='test@edu.cc.saga-u.ac.jp')
        user_ip = IPAddress.objects.get(user=user, ip_address='127.0.0.2')
        self.assertTrue(user_ip)

        email_ip = mail.outbox[1].body.split('\n')[3]
        self.assertIn('127.0.0.2', email_ip)

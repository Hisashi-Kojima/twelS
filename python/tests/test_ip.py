from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.test.utils import override_settings
from login.models import IPAddress
from datetime import datetime
from django.db.models.query import QuerySet


User = get_user_model()


class IPTests(TestCase):
    """IPアドレス警告のテスト"""
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')  # メールのテストのために上書き
    def setUp(self):
        """ログインするユーザーを作成"""
        user_create_url = reverse('login:user_create')
        data = {
            'email': 'test@edu.cc.saga-u.ac.jp',
            'password': 'TestPass1',
        }
        self.origin = 'http://127.0.0.1:8000'
        self.client_ip = '127.0.0.2'
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する
        self.response = self.client.post(user_create_url, data, HTTP_ORIGIN=self.origin, REMOTE_ADDR=self.client_ip)

        body_lines = mail.outbox[0].body.split('\n')
        url = body_lines[8]  # メール本文から認証urlを取得
        self.response = self.client.get(url, REMOTE_ADDR=self.client_ip)

        self.assertRedirects(self.response, reverse('search:index'))  # 自動でログインされるのでindexにリダイレクトされるか確認
        self.assertEqual(self.response.status_code, 302)

        self.user = User.objects.get(email='test@edu.cc.saga-u.ac.jp', is_active=True)
        self.assertTrue(self.user)  # ユーザー登録終わり
        self.assertEqual(len(IPAddress.objects.filter(user=self.user, ip_address=self.client_ip)), 1)  # IPアドレスが保存されることを確認

        self.client.get(reverse('login:logout'), REMOTE_ADDR=self.client_ip)

        self.login_url = reverse('login:login')
        self.login_data = {
            'username': 'test@edu.cc.saga-u.ac.jp',
            'password': 'TestPass1',
        }

    def test_registered_ip(self):
        """登録しているIPでログインしたときのテスト
        IPAddressのデータが更新されることを確認"""
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する\
        self.response = self.client.post(self.login_url, self.login_data, HTTP_ORIGIN=self.origin, REMOTE_ADDR=self.client_ip)

        user_ip_set: QuerySet = IPAddress.objects.filter(user=self.user, ip_address=self.client_ip)

        self.assertEqual(len(user_ip_set), 1)  # 同じメールアドレス・IPのデータが複数作られないか確認

        user_ip = user_ip_set[0]
        now_str: str = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        now: datetime = datetime.strptime(now_str, '%Y/%m/%d %H:%M:%S')
        user_date_str: str = user_ip.last_access.strftime('%Y/%m/%d %H:%M:%S')
        user_date: datetime = datetime.strptime(user_date_str, '%Y/%m/%d %H:%M:%S')

        elapsed_time: datetime.timedelta = abs(now - user_date)
        elapsed_time_seconds = float(elapsed_time.total_seconds())
        self.assertLess(elapsed_time_seconds, float(1))  # 最後のアクセスが現在から1秒未満であることを確認

    def test_new_ip(self):
        """登録されていないIPでログインしたときのテスト
        警告メールが送信されることを確認する"""
        client_new_ip = '127.0.0.3'
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する\
        self.response = self.client.post(self.login_url, self.login_data, HTTP_ORIGIN=self.origin, REMOTE_ADDR=client_new_ip)

        user_ip = IPAddress.objects.get(user=self.user, ip_address=client_new_ip)  # IPが保存されることを確認
        self.assertTrue(user_ip)

        text_include_ip = mail.outbox[1].body.split('\n')[3]
        self.assertIn(client_new_ip, text_include_ip)  # 警告メールが送信されることを確認

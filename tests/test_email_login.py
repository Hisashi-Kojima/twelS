import datetime

from django.conf import settings
from django.core import mail
from django.test import LiveServerTestCase, TestCase
from django.test.utils import override_settings
from django.urls import reverse
import freezegun
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from create_webdriver import create_driver_connected_hub
from login.models import EmailUser


class EmailLoginTest(TestCase):
    def setUp(self) -> None:
        """リダイレクトされるか確認"""
        self.response = self.client.get(reverse('search:index'))
        self.assertEqual(self.response.status_code, 302)
        self.response = self.client.get(reverse('login:email_login'))

    def test_user_create_status_code(self):
        """ステータスコード200を確認"""
        self.assertEqual(self.response.status_code, 200)

    def test_csrf(self):
        """csrfトークンを含むこと"""
        self.assertContains(self.response, 'csrfmiddlewaretoken')


class UnsuccessfulEmailLoginTest(TestCase):
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')  # メールのテストのために上書き
    def setUp(self):
        emailuser = EmailUser.objects.filter(email="test@edu.cc.saga-u.ac.jp")
        self.assertQuerysetEqual(emailuser, [])

        url = reverse('login:email_login')
        data = {
            'email': 'test@edu.cc.saga-u.ac.jp',
        }
        # The headers sent via **extra should follow CGI specification.
        # CGI (Common Gateway Interface)に対応するためにヘッダー名の先頭に'HTTP_'を追加する
        self.client.post(url, data, HTTP_ORIGIN='http://127.0.0.1:8000')

        self.assertEqual(len(mail.outbox), 1)  # 1通のメールが送信されていること
        self.assertEqual(mail.outbox[0].from_email, '22801001@edu.cc.saga-u.ac.jp')  # 送信元
        self.assertEqual(mail.outbox[0].to, ['test@edu.cc.saga-u.ac.jp'])  # 宛先

    def test_wrong_url(self):
        wrong_url = 'http://127.0.0.1:8000/login/email_login/complete/wrong_token/'

        response = self.client.get(wrong_url)

        self.assertEqual(response.status_code, 401)

        html_content = response.content.decode('utf-8')
        self.assertIn('この認証URLは正しくありません。', html_content)

    def test_expired_url(self):

        body_lines = mail.outbox[0].body.split('\n')
        auth_url = body_lines[7]  # メール本文から認証urlを取得

        date_after_5m = datetime.datetime.now() + datetime.timedelta(minutes=5)

        with freezegun.freeze_time(date_after_5m):  # 5分後の時刻で以下を実行
            response = self.client.get(auth_url)

            self.assertEqual(response.status_code, 401)
            html_content = response.content.decode('utf-8')
            self.assertIn('この認証URLは期限切れです。', html_content)


class SeleniumEmailLoginTests(LiveServerTestCase):
    """seleniumによるログインテスト"""
    # docker-compose.dev.ymlの
    # pythonコンテナのサービス名にすること
    host = 'python'

    def setUp(self):
        # テスト用のeメールがすでに登録されていないか確認する
        emailuser = EmailUser.objects.filter(email="test@edu.cc.saga-u.ac.jp")
        self.assertQuerysetEqual(emailuser, [])
        # テスト中はCSRFの検証を切っておく
        settings.CSRF_COOKIE_SECURE = False
        settings.SESSION_COOKIE_SECURE = False

    # ----tests----
    # ブラウザごとにテストする

    # 最新バージョン->
    def test_latest_chrome(self):
        self.email_login("chrome", 110)

    def test_latest_firefox(self):
        self.email_login("firefox", 110)

    def test_latest_edge(self):
        self.email_login("edge", 110)

    # 確認できた最も古いバージョン->
    def test_oldest_chrome(self):
        self.email_login("chrome", 61)

    def test_oldest_firefox(self):
        self.email_login("firefox", 88)

    def test_oldest_edge(self):
        self.email_login("edge", 92)
    # -------------

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')  # メールのテストのために上書き
    def email_login(self, browser_name: str, browser_version: int):
        """e-mailでのログインテスト
        Args:
            browser_name: browser name
            browser_version: browser version
        Notes:
            browser_nameはfirefox, edge, chromeのいずれかであること,
            browser_versionに入力する数値は正の整数であること
        """
        # テスト用URL
        url = self.live_server_url
        # 送信先
        e_address = "test@edu.cc.saga-u.ac.jp"
        # seleniumでアクセス
        with create_driver_connected_hub(browser_name, browser_version) as driver:
            wait = WebDriverWait(driver=driver, timeout=30)
            # リダイレクトでログインページに飛ぶ
            driver.get(url)
            # 要素が表示されるまで待つ
            wait.until(EC.presence_of_all_elements_located)
            assert driver.title == 'ログイン'
            # メールアドレスでログインページに移行
            element = driver.find_element(By.LINK_TEXT, "メールアドレスでのログイン")
            element.click()
            wait.until(EC.presence_of_all_elements_located)
            assert driver.title == 'メールでのログイン'
            # inputにメールアドレスを入力してボタンをクリック
            element = driver.find_element(By.NAME, "email")
            element.send_keys(e_address)
            button = driver.find_element(By.XPATH, "//form/button")
            button.click()
            wait.until(EC.presence_of_all_elements_located)
            assert driver.title == 'メールを送信しました'
            # メールの確認
            self.assertEqual(len(mail.outbox), 1)  # 1通のメールが送信されていること
            self.assertEqual(mail.outbox[0].from_email, '22801001@edu.cc.saga-u.ac.jp')  # 送信元
            self.assertEqual(mail.outbox[0].to, [e_address])  # 宛先
            # 認証URLを取得
            body_lines = mail.outbox[0].body.split('\n')
            url = body_lines[7]  # メール本文から認証urlを取得
            self.assertIn(self.live_server_url + '/login/email_login/complete/', url)
            # 認証URLにアクセス
            driver.get(url)
            wait.until(EC.presence_of_all_elements_located)
            assert driver.title == 'twelS'
            # ログインできているか確認
            self.assertTrue(EmailUser.objects.get(email=e_address).is_active)

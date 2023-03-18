from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views import generic
from .forms import (
    LoginForm, CustomUserCreateForm, CustomPasswordChangeForm,
    MyPasswordResetForm, CustomSetPasswordForm, EmailLoginForm
)
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from .models import EmailUser, IPAddress, PasswordResetRequest, UserCreateRequest, EmailLoginRequest
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import datetime


User = get_user_model()
Emailuser = EmailUser


def get_ip(request):
    forwarded_addresses = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_addresses:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがある場合: 転送経路の先頭要素を取得する。
        current_ip = forwarded_addresses.split(',')[0]
    else:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがない場合: 直接接続なので'REMOTE_ADDR'ヘッダを参照する。
        current_ip = request.META.get('REMOTE_ADDR')
    return current_ip


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'htmls/login.html'

    redirect_authenticated_user = True  # ログインしているユーザーがアクセスしたとき数式検索ページにリダイレクト

    def form_valid(self, form):

        login(self.request, form.get_user())

        if self.request.user.is_authenticated:
            try:
                user = User.objects.get(pk=self.request.user.pk)

                current_ip = get_ip(self.request)

                ip = IPAddress.objects.filter(user=user, ip_address=current_ip)

                if ip:
                    ip_address = IPAddress.objects.get(user=user, ip_address=current_ip)
                    ip_address.last_access = timezone.now()
                    ip_address.save()
                    pass
                else:
                    IPAddress.objects.create(user=user, ip_address=current_ip)

                    origin: str = self.request.headers["Origin"]
                    context = {
                        'origin': origin,
                        'user': user,
                        'ip': current_ip
                    }

                    subject = render_to_string('mail_template/unknown_ip/subject.txt', context)
                    message = render_to_string('mail_template/unknown_ip/message.txt', context)

                    user.send_mail(subject, message)

            except ObjectDoesNotExist:
                pass
        return HttpResponseRedirect(self.get_success_url())


class Logout(generic.View):

    def get(self, request):

        """メール認証ログインユーザーはログアウト時にis_active=False"""
        try:
            emailuser: EmailUser = Emailuser.objects.get(email=request.user)

        except Emailuser.DoesNotExist:
            pass
        else:
            emailuser: EmailUser = Emailuser.objects.get(email=request.user)
            emailuser.is_active = False
            emailuser.save()

        logout(request)
        return redirect('login:login')


class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'htmls/user_create.html'
    form_class = CustomUserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        origin: str = self.request.headers["Origin"]
        context = {
            'origin': origin,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('mail_template/user_create/subject.txt', context)
        message = render_to_string('mail_template/user_create/message.txt', context)

        user.send_mail(subject, message)
        return redirect('login:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'htmls/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'htmls/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return render(request, 'htmls/token_error.html', status=401)

        # tokenが間違っている
        except BadSignature:
            return render(request, 'htmls/token_error.html', status=401)

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)

                current_ip = get_ip(self.request)
                IPAddress.objects.create(user=user, ip_address=current_ip)

                UserCreateRequest.objects.filter(email=user.email).delete()

            except User.DoesNotExist:
                return HttpResponseBadRequest('user does not exist')

            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return render(request, 'htmls/token_error.html', status=401)


class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserPage(OnlyYouMixin, generic.TemplateView):
    model = User
    template_name = 'htmls/user.html'


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('login:password_change_done')
    template_name = 'htmls/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'htmls/password_change_done.html'


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'mail_template/password_reset/subject.txt'
    email_template_name = 'mail_template/password_reset/message.txt'
    template_name = 'htmls/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('login:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'htmls/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('login:password_reset_complete')
    template_name = 'htmls/password_reset_confirm.html'

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
            user.save()

            user_request = PasswordResetRequest.objects.get(email=user.email)

            user_request.email_request_times = 0
            user_request.first_request_date = datetime.datetime.now()
            user_request.save()

        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'htmls/password_reset_complete.html'


class EmailLogin(generic.FormView):
    """メールアドレスでのログインページ"""
    form_class = EmailLoginForm
    template_name = 'htmls/email_login.html'

    def form_valid(self, form):
        """ログインのためのメール送信"""

        emailuser: EmailUser = form.save(commit=False)
        emailuser.is_active = False
        emailuser.save()
        # アクティベーションURLの送付
        origin: str = self.request.headers["Origin"]
        context = {
            'origin': origin,
            'token': dumps(emailuser.pk),
            'user': emailuser,
        }

        subject = render_to_string('mail_template/email_login/subject.txt', context)
        message = render_to_string('mail_template/email_login/message.txt', context)

        emailuser.send_mail(subject, message)
        return redirect('login:email_login_sent')


class EmailLoginSent(generic.TemplateView):
    template_name = 'htmls/email_login_sent.html'


class EmailLoginComplete(generic.TemplateView):
    template_name = 'htmls/email_login_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*5)  # デフォルトでは5分以内

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return render(request, 'htmls/token_error.html', status=401)

        # tokenが間違っている
        except BadSignature:
            return render(request, 'htmls/token_error.html', status=401)

        # tokenは問題なし
        else:
            try:
                emailuser = Emailuser.objects.get(pk=user_pk)

                email_request = EmailLoginRequest.objects.get(email=emailuser.email)

                email_request.email_request_times = 0
                email_request.save()

            except Emailuser.DoesNotExist:
                return HttpResponseBadRequest('emailuser does not exist')
            else:
                if not emailuser.is_active:
                    # 問題なければ本登録とする
                    emailuser.is_active = True
                    emailuser.save()
                    login(request, emailuser, backend='login.auth_backend.PasswordlessAuthBackend')
                    return super().get(request, **kwargs)
        return render(request, 'htmls/token_error.html', status=401)

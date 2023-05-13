import datetime

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.views import generic

from .forms import (
    LoginForm, CustomUserCreateForm, CustomPasswordChangeForm,
    MyPasswordResetForm, CustomSetPasswordForm, EmailLoginForm
)
from .models import EmailUser, IPAddress, PasswordResetRequest, UserCreateRequest, EmailLoginRequest
import logging

logger = logging.getLogger('django')


User = get_user_model()
Emailuser = EmailUser


def get_ip(request):
    forwarded_addresses = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_addresses:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがある場合: 転送経路の先頭要素を取得する。
        current_ip = forwarded_addresses.split(',')[0]
        logger.info('get IP from HTTP_X_FORWARDED_FOR')
    else:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがない場合: 直接接続なので'REMOTE_ADDR'ヘッダを参照する。
        current_ip = request.META.get('REMOTE_ADDR')
        logger.info('get IP from REMOTE_ADDR')
    return current_ip


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'htmls/login.html'

    redirect_authenticated_user = True  # ログインしているユーザーがアクセスしたとき数式検索ページにリダイレクト

    def form_valid(self, form):
        """ログイン時にIPアドレスを取得し,未知のIPアドレスだった場合は警告メールを送信する."""
        login(self.request, form.get_user())

        try:
            user = User.objects.get(pk=self.request.user.pk)

            current_ip = get_ip(self.request)

            ip = IPAddress.objects.filter(user=user, ip_address=current_ip)

            if ip:  # 既知のIPアドレスの場合は最後にアクセスした日時を更新する
                ip_address = IPAddress.objects.get(user=user, ip_address=current_ip)
                ip_address.last_access = timezone.now()
                ip_address.save()

            else:  # 未知のIPアドレスの場合はIPアドレスを登録し,ユーザーに警告メールを送信する
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
            # userが存在しない場合でも正常に動作するように用意している
            pass
        except Exception as e:
            logger.error(f'{e} in login  user:{user}')

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
        return render(request=self.request, template_name='htmls/email_sent.html', context={'user': user})


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired as e:
            logger.error(f'{e} in user_create.')
            context = {
                'message': 'この認証URLは期限切れです。',
            }
            return render(request, 'htmls/token_error.html', context, status=401)

        # tokenが間違っている
        except BadSignature as e:
            logger.error(f'{e} in user_create.')
            context = {
                'message': 'この認証URLは正しくありません。',
            }
            return render(request, 'htmls/token_error.html', context, status=401)

        # それ以外のエラー
        except Exception as e:
            logger.error(f'{e} in user_create.')
            context = {
                'message': '予期していないエラーが発生しました。お手数ですが、最初から手続きをお願いいたします。',
            }
            return render(request, 'htmls/token_error.html', status=401)

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
                UserCreateRequest.objects.filter(email=user.email).delete()  # リクエストを削除する．

                current_ip = get_ip(self.request)

                ip_set: QuerySet = IPAddress.objects.filter(user=user, ip_address=current_ip)

                if not ip_set:
                    # 未知のIPアドレスの場合はIPアドレスを登録する
                    IPAddress.objects.create(user=user, ip_address=current_ip)

                else:
                    # 既知のIPアドレスの場合は最後にアクセスした日時を更新する
                    ip_address = ip_set[0]
                    ip_address.last_access = timezone.now()
                    ip_address.save()

            except Exception as e:
                logger.error(f'{e} in user_create')
                context = {
                    'message': '予期していないエラーが発生しました。お手数ですが、最初から手続きをお願いいたします。',
                }
                return render(request, 'htmls/token_error.html', context, status=401)
            else:
                # 同じ認証URLに複数回アクセスした場合もindexにリダイレクト
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('search:index')


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

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        form.save(**opts)
        user = form.cleaned_data['email']
        return render(request=self.request, template_name='htmls/email_sent.html', context={'user': user})


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
        return render(request=self.request, template_name='htmls/email_sent.html', context={'user': emailuser})


class EmailLoginComplete(generic.TemplateView):
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*5)  # デフォルトでは5分以内

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired as e:
            logger.error(f'{e} in email_login')
            context = {
                'message': 'この認証URLは期限切れです。',
            }
            return render(request, 'htmls/token_error.html', context, status=401)

        # tokenが間違っている
        except BadSignature as e:
            logger.error(f'{e} in email_login')
            context = {
                'message': 'この認証URLは正しくありません。',
            }
            return render(request, 'htmls/token_error.html', context, status=401)

        # それ以外のエラー
        except Exception as e:
            logger.error(f'{e} in email_login')
            context = {
                'message': '予期していないエラーが発生しました。お手数ですが、最初から手続きをお願いいたします。',
            }
            return render(request, 'htmls/token_error.html', context, status=401)

        # tokenは問題なし
        else:
            try:
                emailuser = Emailuser.objects.get(pk=user_pk)

                email_request = EmailLoginRequest.objects.get(email=emailuser.email)

                email_request.email_request_times = 0
                email_request.save()

            except Exception as e:
                logger.error(f'{e} in email_login')
                context = {
                    'message': '予期していないエラーが発生しました。お手数ですが、最初から手続きをお願いいたします。',
                }
                return render(request, 'htmls/token_error.html', context, status=401)
            else:
                # 問題なければログインとする
                emailuser.is_active = True
                emailuser.save()
                login(request, emailuser, backend='login.auth_backend.PasswordlessAuthBackend')
                return redirect('search:index')
        return render(request, 'htmls/token_error.html', status=401)

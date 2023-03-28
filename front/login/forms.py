from datetime import datetime
import unicodedata

from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import (
    AuthenticationForm, SetPasswordForm
)
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from login.models import EmailUser, PasswordResetRequest, UserCreateRequest, EmailLoginRequest


User = get_user_model()
Emailuser = EmailUser


def check_request_times(MODEL, email):
    user_request = MODEL.objects.get(email=email)

    if user_request.email_request_times < 3:
        user_request.email_request_times += 1
        user_request.save()

    else:
        message = """
        3回以上認証に失敗したので，24時間以上経過してからもう一度お試しください.もしくは，22801001@edu.cc.saga-u.ac.jpにご連絡ください.
        """
        raise ValidationError(message)


def check_request_date(MODEL, email):
    user_request = MODEL.objects.get(email=email)
    print('user_request: ', type(user_request))

    now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    if user_request.first_request_date is None:
        user_request.first_request_date = datetime.now()
        user_request.save()

    else:
        now = datetime.strptime(now, '%Y/%m/%d %H:%M:%S')
        user_date_str: str = user_request.first_request_date.strftime('%Y/%m/%d %H:%M:%S')
        user_date: datetime = datetime.strptime(user_date_str, '%Y/%m/%d %H:%M:%S')

        elapsed_time = abs(now - user_date)

        if elapsed_time.days > 1:
            user_request.first_request_date = datetime.now()
            user_request.email_request_times = 0
            user_request.save()


def _unicode_ci_compare(s1, s2):
    """
    Perform case-insensitive comparison of two identifiers, using the
    recommended algorithm from Unicode Technical Report 36, section
    2.11.2(B)(2).
    """
    return (
        unicodedata.normalize("NFKC", s1).casefold()
        == unicodedata.normalize("NFKC", s2).casefold()
    )


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる
        self.fields['password'].widget.attrs['id'] = 'Password'


class UsernameField(forms.CharField):
    def to_python(self, value):
        return unicodedata.normalize("NFKC", super().to_python(value))

    def widget_attrs(self, widget):
        return {
            **super().widget_attrs(widget),
            "autocapitalize": "none",
            "autocomplete": "username",
        }


class CustomUserCreateForm(forms.ModelForm):
    """ユーザー登録フォーム
    パスワード確認なし"""
    password = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("email",)
        field_classes = {"email": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = True

            # 下の要素にcssを適用するためにidを設定
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "id"
            ] = 'email'
        self.fields['password'].widget.attrs['id'] = 'Password'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()

        return email

    def _post_clean(self):
        """パスワードのバリデーション
        条件を満たしてなかったら入力内容を削除
        """
        super()._post_clean()
        password = self.cleaned_data.get("password")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
                email = self.cleaned_data['email']
                check_request(UserCreateRequest, email)
            except ValidationError as error:
                self.add_error("password", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomPasswordChangeForm(forms.Form):
    """パスワード変更フォーム
    パスワード確認なし"""
    error_messages = {
        **SetPasswordForm.error_messages,
        "password_incorrect": (
            "Your old password was entered incorrectly. Please enter it again."
        ),
    }

    old_password = forms.CharField(
        label=("old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True}
        ),
    )

    new_password = forms.CharField(
        label=("new password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['id'] = 'OldPassword'
        self.fields['new_password'].widget.attrs['id'] = 'Password'

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password

    def clean_new_password(self):
        """パスワードのバリデーション
        条件を満たしてなかったら入力内容を削除
        """
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            try:
                password_validation.validate_password(new_password)
            except ValidationError as error:
                self.add_error("new_password", error)
        return new_password

    def save(self, commit=True):
        password = self.cleaned_data["new_password"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


def check_user(email):
    user_exist = User.objects.filter(email=email, is_active=True)

    if user_exist:
        check_request(PasswordResetRequest, email)
    if not user_exist:
        raise ValidationError("not exist")


class MyPasswordResetForm(forms.Form):
    """パスワード忘れたときのフォーム"""
    email = forms.EmailField(
        label=("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
        validators=[check_user]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 下の要素にcssを適用するためにidを設定
        self.fields['email'].widget.attrs['id'] = 'email'

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.
        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = User.get_email_field_name()
        active_users = User._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
            and _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def save(
        self,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        origin: str = request.headers["Origin"]
        email_field_name = User.get_email_field_name()
        from_email = '22801001@edu.cc.saga-u.ac.jp'

        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "origin": origin,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                user_email,
                html_email_template_name=html_email_template_name,
            )


class CustomSetPasswordForm(forms.Form):
    """パスワードを忘れたとき，新パスワード入力フォーム
    パスワード確認なし"""
    new_password = forms.CharField(
        label=("New password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['new_password'].widget.attrs['id'] = 'Password'

    def clean_new_password(self):
        """パスワードのバリデーション
        条件を満たしてなかったら入力内容を削除
        """
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            try:
                password_validation.validate_password(new_password)
            except ValidationError as error:
                self.add_error("new_password", error)
        return new_password

    def save(self, commit=True):
        password = self.cleaned_data["new_password"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class EmailLoginForm(forms.ModelForm):
    class Meta:
        model = EmailUser
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        Emailuser.objects.filter(email=email, is_active=False).delete()

        if Emailuser.objects.filter(email=email):
            emailuser = Emailuser.objects.get(email=email)
            
            if emailuser.is_authenticated:
                # active = trueということなので削除，active=falseでもいいかも
                emailuser.delete()

        check_request(EmailLoginRequest, email)
        return email

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model, password_validation
from .models import EmailUser
import unicodedata
from django.core.exceptions import ValidationError


User = get_user_model()
Emailuser = EmailUser


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる


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
        self.fields['password'].widget.attrs['id'] = 'Password'

    
    def _post_clean(self):
        """パスワードのバリデーション
        条件を満たしてなかったら入力内容を削除
        """
        super()._post_clean()
        password = self.cleaned_data.get("password")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
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

class MyPasswordResetForm(PasswordResetForm):
    """パスワード忘れたときのフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


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
        return email

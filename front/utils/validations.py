from django.core.exceptions import ValidationError
import re


class CustomPasswordValidator():

    msg = 'パスワードには，0-9, a-z, A-Zを含めてください'

    def __init__(self):
        pass

    def validate(self, password, user=None):
        if all((
            re.search('[0-9]', password),
            re.search('[a-z]', password),
            re.search('[A-Z]', password)
            )):
            return
        raise ValidationError(self.msg)

    def get_help_text(self):
        return self.msg

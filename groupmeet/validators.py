from django.utils.translation import ngettext  # https://docs.python.org/2/library/gettext.html#gettext.ngettext
from django.core.exceptions import ValidationError
import re
from difflib import SequenceMatcher
from django.core.exceptions import (
    FieldDoesNotExist, ValidationError,
)

    # https://docs.djangoproject.com/en/2.0/_modules/django/contrib/auth/password_validation/#MinimumLengthValidator
class MyCustomMinimumLengthValidator(object):
    def __init__(self, min_length=8):  # put default min_length here
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "비밀번호는 최소 %(min_length)d 글자 이상이어야 합니다",
                    "비밀번호는 최소 %(min_length)d 글자 이상이어야 합니다",
                    self.min_length
                ),
            code='password_too_short',
            params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return ngettext(
            # you can also change the help text to whatever you want for use in the templates (password.help_text)
            "비밀번호는 최소 %(min_length)d 글자 이상이어야 합니다",
            "비밀번호는 최소 %(min_length)d 글자 이상이어야 합니다",
            self.min_length
        ) % {'min_length': self.min_length}

class MyCustomNumericPasswordValidator:
    """
    Validate whether the password is alphanumeric.
    """
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                ("비밀번호가 숫자로만 구성되어 있습니다"),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return ("Your password can't be entirely numeric.")

class MyCustomUserAttributeSimilarityValidator:
    """
    Validate whether the password is sufficiently different from the user's
    attributes.

    If no specific attributes are provided, look at a sensible list of
    defaults. Attributes that don't exist are ignored. Comparison is made to
    not only the full attribute value, but also its components, so that, for
    example, a password is validated against either part of an email address,
    as well as the full address.
    """
    DEFAULT_USER_ATTRIBUTES = ('username', 'nickname','email')

    def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=0.7):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return

        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_parts = re.split(r'\W+', value) + [value]
            for value_part in value_parts:
                if SequenceMatcher(a=password.lower(), b=value_part.lower()).quick_ratio() >= self.max_similarity:
                    try:
                        verbose_name = str(user._meta.get_field(attribute_name).verbose_name)
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        ("입력한 비밀번호가 %(verbose_name)s과 비슷합니다"),
                        code='password_too_similar',
                        params={'verbose_name': verbose_name},
                    )

    def get_help_text(self):
        return ("Your password can't be too similar to your other personal information.")

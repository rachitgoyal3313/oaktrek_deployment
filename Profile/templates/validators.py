from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class UppercaseValidator:
    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter (A-Z)."),
                code='password_no_uppercase',
            )
    
    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter (A-Z).")

class SpecialCharacterValidator:
    def validate(self, password, user=None):
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        if not any(char in special_characters for char in password):
            raise ValidationError(
                _("Password must contain at least one special character."),
                code='password_no_special_char',
            )
    
    def get_help_text(self):
        return _("Your password must contain at least one special character.")

class NumberValidator:
    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("Password must contain at least one digit (0-9)."),
                code='password_no_digit',
            )
    
    def get_help_text(self):
        return _("Your password must contain at least one digit (0-9).")

class MinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length
        
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least %(min_length)d characters long."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )
    
    def get_help_text(self):
        return _("Your password must be at least %d characters long." % self.min_length)

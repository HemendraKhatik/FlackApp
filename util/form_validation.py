"""
Author:		kaloneh <kaloneh@gmail.com>
Comment:	A helper to validate form field data
"""
import re

from wtforms.validators import ValidationError
from models.exceptions import WordSizeException


class UserFieldValidation:
    def __init__(self, **kwargs):
        self.username = kwargs.get('username', None)
        self.email = kwargs.get('email', None)
        self.password = kwargs.get('password', None)

    def validateUsername(self, username=None, min_letters=3, max_letters=32):
        usr = username if username is not None else self.username
        if usr is None or len(usr) < min_letters or len(usr) > max_letters:
            raise WordSizeException(min_size=min_letters, max_size=max_letters)
        return re.search(
            "[a-zA-Z]\w{%s,%s}" % (min_letters - 1, max_letters - 1), usr
        ) is not None

    def validateEmail(self, email=None, min_letters=5, max_letters=64):
        _email = email if email is not None else self.email
        if _email is None or len(_email) < min_letters or len(_email) > max_letters:
            raise WordSizeException(min_size=min_letters, max_size=max_letters)
        return re.search(
            "[a-zA-Z][\w\.]*@\w+\.\w+", _email
        ) is not None

    def passwordStrength(self, password=None, min_letters=6, max_letters=128):
        psw = password if password is not None else self.password
        if psw is None or len(psw) < min_letters or len(psw) > max_letters:
            raise WordSizeException(min_size=min_letters, max_size=max_letters)
        criteria = (r'[$-/:-?{-~!"^_`\[\]]+', r'[a-z]', r'[A-Z]', r'[0-9]')
        strength = 0
        for c in criteria:
            if re.search(c, psw):
                strength += 1
        return strength

    def enumStrength(self, strength, max_length=4):
        return (
            'awful', 'weak', 'not_strong', 'strong', 'awesome'
        )[strength] if strength >= 0 and strength <= max_length else None


class ChannelFieldValidation:
    def __init__(self, **kwargs):
        pass

    def validateChannelName(self, channel_name):
        pass

    def validateDescription(self, description):
        pass


class Unique(object):
    def __init__(self, model, field, message=u'This element already exists.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)


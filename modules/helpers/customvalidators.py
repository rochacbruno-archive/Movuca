# -*- coding: utf-8 -*-

from gluon import *
from gluon.validators import IS_EMPTY_OR, is_empty, IS_EMAIL


class IS_MASK(object):
    def __init__(self, error_message="Invalid", mask=""):
        self.error_message = error_message
        self.mask = mask

    def __call__(self, value):
        if value == self.mask:

            return (None, None)
        else:
            return (value, None)


class IS_EMAIL_LIST(object):
    def __init__(self, error_message="Email %s is invalid", sep=","):
        self.error_message = error_message
        self.sep = sep

    def __call__(self, value):
            emails = value.strip().replace('\n', '').replace('\t', '').split(self.sep)
            for email in emails:
                email = email.strip()
                if IS_EMAIL()(email)[1] != None:
                    return (email, self.error_message % email)
            return (emails, None)


class COMMA_SEPARATED_LIST(object):
    def __init__(self, error_message="value %s is invalid", sep=","):
        self.error_message = error_message
        self.sep = sep

    def __call__(self, value):
            items = value.strip().replace('\n', '').replace('\t', '').split(self.sep)
            return ([item.strip().lower() for item in items], None)


class IS_EMPTY_OR_MASK_OR(IS_EMPTY_OR):
    def __call__(self, value):
        if value in ['____-__-__', '    -  -  ',
                     '  /  /    ', '__/__/____',
                     '(  )     -    ', '(__) ____-____']:
            value = ''
        value, empty = is_empty(value, empty_regex=self.empty_regex)
        if empty:
            return (self.null, None)
        if isinstance(self.other, (list, tuple)):
            for item in self.other:
                value, error = item(value)
                if error:
                    break
            return value, error
        else:
            return self.other(value)

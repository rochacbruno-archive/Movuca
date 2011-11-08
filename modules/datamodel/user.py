# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseModel
from gluon.validators import IS_EMAIL, IS_IN_DB, IS_NOT_IN_DB, CRYPT


class User(BaseModel):
    from gluon import current
    request = current.request
    tablename = "auth_user"
    properties = [Field("name", notnull=True),
                  Field("email", unique=True, notnull=True),
                  Field("password", "password"),
                  Field('registration_key', length=512, writable=False, readable=False, default=''),
                  Field('reset_password_key', length=512, writable=False, readable=False, default=''),
                  Field('registration_id', length=512, writable=False, readable=False, default=''),
                  Field('record_created', 'datetime', default=request.now, writable=False, readable=False),
                  Field('record_updated', 'datetime', default=request.now, update=request.now, writable=False, readable=False)]
    visibility = {'password': (True, False),
                  'registration_key': (False, False),
                  'reset_password_key': (False, False),
                  }
    #representation = {'tele': lambda v: XML("<b>%s</b>" % v)}
    #widgets = {'tele': None}
    #labels = {'password': "EMAIL"}
    #comments = {'email': "Seu E-mail"}

    def set_validators(self):
        self.entity.email.requires = [IS_EMAIL(),
            IS_NOT_IN_DB(self.db, self.entity.email)]
        self.entity.password.requires = CRYPT(key=self.auth.settings.hmac_key)


class Category(BaseModel):
    tablename = "category"
    properties = [Field("title"),
                  Field("user", "integer")]

    def set_validators(self):
        self.entity.user.requires = IS_IN_DB(self.db, 'auth_user.id')

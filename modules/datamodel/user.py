# -*- coding: utf-8 -*-

from gluon.dal import Field
from gluon import current
from gluon import *  # change here for specific imports
from basemodel import BaseModel
from gluon.validators import IS_EMAIL, IS_IN_DB


class User(BaseModel):
    tablename = "auth_user"
    properties = [Field("name"),
                  Field("email"),
                  Field("tele", default="123")]
    validators = {'email': IS_EMAIL()}
    visibility = {'tele': (True, True)}
    representation = {'tele': lambda v: XML("<b>%s</b>" % v)}
    widgets = {'tele': None}
    labels = {'email': "EMAIL"}
    comments = {'email': "Seu E-mail"}


class Category(BaseModel):
    tablename = "category"
    properties = [Field("title"),
                  Field("user", "reference auth_user")]

    def set_validators(self):
        self.entity.user.requires = IS_IN_DB(self.db, 'auth_user.id')

# -*- coding: utf-8 -*-

from gluon.dal import Field
from gluon import current
from gluon import *  # change here for specific imports
from basemodel import BaseModel


class User(BaseModel):
    tablename = "auth_user"
    properties = [Field("name"), Field("email")]

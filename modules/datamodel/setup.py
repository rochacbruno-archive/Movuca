# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseModel
from gluon.validators import *


class Setup(BaseModel):
    tablename = 'application_setup'

    def set_properties(self):
        self.fields = [
            Field("appname", "string"),
        ]

# coding: utf-8

from gluon.dal import Field
from basemodel import BaseModel
from gluon.validators import *


class Menu(BaseModel):
    tablename = "menu"

    def set_properties(self):
        self.fields = [
            Field("title"),
            Field("href"),
            Field("parent", "integer", default=0),
            Field("place", default="top"),
            Field("show_order", "integer", default=0),
            Field("visibility", "integer", default=1)
        ]

        #parents = [(0, "no - parent")]

        self.validators = {
            "title": [IS_NOT_EMPTY(), IS_NOT_IN_DB(self.db, 'menu.title')],
            "href": IS_NOT_EMPTY(),
            "place": IS_IN_SET(["top", "left", "right", "bottom"]),
            "visibility": IS_IN_SET([(1, self.db.T("Logged out")), (2, self.db.T("Logged in")), (3, self.db.T("Admin")), (4, self.db.T("Everyone"))]),
            #"parent": IS_EMPTY_OR(IS_IN_DB(self.db(self.entity.parent == 0), self.entity.id, '%(title)s'))
        }

    def set_validators(self):
        self.entity.parent.requires = IS_EMPTY_OR(IS_IN_DB(self.db((self.entity.parent == 0) | (self.entity.parent == None)), self.entity.id, '%(title)s'))

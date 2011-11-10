# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseModel
from gluon.validators import *


class Article(BaseModel):
    tablename = "article"

    def set_properties(self):
        self.properties = [
                      # main
                      Field("author", "reference auth_user"),
                      Field("author_nickname", "string"),
                      Field("title", "string"),
                      Field("description", "text"),
                      Field("picture", "upload"),
                      Field("draft", "boolean"),
                      Field("tags", "list:string"),
                      # control
                      Field("content_type_id", "integer"),
                      Field("content_type", "string"),
                      Field("slug", "string"),
                      Field("search_index", "text"),
                      Field("publish_date", "datetime"),
                      Field("publish_tz", "string"),
                      # privacy
                      Field("privacy", "integer"),
                      Field("license", "string"),
                      # counters
                      Field("likes", "integer"),
                      Field("dislikes", "integer"),
                      Field("views", "integer"),
                      Field("responses", "integer"),
                      Field("favorited", "integer"),
                      # lists
                      Field("subscribers", "list:string"),
                     ]

        self.visibility = {
                     #'author': (False, True),
                     'author_nickname': (False, True),
                     "content_type": (False, False),
                     "slug": (False, False),
                     "search_index": (False, False),
                     "publish_tz": (False, False),
                     "subscribers": (False, False)
                     }
        # representation = {'tele': lambda v: XML("<b>%s</b>" % v)}
        # widgets = {'tele': None}
        # labels = {'email': "EMAIL"}
        # comments = {'email': "Seu E-mail"}

    def set_validators(self):
        from gluon import current
        session = current.session
        self.entity.author_nickname.compute = lambda row: self.db.auth_user[row.author].nickname
        self.entity.author.default = session.auth.user.id if session.auth else None

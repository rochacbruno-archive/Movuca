# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseModel
from gluon.validators import *
from gluon import current


class Article(BaseModel):
    tablename = "article"

    def set_properties(self):
        self.fields = [
                      # main
                      Field("author", "reference auth_user"),
                      Field("author_nickname", "string"),
                      Field("title", "string"),
                      Field("description", "text"),
                      Field("picture", "upload"),
                      Field("thumbnail", "upload"),
                      Field("draft", "boolean", default=False),
                      Field("tags", "list:string"),
                      Field("keywords", "string"),
                      # control
                      Field("content_type_id", "reference content_type"),
                      Field("content_type", "string"),
                      Field("slug", "string"),
                      Field("search_index", "text"),
                      Field("publish_date", "datetime"),
                      Field("publish_tz", "string"),
                      # privacy
                      Field("privacy", "integer"),
                      Field("license", "string"),
                      # counters
                      Field("likes", "integer", default=0),
                      Field("dislikes", "integer", default=0),
                      Field("views", "integer", default=0),
                      Field("responses", "integer", default=0),
                      Field("favorited", "integer", default=0),
                      # lists
                      Field("subscriptions", "integer", default=0),
                     ]

        self.visibility = {
                     'author': (False, True),
                     'author_nickname': (False, True),
                     "content_type": (False, False),
                     "search_index": (False, False),
                     "publish_tz": (False, False),
                     "content_type_id": (False, True),
                     "likes": (False, True),
                     "dislikes": (False, True),
                     "views": (False, True),
                     "responses": (False, True),
                     "favorited": (False, True),
                     "subscriptions": (False, True),
                     "draft": (False, False),
                     "keywords": (False, False),
                     }

        self.computations = {
          "slug": lambda r: IS_SLUG()(r.title)[0],
          "author_nickname": lambda r: r.author.nickname
        }

        # representation = {'tele': lambda v: XML("<b>%s</b>" % v)}
        # widgets = {'tele': None}
        # labels = {'email': "EMAIL"}
        # comments = {'email': "Seu E-mail"}

    def set_validators(self):
        T = current.T
        session = self.db.session
        self.entity.publish_date.default = current.request.now
        self.entity.author_nickname.compute = lambda row: self.db.auth_user[row.author].nickname
        self.entity.author.default = session.auth.user.id if session.auth else None
        self.entity.privacy.requires = IS_IN_SET([
                                                 ("1", T("Public")),
                                                 ("2", T("Contacts & Groups")),
                                                 ("3", T("Contacts")),
                                                 ("4", T("Groups")),
                                                  ],
                                                  zero=None)


class ContentType(BaseModel):
    tablename = "content_type"
    format = "%(identifier)s"

    def set_properties(self):
        self.fields = [
            Field("title", notnull=True),
            Field("description"),
            Field("identifier", unique=True, notnull=True),
            Field("classname", unique=True, notnull=True),
            Field("tablename", unique=True, notnull=True),
            Field("viewname", "string"),
            Field("childs", "integer", notnull=True, default=1),
        ]


class Favoriters(BaseModel):
    tablename = "article_favoriters"

    def set_properties(self):
        self.fields = [
            Field("article_id", "reference article", notnull=True),
            Field("user_id", "reference auth_user", notnull=True),
        ]


class Subscribers(BaseModel):
    tablename = "article_subscribers"

    def set_properties(self):
        self.fields = [
            Field("article_id", "reference article", notnull=True),
            Field("user_id", "reference auth_user", notnull=True),
        ]


class Likers(BaseModel):
    tablename = "article_likers"

    def set_properties(self):
        self.fields = [
            Field("article_id", "reference article", notnull=True),
            Field("user_id", "reference auth_user", notnull=True),
        ]


class Dislikers(BaseModel):
    tablename = "article_dislikers"

    def set_properties(self):
        self.fields = [
            Field("article_id", "reference article", notnull=True),
            Field("user_id", "reference auth_user", notnull=True),
        ]

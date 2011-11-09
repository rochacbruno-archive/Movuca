# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseModel, BaseAuth
from gluon.validators import *


class User(BaseAuth):
    properties = [
                  # Person info
                  Field("nickname"),
                  Field("tagline"),
                  Field("twitter", "string"),
                  Field("facebook", "string"),
                  Field("website", "string"),
                  Field("avatar", "upload"),
                  Field("thumbnail", "upload"),
                  Field("photo_source", "string"),
                  Field("about", "text"),
                  Field("gender", "string"),
                  Field("birthdate", "datetime"),
                  # Preferences
                  Field("privacy", "integer", notnull=True, default=1),  # 1 = public, 2 = contacts, 3 = private
                  Field("facebookid", "string"),
                  Field("registration_type", "integer", notnull=True, default=1),  # 1 = local, 2 = Facebook
                  # counters
                  Field("articles", "integer", notnull=True, default=0),
                  Field("draft_articles", "integer", notnull=True, default=0),
                  Field("messages", "integer", notnull=True, default=0),
                  Field("draft_messages", "integer", notnull=True, default=0),
                  Field("unread_messages", "integer", notnull=True, default=0),
                  Field("sent_messages", "integer", notnull=True, default=0),
                  Field("comments", "integer", notnull=True, default=0),
                  Field("rating_count", "integer", notnull=True, default=0),
                  Field("rating_total", "integer", notnull=True, default=0),
                  Field("rating_average", "integer", notnull=True, default=0),
                  Field("threads", "integer", notnull=True, default=0),
                  Field("responses", "integer", notnull=True, default=0),
                  Field("groups", "integer", notnull=True, default=0),
                  Field("contacts", "integer", notnull=True, default=0),
                  Field("pages", "integer", notnull=True, default=0),
                  Field("pictures", "integer", notnull=True, default=0),
                  Field("favorites", "integer", notnull=True, default=0),
                  # location
                  Field("country", "string"),
                  Field("city", "string"),
                  Field("languages", "list:string"),
                 ]

    register_visibility = {
                          "birthdate": (True, True)
                          }

    profile_visibility = {
                          "privacy": (True, True),
                          "nickname": (True, True),
                          "tagline": (True, True),
                          "twitter": (True, True),
                          "facebook": (True, True),
                          "website": (True, True),
                          "avatar": (True, True),
                          "photo_source": (True, True),
                          "about": (True, True),
                          "gender": (True, True),
                          "birthdate": (True, True),
                          "country": (True, True),
                          "city": (True, True),
                          "languages": (True, True),
                         }

    def set_validators(self):
        self.entity.nickname.requires = IS_NOT_IN_DB(self.db, self.entity.nickname)


class Category(BaseModel):
    tablename = "category"
    properties = [Field("title"),
                  Field("user", "integer")]

    def set_validators(self):
        from gluon.validators import IS_IN_DB
        self.entity.user.requires = IS_IN_DB(self.db, 'auth_user.id')

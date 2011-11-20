# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseAuth
from gluon.validators import IS_NOT_IN_DB, IS_IN_SET, IS_EMPTY_OR, IS_DATE, IS_URL
from helpers.images import THUMB2


class User(BaseAuth):
    def set_properties(self):
        request = self.db.request
        self.fields = [
                      # Person info
                      Field("nickname"),
                      Field("tagline"),
                      Field("twitter", "string"),
                      Field("facebook", "string"),
                      Field("website", "string"),
                      Field("avatar", "upload"),
                      Field("thumbnail", "upload"),
                      Field("photo_source", "integer", default=1),
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
                      Field("userpages", "integer", notnull=True, default=0),
                      Field("pictures", "integer", notnull=True, default=0),
                      Field("favorites", "integer", notnull=True, default=0),
                      Field("likes", "integer", notnull=True, default=0),
                      Field("dislikes", "integer", notnull=True, default=0),
                      Field("subscriptions", "integer", notnull=True, default=0),
                      # location
                      Field("country", "string"),
                      Field("city", "string"),
                      Field("languages", "list:string"),
                     ]

        self.register_visibility = {
                              "birthdate": (True, True)
                              }

        self.profile_visibility = {
                              "privacy": (True, True),
                              "nickname": (True, True),
                              "tagline": (True, True),
                              "twitter": (True, True),
                              "facebook": (True, True),
                              "website": (True, True),
                              "avatar": (True, True),
                              "thumbnail": (True, True),
                              "photo_source": (True, True),
                              "about": (True, True),
                              "gender": (True, True),
                              "birthdate": (True, True),
                              "country": (True, True),
                              "city": (True, True),
                              "languages": (True, True),
                             }

        self.computations = {
          "thumbnail": lambda r: THUMB2(r['avatar'], gae=request.env.web2py_runtime_gae)
        }

    def set_validators(self):
        #from config import Config
        #config = Config()
        #from gluon import current
        #T = current.T
        config = self.db.config
        T = self.db.T
        request = self.db.request
        self.entity.nickname.requires = IS_EMPTY_OR(IS_NOT_IN_DB(self.db, self.entity.nickname))
        self.entity.twitter.requires = IS_EMPTY_OR(IS_NOT_IN_DB(self.db, self.entity.twitter))
        self.entity.facebook.requires = IS_EMPTY_OR(IS_NOT_IN_DB(self.db, self.entity.facebook))

        self.entity.photo_source.requires = IS_IN_SET(config.get_list('auth', 'photo_source'))
        self.entity.gender.requires = IS_IN_SET(config.get_list('auth', 'gender'))
        self.entity.privacy.requires = IS_IN_SET(config.get_list('auth', 'privacy'))
        #date format not allowed on gae
        if not request.env.web2py_runtime_gae:
            self.entity.birthdate.requires = IS_DATE(format=str(T('%Y-%m-%d')))

        self.entity.website.requires = IS_EMPTY_OR(IS_URL())

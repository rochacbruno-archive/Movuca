# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseAuth, BaseModel
from gluon.validators import IS_NOT_IN_DB, IS_IN_SET, IS_EMPTY_OR, IS_DATE, IS_URL
from helpers.images import THUMB2
from gluon import CAT, A, IMG, XML, BR, EM


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


class UserTimeLine(BaseModel):
    tablename = "user_timeline"

    def set_properties(self):
        self.fields = [
            Field("user_id", "reference auth_user"),
            Field("nickname", "string"),
            Field("event_type", "string"),
            Field("event_to", "string"),
            Field("event_reference", "integer"),
            Field("event_text", "text"),
            Field("event_image", "string"),
            Field("event_link", "string"),
        ]

        self.representation = {
          "created_on": lambda v: self.db.pdate(v)
        }

    def set_fixtures(self):
        T = self.db.T
        CURL = self.db.CURL
        self.entity._event_types = {
            "new_article": CAT(A(IMG(_src="%(event_image)s"), _href="%(event_link)s"),
                               A(T("%(nickname)s added new %(event_to)s: %(event_text)s"), _href=CURL('article', 'show') + "/%(event_link)s")),
            "update_article": CAT(A(IMG(_src="%(event_image)s"), _href="%(event_link)s"),
                               A(T("%(nickname)s updated an %(event_to)s: %(event_text)s"), _href=CURL('article', 'show') + "/%(event_link)s")),
            "new_contact": CAT(A(IMG(_src="%(event_image)s"), _href="%(event_link)s"),
                               A(T("%(nickname)s added %(event_to)s as a new contact"), _href="%(event_link)s")),
            "new_article_comment": CAT(A(T("%(nickname)s commented on %(event_to)s: %(event_text)s"), _href=CURL('article', 'show') + "/%(event_link)s")),
            "liked": CAT(A(XML(T("%(nickname)s liked the %(event_to)s: <p>%(event_text)s</p>")), _href=CURL('article', 'show') + "/%(event_link)s")),
            "subscribed": CAT(A(T("%(nickname)s subscribed to %(event_to)s updates: %(event_text)s"), _href=CURL('article', 'show') + "/%(event_link)s")),
            "favorited": CAT(A(T("%(nickname)s favorited the %(event_to)s: %(event_text)s"), _href=CURL('article', 'show') + "/%(event_link)s")),
            "disliked": CAT(A(T("%(nickname)s disliked the %(event_to)s: %(event_text)s"), _href=CURL('article', 'show') + "/%(event_link)s")),
            "new_picture": CAT(A(T("%(nickname)s added new picture"), _href="%(event_link)s"),
                               A(IMG(_src="%(event_image)s"), _href="%(event_link)s")),
            "new_picture_comment": CAT(A(T("%(nickname)s commented on %(event_to)s picture"), _href="%(event_link)s"),
                               A(IMG(_src="%(event_image)s"), _href="%(event_link)s")),
            "wrote_on_wall": CAT(A(T("%(nickname)s wrote on %(event_to)s wall: %(event_text)s"), _href="%(event_link)s")),
        }
        self.entity._new_event = self.new_event

    def new_event(self, form=None, v=None):
        if not v:
            v = self.db.request.vars
        elif v == 'form':
            v = form.vars
        else:
            from gluon.storage import Storage
            v = Storage(v)

        event_text = v.event_text or v.comment_text or ' '
        data = dict(
            user_id=int(v.user_id),
            nickname=v.nickname,
            event_type=v.event_type,
            event_image=v.event_image,
            event_to=v.event_to,
            event_reference=int(v.event_reference),
            event_text=event_text[:50],
            event_link=v.event_link
        )
        self.entity.insert(**data)
        self.db.commit()

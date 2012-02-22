# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseAuth, BaseModel
from gluon.validators import IS_NOT_IN_DB, IS_IN_SET, IS_EMPTY_OR, IS_DATE, IS_URL, IS_SLUG, IS_NOT_EMPTY, IS_LIST_OF
from helpers.images import THUMB2


class User(BaseAuth):
    def set_properties(self):
        request = self.db.request
        T = self.db.T
        self.fields = [
                      # Person info
                      Field("nickname", notnull=True),
                      Field("tagline"),
                      Field("twitter", "string"),
                      Field("facebook", "string"),
                      Field("website", "string"),
                      Field("extra_links", "list:string"),
                      Field("avatar", "upload"),
                      Field("thumbnail", "upload"),
                      Field("photo_source", "integer", default=1),
                      Field("about", "text"),
                      Field("gender", "string"),
                      Field("birthdate", "date"),
                      # Preferences
                      Field("privacy", "integer", notnull=True, default=1),  # 1 = public, 2 = contacts, 3 = private
                      Field("facebookid", "string"),
                      Field("googleid", "string"),
                      Field("googlepicture", "string"),
                      Field("registration_type", "integer", notnull=True, default=1),  # 1 = local, 2 = Facebook, 3 - google
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
                      Field("isfollowing", "integer", notnull=True, default=0),
                      Field("followers", "integer", notnull=True, default=0),
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
                              "nickname": (True, True)
                              }

        self.profile_visibility = {
                              "privacy": (True, True),
                              "nickname": (True, True),
                              "tagline": (True, True),
                              "twitter": (True, True),
                              "facebook": (True, True),
                              "website": (True, True),
                              "extra_links": (True, True),
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
          "thumbnail": lambda r: THUMB2(r['avatar'], gae=request.env.web2py_runtime_gae),
        }

        self.labels = {
          "first_name": T("First Name"),
          "last_name": T("Last Name"),
          "email": T("E-mail"),
          "password": T("Password"),
          "nickname": T("Nickname - will be used for links and signatures"),
          "privacy": T("Privacy - Profile visibility"),
          "tagline": T("Tagline -  short sentence about you"),
          "twitter": T("twitter - your twitter username"),
          "facebook": T("Facebook - Your facebook username or id"),
          "website": T("website - your primary link on the web"),
          "extra_links": T("Extra links - up to 5 links for your profiles (blog, github, company etc)"),
          "avatar": T("Avatar - Used only when photo source is 'upload'"),
          "photo_source": T("Photo source - you can use the avatar from:"),
          "about": T("about you"),
          "gender": T("Gender"),
          "birthdate": T("Birth Date"),
          "country": T("Country"),
          "city": T("City"),
          "languages": T("Languages")
        }

    def set_validators(self):
        config = self.db.config
        T = self.db.T
        request = self.db.request
        self.entity.nickname.requires = [IS_SLUG(), IS_NOT_IN_DB(self.db, self.entity.nickname)]
        self.entity.twitter.requires = IS_EMPTY_OR(IS_NOT_IN_DB(self.db, self.entity.twitter))
        self.entity.facebook.requires = IS_EMPTY_OR(IS_NOT_IN_DB(self.db, self.entity.facebook))

        self.entity.extra_links.requires = IS_EMPTY_OR(IS_LIST_OF(IS_URL(allowed_schemes=['https', 'http'], prepend_scheme='http')))

        self.entity.photo_source.requires = IS_IN_SET(config.get_list('auth', 'photo_source'))
        self.entity.gender.requires = IS_EMPTY_OR(IS_IN_SET(config.get_list('auth', 'gender')))
        self.entity.privacy.requires = IS_IN_SET(config.get_list('auth', 'privacy'))
        #date format not allowed on gae
        if not request.env.web2py_runtime_gae:
            self.entity.birthdate.requires = IS_EMPTY_OR(IS_DATE(format=str(T('%Y-%m-%d'))))

        self.entity.website.requires = IS_EMPTY_OR(IS_URL())


class UserBoard(BaseModel):
    tablename = "user_board"

    def set_properties(self):
        self.fields = [
            Field("user_id", "reference auth_user"),
            Field("writer", "reference auth_user"),
            Field("board_text", "string"),
        ]

        self.visibility = {
            "user_id": (False, False),
            "writer": (False, False)
        }

        self.validators = {
            "board_text": IS_NOT_EMPTY()
        }

    def set_fixtures(self):
        self.entity._write_on_board = self.write_on_board

    def write_on_board(self, user_id, writer, text):
        self.entity.insert(user_id=user_id, writer=writer, board_text=text)
        self.db.commit()


class UserContact(BaseModel):
    tablename = "user_contact"

    def set_properties(self):
        self.fields = [
            Field("follower", "reference auth_user"),
            Field("followed", "reference auth_user"),
        ]

    def set_fixtures(self):
        self.entity._relation = self.relation

    def relation(self, a, b):
        if a == b:
            return 'yourself'
        a_follows_b = self.db((self.entity.follower == a) & ((self.entity.followed == b))).count()
        b_follows_a = self.db((self.entity.follower == b) & ((self.entity.followed == a))).count()
        if all([a_follows_b, b_follows_a]):
            return 'contacts'
        elif a_follows_b:
            return 'following'
        elif b_follows_a:
            return 'follower'
        else:
            return 'unknown'


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
            Field("event_image_to", "string"),
            Field("event_link_to", "string"),
        ]

        self.representation = {
          "created_on": lambda v: self.db.pdate(v)
        }

    def set_fixtures(self):
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
            event_link=v.event_link,
            event_image_to=v.get("event_image_to", ""),
            event_link_to=v.get("event_link_to", ""),
        )
        self.entity.insert(**data)
        self.db.commit()

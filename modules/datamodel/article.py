# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseModel
from gluon.validators import *
from gluon import current
from helpers.widgets import StringListWidget
from helpers.customvalidators import COMMA_SEPARATED_LIST
from gluon import SQLFORM


class Article(BaseModel):
    tablename = "article"

    def set_properties(self):
        T = self.db.T
        self.fields = [
                      # main
                      Field("author", "reference auth_user"),
                      Field("author_nickname", "string"),
                      Field("title", "string"),
                      Field("description", "text"),
                      Field("picture", "upload"),
                      Field("medium_thumbnail", "upload"),
                      Field("thumbnail", "upload"),
                      Field("draft", "boolean", default=False),
                      Field("category_id", "list:reference article_category"),
                      Field("tags", "list:string"),
                      Field("keywords", "string"),
                      # control
                      Field("content_type_id", "reference content_type"),
                      Field("content_type", "string"),
                      Field("slug", "string"),
                      Field("search_index", "text"),
                      Field("publish_date", "datetime"),
                      Field("publish_tz", "string"),
                      Field("featured", "boolean", default=False),
                      # privacy
                      Field("privacy", "integer", default=1),
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

        self.widgets = {
            "tags": StringListWidget.widget
        }

        self.visibility = {
                     'author': (False, True),
                     'author_nickname': (False, True),
                     "content_type": (False, False),
                     "search_index": (False, False),
                     "publish_date": (False, False),
                     "publish_tz": (False, False),
                     "content_type_id": (False, True),
                     "likes": (False, True),
                     "dislikes": (False, True),
                     "views": (False, True),
                     "responses": (False, True),
                     "favorited": (False, True),
                     "subscriptions": (False, True),
                     #"draft": (False, False),
                     "keywords": (False, False),
                     }

        self.computations = {
          "slug": lambda r: IS_SLUG()(r.title)[0],
          "author_nickname": lambda r: self.db.auth_user[r.author].nickname
        }

        self.labels = {
          "title": T("Title"),
          "description": T("Short Description"),
          "picture": T("Picture"),
          "category_id": T("Category"),
          "tags": T("Tags"),
          "privacy": T("Privacy"),
          "license": T("License"),
          "draft": T("Draft")
        }

        self.comments = {
          "description": T("Text to be shown at home page, email and RSS"),
          "picture": T("Optional picture to be shown at home page, email and RSS (a thumbnail will be created)"),
          "tags": T("Tag is used for search and to find related articles. (comma separated)"),
          "privacy": T("Who can view this publication?"),
          "draft": T("Check to save as a draft")
        }

        self.validators = {
          "title": IS_NOT_EMPTY(),
          "description": IS_NOT_EMPTY(),
          "picture": IS_EMPTY_OR(IS_IMAGE()),
          "license": IS_IN_SET(self.db.config.get_list('article', 'license'), zero=None),
          #"tags": IS_IN_SET(['teste', 'bla', 'bruno'], multiple=True),
          "tags": COMMA_SEPARATED_LIST()
        }

        # representation = {'tele': lambda v: XML("<b>%s</b>" % v)}
        # widgets = {'tele': None}
        # labels = {'email': "EMAIL"}
        # comments = {'email': "Seu E-mail"}

    def set_validators(self):
        T = self.db.T
        session = self.db.session
        self.entity.publish_date.default = current.request.now
        self.entity.author_nickname.compute = lambda row: self.db.auth_user[row.author].nickname
        self.entity.author.default = session.auth.user.id if session.auth else None
        # self.entity.privacy.requires = IS_IN_SET([
        #                                          ("1", T("Public")),
        #                                          ("2", T("Contacts & Groups")),
        #                                          ("3", T("Contacts")),
        #                                          ("4", T("Groups")),
        #                                           ],
        #                                           zero=None)


class ContentType(BaseModel):
    tablename = "content_type"
    format = "%(identifier)s"

    def set_properties(self):
        self.fields = [
            Field("title", notnull=True),
            Field("description"),
            Field("identifier", unique=True, notnull=True),
            Field("classname", notnull=True),
            Field("tablename", notnull=True),
            Field("viewname", "string"),
            Field("childs", "integer", notnull=True, default=1),
        ]

    def set_fixtures(self):
        if not self.db(self.entity).count():
            self.entity.insert(
               title="Article",
               description="User Article",
               identifier="Article",
               classname="Article",
               tablename="article_data",
               viewname="article",
               )
            self.db.commit()


class Category(BaseModel):
    tablename = "article_category"
    format = "%(name)s"

    def set_properties(self):
        self.fields = [
            Field("name", "string"),
            Field("description", "text"),
            Field("picture", "upload"),
            Field("thumbnail", "upload"),
            Field("parent_id", "reference article_category"),
            Field("content_type", "reference content_type"),
        ]

    def set_fixtures(self):
        if not self.db(self.entity).count():
            self.entity.insert(
               name="Article",
               description="General article",
               content_type=self.db(self.db.content_type.identifier == 'Article').select().first().id
               )
            self.db.commit()


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


class Comments(BaseModel):
    tablename = "article_comments"

    def set_properties(self):
        self.fields = [
            Field("article_id", "reference article", notnull=True),
            Field("user_id", "reference auth_user", notnull=True),
            Field("nickname", notnull=True),
            Field("parent_id", "reference article_comments"),
            Field("replies", "integer", notnull=True, default=0),
            Field("comment_text", "text", notnull=True),
            Field("commenttime", "datetime"),
            Field("answer", "boolean", default=False),
        ]

        self.visibility = {
            "article_id": (False, False),
            "user_id": (False, False),
            "parent_id": (False, False),
            "commenttime": (False, False),
            "replies": (False, False),
            "answer": (False, False),
        }

        self.computations = {
          "nickname": lambda r: self.db.auth_user[r.user_id].nickname
        }

        self.validators = {
          "comment_text": IS_LENGTH(1024, 2)
        }


class CommentVotes(BaseModel):
    tablename = "article_comment_votes"

    def set_properties(self):
        self.fields = [
            Field("comment_id", "reference article_comments", notnull=True),
            Field("user_id", "reference auth_user", notnull=True),
            Field("vote", "integer", notnull=True, default=1),
            Field("unikey", unique=True, notnull=True)
        ]

        self.validators = {
            "vote": IS_IN_SET([(0, "Down"), (1, "Up")])
        }

        self.computations = {
            "unikey": lambda row: "%(user_id)s_%(comment_id)s_%(vote)s" % row
        }

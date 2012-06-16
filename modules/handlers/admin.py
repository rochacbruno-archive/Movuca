# coding: utf-8

from handlers.base import Base
from gluon import *
from plugin_ckeditor import CKEditor


class Admin(Base):
    def start(self):
        from movuca import DataBase, User, UserTimeLine, UserContact, UserBoard
        from datamodel.article import Article, ContentType, Category, Favoriters, Subscribers, Likers, Dislikers, Comments
        from datamodel.ads import Ads
        from datamodel.contenttypes import Article as ArticleData
        from datamodel.contenttypes import CookRecipe, CookRecipeBook, CodeRecipe, Product
        from datamodel.notification import NotificationPermission, Notification, EmailTemplate
        from datamodel.menu import Menu
        self.db = DataBase([User,
                       UserTimeLine,
                       ContentType,
                       Category,
                       Article,
                       Favoriters,
                       Subscribers,
                       Likers,
                       Dislikers,
                       Comments,
                       UserBoard,
                       UserContact,
                       CookRecipe,
                       CookRecipeBook,
                       CodeRecipe,
                       Product,
                       Ads,
                       NotificationPermission,
                       Notification,
                       EmailTemplate,
                       Menu
                       ])
        self.db.ArticleData = ArticleData(self.db).entity

        # visibility

        comments_fields = ['article_id', "user_id", "nickname", "parent_id", "replies", "commenttime", "answer"]
        for f in comments_fields:
            self.db.article_comments[f].readable = self.db.article_comments[f].writable = True
        ckeditor = CKEditor()
        self.db.article_comments.comment_text.widget = ckeditor.widget
        # visibility

        if not self.db.auth.has_membership("admin"):
            redirect(self.db.CURL("home", "index"))

    def pre_render(self):
        # obrigatorio ter um config, um self.response|request, que tenha um render self.response.render
        self.response = self.db.response
        self.request = self.db.request
        self.config = self.db.config
        self.session = self.db.session
        self.T = self.db.T
        self.CURL = self.db.CURL
        self.get_image = self.db.get_image
        self.context.theme_name = self.config.theme.name
        self.context.header_enabled = False
        #self.view = "app/home.html"
        self.context.content_types = self.context.content_types or self.allowed_content_types()
        self.context.categories = self.context.categories = self.allowed_categories()

    def configindex(self):
        tables = self.config._db.tables
        links = [A(table, _href=URL('config', table), _class="") for table in tables]
        self.context.object = UL(*links, _style="list-style:none;", _class="nav nav-list")

    def adminindex(self):
        tables = self.db.tables
        allowed = "auth_user,auth_group,auth_membership,content_type,article_category,article,article_comments,notification,email_template,menu, internal_page".split(',')
        links = [A(table, _href=URL('adm', table), _class="") for table in tables if table in allowed]
        self.context.object = UL(*links, _style="list-style:none;", _class="nav nav-list")

    def contenttypes(self):
        query = self.db.content_type.id > 0
        self.context.object = SQLFORM.grid(query)

    def tables(self):
        tablename = self.request.function
        if 'view' in self.request.args or 'edit' in self.request.args:
            ignore_rw = True
        else:
            ignore_rw = False
        self.context.object = SQLFORM.smartgrid(self.db[tablename], ignore_rw=ignore_rw)

    def simpletables(self):
        tablename = self.request.function
        query = self.db[tablename].id > 0
        self.context.object = SQLFORM.grid(query)

    def configtables(self):
        tablename = self.request.function
        self.context.object = SQLFORM.smartgrid(self.config._db[tablename])

    def configsimpletables(self):
        tablename = self.request.function
        query = self.config._db[tablename].id > 0
        self.context.object = SQLFORM.grid(query)

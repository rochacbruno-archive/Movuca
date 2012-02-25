# coding: utf-8

from handlers.base import Base
from gluon import *


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
        #self.view = "app/home.html"
        self.context.content_types = self.context.content_types or self.db(self.db.ContentType).select()

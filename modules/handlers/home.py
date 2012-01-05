# -*- coding: utf-8 -*-

from handlers.base import Base


class Home(Base):
    def start(self):
        from movuca import DataBase, User
        from datamodel.article import Article, ContentType, Category
        self.db = DataBase([User, ContentType, Category, Article])

    def pre_render(self):
        # obrigatorio ter um config, um self.response|request, que tenha um render self.response.render
        self.response = self.db.response
        self.request = self.db.request
        self.config = self.db.config
        #self.view = "app/home.html"

    def last_articles(self):
        from helpers.article import latest_articles
        self.context.latest_articles = latest_articles(self.db)

    def featured(self):
        self.context.featured = self.db(self.db.Article.featured == True).select(limitby=(0, 4), orderby="<random>")

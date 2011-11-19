# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import SQLFORM


class Article(Base):
    def start(self):
        from movuca import DataBase, User
        from datamodel.article import Article, ContentType
        self.db = DataBase([User, ContentType, Article])

    def pre_render(self):
        # obrigatorio ter um config, um self.response|request, que tenha um render self.response.render
        self.response = self.db.response
        self.request = self.db.request
        self.config = self.db.config
        #self.view = "app/home.html"

    def lastest_articles(self):
        from helpers.article import latest_articles
        self.context.latest_articles = latest_articles(self.db)

    def show(self):
        article_id = self.request.args(0)
        article_slug = self.request.args(1)
        queries = [self.db.article.id == article_id]
        if article_slug:
            queries.append(self.db.article.slug == article_slug)
        query = reduce(lambda a, b: (a & b), queries)
        self.context.article = self.db(query).select().first()

    def edit(self):
        self.show()
        self.context.form = SQLFORM(self.db.article, self.context.article).process()

    def new(self):
        arg = self.request.args(0)
        query = self.db.content_type.identifier == arg
        content_type = self.db(query).select().first()
        from datamodel import contenttypes
        content = getattr(contenttypes, content_type.classname)(self.db)
        self.context.form = SQLFORM(self.db.article).process()
        self.context.form2 = SQLFORM(content.entity).process()

# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import SQLFORM, redirect, URL
from helpers.images import THUMB2
import os


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
        self.session = self.db.session
        self.T = self.db.T
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
        content_type = self.db.content_type(self.context.article.content_type_id)
        from datamodel import contenttypes
        content = getattr(contenttypes, content_type.classname)(self.db)
        article_data = self.db(content.entity.article_id == self.context.article.id).select().first()
        self.context.form2 = SQLFORM(content.entity, article_data).process()

    def new(self):
        arg = self.request.args(0)
        query = self.db.content_type.identifier == arg
        content_type = self.db(query).select().first() or redirect(URL('home', 'index'))
        from datamodel import contenttypes
        content = getattr(contenttypes, content_type.classname)(self.db)
        path = os.path.join(self.request.folder, 'uploads/')
        if not self.request.env.web2py_runtime_gae:
            self.db.article.picture.uploadfolder = path
            self.db.article.thumbnail.uploadfolder = path
        else:
            self.db.article.picture.uploadfield = "picture_blob"
            self.db.article.thumbnail.uploadfield = "thumbnail_blob"
        self.db.article.author.default = self.session.auth.user.id
        self.db.article.thumbnail.compute = lambda r: THUMB2(r['picture'], gae=self.request.env.web2py_runtime_gae)
        self.db.article.content_type_id.default = content_type.id
        self.context.form = SQLFORM.factory(self.db.article, content.entity, table_name="article")
        if self.context.form.process().accepted:
            try:
                id = self.db.article.insert(**self.db.article._filter_fields(self.context.form.vars))
                self.context.form.vars.article_id = id
                self.context.form.vars.type_id = content_type.id
                id = content.entity.insert(**content.entity._filter_fields(self.context.form.vars))
            except Exception:
                self.db.rollback()
                self.response.flash = self.T("error including %s." % content_type.title)
            else:
                self.db.commit()
                self.response.flash = self.T("%s included." % content_type.title)

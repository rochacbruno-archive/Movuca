# coding: utf-8

from handlers.base import Base
from gluon import SQLFORM, redirect, A, IMG, SPAN, URL


class Page(Base):
    def start(self):
        from movuca import DataBase, User
        from datamodel.page import Page
        from datamodel.article import ContentType, Category
        self.db = DataBase([User, Page, Category, ContentType])

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
        self.context.content_types = self.context.content_types or self.allowed_content_types()
        self.context.categories = self.context.categories = self.allowed_categories()

    def get(self):
        try:
            self.context.page = self.db.Page[int(self.request.args(0))]
        except Exception:
            self.context.page = self.db(self.db.Page.slug == self.request.args(0)).select().first()

    def show(self):
        self.get()

    def new(self):
        self.context.form = SQLFORM(self.db.Page, formstyle='divs').process()

    def edit(self):
        self.get()
        self.context.form = SQLFORM(self.db.Page, self.context.page, formstyle='divs').process()

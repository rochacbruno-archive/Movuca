# coding: utf-8

from handlers.base import Base
from gluon import SQLFORM, redirect, A, IMG, SPAN, URL


class Content(Base):
    def start(self):
        from movuca import DataBase, User
        from datamodel.content import report
        from datamodel.article import ContentType, Category, Article
        self.db = DataBase([User, Page, Category, ContentType, Article])
        if self.db.request.function != "show" and not self.db.auth.has_membership("admin"):
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
        self.context.content_types = self.context.content_types or self.allowed_content_types()
        self.context.categories = self.context.categories = self.allowed_categories()

    def get(self):
        try:
            self.context.page = self.db.Page[int(self.request.args(0))]
        except Exception:
            self.context.page = self.db(self.db.Page.slug == self.request.args(0)).select().first()

        if not self.context.page:
            redirect(self.CURL('home', 'index'))

        self.response.meta.title = "%s | %s" % (
                                             self.context.page.title,
                                             self.db.config.meta.title,
                                            )

    def show(self):
        self.get()

    def new(self):
        self.context.form = SQLFORM(self.db.Page, formstyle='divs')
        if self.context.form.process().accepted:
            redirect(self.CURL("show", args=self.context.form.vars.id))

    def edit(self):
        self.get()
        self.context.form = SQLFORM(self.db.Page, self.context.page, formstyle='divs')
        if self.context.form.process().accepted:
            redirect(self.CURL("show", args=self.context.form.vars.id))

    def list(self):
        self.context.form = SQLFORM.grid(self.db.Page)

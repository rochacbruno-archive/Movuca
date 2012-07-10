# coding: utf-8

from handlers.base import Base
from gluon import SQLFORM, redirect, A, IMG, SPAN, URL, H1


class Page(Base):
    def start(self):
        from movuca import DataBase, User
        from datamodel.page import Page, Report
        from datamodel.article import ContentType, Category, Article
        self.db = DataBase([User, Page, Report, Category, ContentType, Article])
        if self.db.request.function not in ["show", "reportcontent"] and not self.db.auth.has_membership("admin"):
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
        self.response.meta.description = self.context.page.description
        self.response.meta.keywords = "vegan, vegetarian, vegano, vegetariano, vegetariana, receita, rede social," + ",".join(self.context.page.tags)
        self.response.meta.og_url = self.CURL("page", "show", args=[self.context.page.slug], scheme=True, host=True)

    def show(self):
        self.get()
        if self.context.page.redirect_url:
            redirect(self.context.page.redirect_url)

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
        if 'view' in self.request.args or 'edit' in self.request.args:
            ignore_rw = True
        else:
            ignore_rw = False
        self.context.form = SQLFORM.grid(self.db.Page, ignore_rw=ignore_rw)

    def reportcontent(self):
        if not self.db.auth.user:
            vrs = {"_next": self.CURL('page', 'reportcontent', args=self.db.request.args)}
            redirect(self.CURL('person', 'account', args=['login'], vars=vrs))

        self.response.meta.title = "%s | %s" % (
                                     self.db.T("Report content"),
                                     self.db.config.meta.title,
                                    )

        self.db.Report.content_type.default = self.db.T(self.db.request.args(0))
        self.db.Report.item_id.default = int(self.db.request.args(1))
        self.db.Report.slug.default = self.db.request.args(2)

        self.db.Report.content_type.writable = \
        self.db.Report.item_id.writable = \
        self.db.Report.slug.writable = False

        self.context.form = SQLFORM(self.db.Report, formstyle='divs')
        self.context.form.insert(0, H1(self.db.T("Report content or user")))

        if self.context.form.process().accepted:
            self.db.response.flash = self.db.T("Thank you for reporting this content")

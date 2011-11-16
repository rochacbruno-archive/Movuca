# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import UL, LI, SQLFORM


class Home(Base):
    def start(self):
        from movuca import Access, DataBase
        self.db = DataBase()
        self.access = Access(self.db)

    def build(self):
        self.user_list()
        self.user_form()

    def pre_render(self):
        # obrigatorio ter um config, um self.response, que tenha um render self.response.render
        self.response = self.db.response
        self.config = self.db.config
        self.view = "app/home.html"

    def user_list(self):
        table = self.access.entity
        records = self.db(table).select()
        self.context['users'] = UL(*[LI(user.first_name) for user in records])

    def user_form(self):
        self.context['userform'] = SQLFORM(self.access.entity).process()

# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import UL, LI


class Home(Base):
    def start(self):
        from movuca import Access, DataBase
        self.db = DataBase()
        self.access = Access(self.db)

    def build(self):
        self.user_list()

    def pre_render(self):
        self.context["pre"] = "ok"

    def user_list(self):
        table = self.access.entity
        records = self.db(table).select()
        self.context['users'] = UL(*[LI(user.first_name) for user in records])

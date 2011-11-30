# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import *


class Person(Base):
    def start(self):
        from movuca import DataBase, User, UserTimeLine
        self.db = DataBase([User, UserTimeLine])

    def pre_render(self):
        # obrigatorio ter um config, um self.response|request, que tenha um render self.response.render
        self.response = self.db.response
        self.request = self.db.request
        self.config = self.db.config
        self.session = self.db.session
        self.T = self.db.T
        self.CURL = self.db.CURL

    def get(self, query, orderby=None):
        timeline = self.db.UserTimeLine
        events = self.db(query).select(orderby=orderby or ~timeline.created_on)
        event_types = timeline._event_types
        self.context.timeline = \
             DIV(
                UL(
                    *[LI(XML(str(event_types[event.event_type]) % event),
                        _class="timeline-item")
                        for event in events],
                     **dict(_class="timeline-wrapper")
                  )
                )

    def usertimeline(self):
        user = self.request.args(0)
        query = self.db.UserTimeLine.user_id == user
        self.get(query)

    def publictimeline(self):
        self.get(self.db.UserTimeLine)

# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import *


class Person(Base):
    def start(self):
        from movuca import DataBase, User, UserTimeLine, UserContact
        self.db = DataBase([User, UserTimeLine, UserContact])

    def pre_render(self):
        # obrigatorio ter um config, um self.response|request, que tenha um render self.response.render
        self.response = self.db.response
        self.request = self.db.request
        self.config = self.db.config
        self.session = self.db.session
        self.T = self.db.T
        self.CURL = self.db.CURL

    def get_timeline(self, query, orderby=None):
        timeline = self.db.UserTimeLine
        events = self.db(query).select(orderby=orderby or ~timeline.created_on)
        event_types = timeline._event_types
        self.context.timeline = \
             DIV(
                UL(
                    *[LI(XML(str(event_types[event.event_type]) % event),
                        EM(self.db.pdate(event.created_on)),
                        _class="timeline-item")
                        for event in events],
                     **dict(_class="timeline-wrapper")
                  )
                )

    def usertimeline(self):
        user = self.request.args(0)
        query = self.db.UserTimeLine.user_id == user
        self.get_timeline(query)

    def publictimeline(self):
        self.get_timeline(self.db.UserTimeLine)

    def follow(self):
        follower = self.session.auth.user if self.session.auth else None
        followed = self.request.args(0)
        if follower and followed:
            self.db.UserContact.update_or_insert(follower=follower.id, followed=followed)
            self.db.commit()

    def unfollow(self):
        follower = self.session.auth.user if self.session.auth else None
        followed = self.request.args(0)
        if follower and followed:
            query = (self.db.UserContact.follower == follower.id) & (self.db.UserContact.followed == followed)
            self.db(query).delete()
            self.db.commit()

    def followers(self, arg=None):
        if arg:
            try:
                query = self.db.auth_user.id == int(self.request.args(0))
            except:
                query = self.db.auth_user.slug == self.request.args(0)

            followed = self.db(query).select().first()
        else:
            followed = self.session.auth.user if self.session.auth else redirect(self.CURL('home', 'index'))

        self.context.followers = self.db(self.db.UserContact.followed == followed.id).select()

    def following(self, arg=None):
        if arg:
            try:
                query = self.db.auth_user.id == int(self.request.args(0))
            except:
                query = self.db.auth_user.slug == self.request.args(0)

            follower = self.db(query).select().first()
        else:
            follower = self.session.auth.user if self.session.auth else redirect(self.CURL('home', 'index'))

        self.context.following = self.db(self.db.UserContact.follower == follower.id).select()

    def contacts(self, args=None):
        self.followers()
        self.following()
        followers = [follower.follower for follower in self.context.followers]
        following = [followed.followed for followed in self.context.following]
        friends = set()
        [friends.add(friend) for friend in followers if friend in following]
        [friends.add(friend) for friend in following if friend in followers]
        self.context.contacts = self.db(self.db.auth_user.id.belongs(friends)).select()

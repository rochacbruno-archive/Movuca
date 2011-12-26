# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import *
from helpers.person import contact_box


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
        if self.request.args(0):
            try:
                user = self.db.auth_user[int(self.request.args(0))]
            except Exception:
                user = self.db.auth_user(nickname=self.request.args(0))
        else:
            user = self.db.auth_user[self.session.auth.user.id]

        if user:
            query = self.db.UserTimeLine.user_id == user.id
            self.get_timeline(query)

    def publictimeline(self):
        self.get_timeline(self.db.UserTimeLine)

    def follow(self):
        follower = self.session.auth.user if self.session.auth else None
        try:
            followed = self.db.auth_user[int(self.request.args(0))]
        except:
            followed = self.db(self.db.auth_user.nickname == self.request.args(0)).select(0).first()

        yourself = followed.id == follower.id

        if follower and followed:
            if not yourself:
                self.db.UserContact.update_or_insert(follower=follower.id, followed=followed.id)
                self.db.commit()
                self.db.UserTimeLine._new_event(v={"user_id": follower.id,
                                                  "nickname": follower.nickname,
                                                  "event_type": "new_contact",
                                                  "event_image": followed.thumbnail,
                                                  "event_to": followed.nickname or followed.first_name,
                                                  "event_reference": followed.id,
                                                  "event_text": "",
                                                  "event_link": followed.nickname or followed.id})
                return contact_box(followed, 'contact', ajax=True)
            else:
                return self.T('You cannot follow yourself')
        else:
            return self.T('Error following')

    def unfollow(self):
        follower = self.session.auth.user if self.session.auth else None
        try:
            followed = self.db.auth_user[int(self.request.args(0))]
        except:
            followed = self.db(self.db.auth_user.nickname == self.request.args(0)).select(0).first()

        yourself = followed.id == follower.id

        if follower and followed:
            if not yourself:
                query = (self.db.UserContact.follower == follower.id) & (self.db.UserContact.followed == followed.id)
                self.db(query).delete()
                self.db.commit()
                return contact_box(followed, 'follower', ajax=True)
            else:
                return self.T('You cannot unfollow yourself')
        else:
            return self.T('Error unfollowing')

    def followers(self, arg=None):
        if arg:
            try:
                query = self.db.auth_user.id == int(self.request.args(0))
            except:
                query = self.db.auth_user.nickname == self.request.args(0)

            followed = self.db(query).select().first()
        else:
            followed = self.session.auth.user if self.session.auth else redirect(self.CURL('home', 'index'))

        self.context.followers = self.db(self.db.UserContact.followed == followed.id).select()

    def following(self, arg=None):
        if arg:
            try:
                query = self.db.auth_user.id == int(self.request.args(0))
            except:
                query = self.db.auth_user.nickname == self.request.args(0)

            follower = self.db(query).select().first()
        else:
            follower = self.session.auth.user if self.session.auth else redirect(self.CURL('home', 'index'))

        self.context.following = self.db(self.db.UserContact.follower == follower.id).select()

    def contacts(self, arg=None):
        self.followers(arg)
        self.following(arg)

        followers = [follower.follower for follower in self.context.followers]
        following = [followed.followed for followed in self.context.following]

        friends = set()

        [friends.add(friend) for friend in followers if friend in following]
        [friends.add(friend) for friend in following if friend in followers]

        self.context.contacts_list = friends
        self.context.followers_list = followers
        self.context.following_list = following

        if self.request.env.web2py_runtime_gae:
            queries = []
            for friend in friends:
                queries.append(self.db.auth_user.id == friend)
            query = reduce(lambda a, b: (a | b), queries)
            self.context.contacts = self.db(query).select()
        else:
            self.context.contacts = self.db(self.db.auth_user.id.belongs(friends)).select()

        from helpers.person import contact_box
        self.context.contact_box = contact_box

    def search(self, q):
        self.contacts()
        self.context.results = []

        if q:
            words = q.split()
            queries = []

            for word in words:
                queries.append(self.db.auth_user.first_name.like("%" + word + "%"))
                queries.append(self.db.auth_user.last_name.like("%" + word + "%"))
                queries.append(self.db.auth_user.email.like("%" + word + "%"))
                queries.append(self.db.auth_user.nickname.like("%" + word + "%"))
                queries.append(self.db.auth_user.about.like("%" + word + "%"))
                queries.append(self.db.auth_user.tagline.like("%" + word + "%"))

            query = reduce(lambda a, b: (a | b), queries)
            self.context.results = self.db(query & (self.db.auth_user.id != self.session.auth.user.id)).select()

            from helpers.person import contact_box
            self.context.contact_box = contact_box

        self.context.form = SQLFORM.factory(Field('q', default=q or ''), _method="GET")

    def show(self, uid):
        T = self.T
        try:
            user = self.db.auth_user[int(uid)]
        except Exception:
            user = self.db.auth_user(nickname=uid)
        self.context.user = user

        if self.session.auth and self.session.auth.user:
            self.context.buttons = CAT(
                                       TAG.BUTTON(T("Follow"), _class="alpha three columns"),
                                       TAG.BUTTON(T("Message"), _class="three columns"),
                                       TAG.BUTTON(T("Report/Block"), _class="omega three columns"),
                                       )

        self.context.resume = UL(
                                 LI(T("Wrote %s articles", user.articles)),
                                 LI(T("Has %s favorites", user.favorites)),
                                 LI(T("Has %s contacts", user.contacts)),
                                 LI(T("Liked %s articles", user.likes)),
                                 LI(T("Joined %s groups", user.groups)),
                                 _class="person-resume"
                                )

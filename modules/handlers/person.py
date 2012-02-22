# -*- coding: utf-8 -*-

###############################################################################
# Movuca - The Social CMS
# Copyright (C) 2012  Bruno Cezar Rocha <rochacbruno@gmail.com>

# License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
###############################################################################

from handlers.base import Base
from gluon import *
from helpers.person import contact_box
from movuca import DataBase, User, UserTimeLine, UserContact, UserBoard
from datamodel.article import ContentType
from handlers.notification import Notifier
from plugin_paginator import Paginator, PaginateSelector, PaginateInfo


class Person(Base):
    def start(self):
        self.db = DataBase([User, UserTimeLine, UserContact, UserBoard, ContentType])
        self.notifier = Notifier(self.db)

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
        self.context.use_facebook = self.db.config.auth.use_facebook
        self.context.use_google = self.db.config.auth.use_google
        self.mail = self.db.auth.settings.mailer
        self.context.content_types = self.db(self.db.ContentType).select()

    def check_if_allowed(self, row):
        if self.db.auth.user_id:
            relation = self.db.UserContact._relation(self.db.auth.user_id, row.user_timeline.user_id)
        else:
            relation = 'unknown'

        if row.user_timeline.user_id.privacy != 1 and \
               relation not in ['contacts', 'follower', 'yourself'] and \
                   not self.db.auth.has_membership("admin", self.db.auth.user_id):
            return False
        else:
            return True

    def get_private_timeline(self, query, orderby=None, limitby=None):
        timeline = self.db.UserTimeLine
        timeline.allowed = Field.Lazy(lambda row: self.check_if_allowed(row))
        rows = self.db(query).select(orderby=orderby or ~timeline.created_on, limitby=limitby or (0, 20))
        self.context.events = rows.find(lambda row: row.allowed() == True)

    def get_timeline(self, query, orderby=None, limitby=None, public=True):
        timeline = self.db.UserTimeLine
        if public:
            self.context.events = self.db(query).select(orderby=orderby or ~timeline.created_on, limitby=limitby or (0, 20))
        else:
            timeline.allowed = Field.Lazy(lambda row: self.check_if_allowed(row))
            rows = self.db(query).select(orderby=orderby or ~timeline.created_on, limitby=limitby or (0, 20))
            self.context.events = rows.find(lambda row: row.allowed() == True)

    def usertimeline(self):
        if self.request.args(0):
            try:
                user = self.db.auth_user[int(self.request.args(0))]
            except Exception:
                user = self.db.auth_user(nickname=self.request.args(0))
        else:
            user = self.db.auth_user[self.session.auth.user.id]
        self.context.user = user
        if self.request.extension == "html":
            self.show(user.id)
        if user:
            query = self.db.UserTimeLine.user_id == user.id
            #### pagination
            self.context.paginate_selector = PaginateSelector(paginates=(10, 25, 50, 100))
            self.context.paginator = Paginator(paginate=self.context.paginate_selector.paginate)
            self.context.paginator.records = self.db(query).count()
            self.context.paginate_info = PaginateInfo(self.context.paginator.page, self.context.paginator.paginate, self.context.paginator.records)
            limitby = self.context.paginator.limitby()
            #### /pagination
            if 'limitby' in self.request.vars:
                limitby = [int(item) for item in self.request.vars.limitby.split(',')]
            self.get_timeline(query, limitby=limitby, public=user.privacy == 1)
            #self.context.paginator.records = self.context.paginate_info.records = len(self.context.events)

        self.context.TIMELINEFUNCTIONS = '%s/app/person/usertimeline_events.html' % self.context.theme_name

    def publictimeline(self):
        query = (self.db.UserTimeLine.user_id == self.db.auth_user.id) & (self.db.auth_user.privacy == 1)
        #### pagination
        self.context.paginate_selector = PaginateSelector(paginates=(10, 25, 50, 100))
        self.context.paginator = Paginator(paginate=self.context.paginate_selector.paginate)
        self.context.paginator.records = self.db(query).count()
        self.context.paginate_info = PaginateInfo(self.context.paginator.page, self.context.paginator.paginate, self.context.paginator.records)
        limitby = self.context.paginator.limitby()
        #### /pagination
        if 'limitby' in self.request.vars:
            limitby = [int(item) for item in self.request.vars.limitby.split(',')]
        self.get_timeline(query, limitby=limitby, public=True)
        #self.context.paginator.records = self.context.paginate_info.records = len(self.context.events)
        if self.db.request.args(0) == "sidebar":
            self.context.TIMELINEFUNCTIONS = '%s/app/person/sidebar_publictimeline_events.html' % self.context.theme_name
        else:
            self.context.TIMELINEFUNCTIONS = '%s/app/person/publictimeline_events.html' % self.context.theme_name

    def privatetimeline(self):
        self.board(self.session.auth.user.id)
        self.contacts()
        allowed = list(self.context.following_list) + list(self.context.contacts_list)
        allowed.append(self.session.auth.user.id)
        query = self.db.UserTimeLine.created_by.belongs(allowed)
        #### pagination
        self.context.paginate_selector = PaginateSelector(paginates=(10, 25, 50, 100))
        self.context.paginator = Paginator(paginate=self.context.paginate_selector.paginate)
        self.context.paginator.records = self.db(query).count()
        self.context.paginate_info = PaginateInfo(self.context.paginator.page, self.context.paginator.paginate, self.context.paginator.records)
        limitby = self.context.paginator.limitby()
        #### /pagination
        if 'limitby' in self.request.vars:
            limitby = [int(item) for item in self.request.vars.limitby.split(',')]
        self.get_private_timeline(query, limitby=limitby)
        #self.context.paginator.records = self.context.paginate_info.records = len(self.context.events)
        if self.db.request.args(0) == "sidebar":
            self.context.TIMELINEFUNCTIONS = '%s/app/person/sidebar_privatetimeline_events.html' % self.context.theme_name
        else:
            self.context.TIMELINEFUNCTIONS = '%s/app/person/privatetimeline_events.html' % self.context.theme_name

    def update_contact_counter(self, follower=None, followed=None, arg=None):
        if arg:
            try:
                query = self.db.auth_user.id == int(self.request.args(0))
            except:
                query = self.db.auth_user.nickname == self.request.args(0)

            follower = self.db(query).select().first()
        else:
            follower = self.session.auth.user if self.session.auth else redirect(self.CURL('person', 'account', args='login'))

        def update_counter(person):
            i_follow = self.db(self.db.UserContact.follower == person.id).select(self.db.UserContact.followed)
            follows_me = self.db(self.db.UserContact.followed == person.id).select(self.db.UserContact.follower)
            i_follow_set = set([row.followed for row in i_follow])
            follows_me_set = set([row.follower for row in follows_me])
            contacts = len(i_follow_set & follows_me_set)
            following = len(i_follow_set - follows_me_set)
            followers = len(follows_me_set - i_follow_set)
            self.db(self.db.auth_user.id == person.id).update(contacts=contacts, isfollowing=following, followers=followers)
            self.db.commit()
            if person.id == self.db.auth.user_id:
                self.db.auth.user.update(contacts=contacts, isfollowing=following, followers=followers)

        if follower:
            update_counter(follower)
        if followed:
            update_counter(followed)

    def follow(self):
        follower = self.session.auth.user if self.session.auth else None
        if not follower and 'profile' in self.request.args:
            return "window.location = '%s'" % self.CURL('default', 'user', args='login', vars={'_next': self.CURL('person', 'show', args=self.request.args(0))})
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
                                                  "event_image": self.get_image(None, 'user', themename=self.context.theme_name, user=follower),
                                                  "event_to": followed.nickname or followed.first_name,
                                                  "event_reference": followed.id,
                                                  "event_text": "",
                                                  "event_link": follower.nickname or follower.id,
                                                  "event_link_to": followed.nickname or followed.id,
                                                  "event_image_to": self.get_image(None, 'user', themename=self.context.theme_name, user=followed)})

                self.notifier.notify("new_contact",
                                 followed,
                                 event_text=self.T("%(nickname)s followed you", follower),
                                 event_link=follower.nickname or follower.id,
                                 event_reference=followed.id,
                                 event_image=self.get_image(None, 'user', themename=self.context.theme_name, user=follower),
                                 follower=follower
                                 )

                # relation = self.db.UserContact._relation(follower.id, followed.id)
                # if relation == 'contacts':
                #     acount = followed.contacts + 1
                #     followed.update_record(contacts=acount)
                #     follower_user = self.db.auth_user[int(follower.id)]
                #     bcount = follower_user.contacts + 1
                #     follower_user.update_record(contacts=bcount)
                self.update_contact_counter(follower, followed)

                return contact_box(followed, 'contact', ajax=True, css={"main": "well span5", "img": "span", "div": "four columns"})
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
                #relation = self.db.UserContact._relation(follower.id, followed.id)
                query = (self.db.UserContact.follower == follower.id) & (self.db.UserContact.followed == followed.id)
                self.db(query).delete()
                self.db.commit()
                # if relation == 'contacts':
                #     acount = followed.contacts - 1
                #     followed.update_record(contacts=acount)
                #     follower_user = self.db.auth_user[int(follower.id)]
                #     bcount = follower_user.contacts - 1
                #     follower_user.update_record(contacts=bcount)
                self.update_contact_counter(follower, followed)
                return contact_box(followed, 'follower', ajax=True, css={"main": "well span5", "img": "span", "div": "four columns"})
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
            followed = self.session.auth.user if self.session.auth else redirect(self.CURL('person', 'account', args='login'))

        if followed:
            self.context.followers = self.db(self.db.UserContact.followed == followed.id).select()

    def following(self, arg=None):
        if arg:
            try:
                query = self.db.auth_user.id == int(self.request.args(0))
            except:
                query = self.db.auth_user.nickname == self.request.args(0)

            follower = self.db(query).select().first()
        else:
            follower = self.session.auth.user if self.session.auth else redirect(self.CURL('person', 'account', args='login'))

        if follower:
            self.context.following = self.db(self.db.UserContact.follower == follower.id).select()

    def contacts(self, arg=None):
        if 'refresh' in self.request.vars:
            self.update_contact_counter(arg=arg)
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
            if friends:
                self.context.contacts = self.db(self.db.auth_user.id.belongs(list(friends))).select()
            else:
                self.context.contacts = []

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
            finalquery = query & (self.db.auth_user.id != self.session.auth.user.id)
            #### pagination
            self.context.paginate_selector = PaginateSelector(paginates=(26, 50, 100))
            self.context.paginator = Paginator(paginate=self.context.paginate_selector.paginate)
            self.context.paginator.records = self.db(finalquery).count()
            self.context.paginate_info = PaginateInfo(self.context.paginator.page, self.context.paginator.paginate, self.context.paginator.records)
            limitby = self.context.paginator.limitby()
            #### /pagination
            self.context.results = self.db(finalquery).select(orderby=~self.db.auth_user.id, limitby=limitby)

            from helpers.person import contact_box
            self.context.contact_box = contact_box

        self.context.form = SQLFORM.factory(Field('q', default=q or '', label=self.T("Search Term"), comment=self.T("In name, email, nickname, about")), formstyle='divs', _method="GET")

    def new_board_event(self, form=None, writer=None, user=None, relation=None):
        writer_user = self.db.auth_user[writer]

        self.db.UserTimeLine._new_event(v={"user_id": writer_user.id,
                                  "nickname": writer_user.nickname,
                                  "event_type": "wrote_on_wall",
                                  "event_image": self.get_image(None, 'user', themename=self.context.theme_name, user=writer_user),
                                  "event_to": "" if relation == 'yourself' else user.nickname or user.first_name,
                                  "event_reference": form.vars.id,
                                  "event_text": form.vars.board_text,
                                  "event_link": writer_user.nickname or writer_user.id,
                                  "event_link_to": "" if relation == 'yourself' else user.nickname or user.id,
                                  "event_image_to": "" if relation == 'yourself' else self.get_image(None, 'user', themename=self.context.theme_name, user=user)})

        if writer_user.id != user.id:
            # self.mail.send(to=user.email,
            #            subject=self.T("Hi, %(nickname)s posted on your Movuca board", writer_user),
            #            message=[None, """<h1>You got a new post on your board!</h1><p>%(board_text)s</p>Note: this is a beta test of http://movu.ca CMS, thank you for the help with tests""" % form.vars])
            self.notifier.notify("wrote_on_wall",
                                 user,
                                 event_text=self.db.T("%s wrote on your wall: %s", (writer_user.nickname, form.vars.board_text)),
                                 event_link=user.nickname or user.id,
                                 event_reference=form.vars.id,
                                 event_image=self.get_image(None, 'user', themename=self.context.theme_name, user=writer_user),
                                 writer=writer_user
                                 )
        # TODO: RENDER TEMPLATE EMAILS CHECK PREFERENCES FOR NOTIFICATIONS

    def board(self, uid, post_id=None):
        if self.request.extension == 'html':
            self.show(uid)
        T = self.T
        try:
            user = self.db.auth_user[int(uid)]
        except Exception:
            user = self.db.auth_user(nickname=uid)
        self.context.user = user
        self.db.UserBoard.user_id.default = user.id
        self.db.UserBoard.writer.default = self.session.auth.user.id if self.session.auth else 0

        relation = self.db.UserContact._relation(self.session.auth.user.id if self.session.auth else 0, user.id)
        self.context.relation = relation
        if relation == "yourself":
            board_text_label = T("Whats up?")
        elif relation in ["contacts", "follower"]:
            board_text_label = T("Write something on %s's board", user.nickname)

        if relation in ['contacts', 'yourself', 'follower']:
            #self.db.UserBoard.board_text.label = CAT(board_text_label, A(T(" add photo "), _onclick="alert('Sorry, Photo upload is under development!');"))
            self.db.UserBoard.board_text.label = board_text_label
            self.context.form = SQLFORM(self.db.UserBoard, formstyle='divs', submit_button=T('Post'), separator='').process(onsuccess=lambda form: self.new_board_event(form, writer=self.session.auth.user.id, user=user, relation=relation))
        else:
            self.context.form = ''

        query = self.db.UserBoard.user_id == user.id

        if post_id:
            query = query & (self.db.UserBoard.id == post_id)
            self.context.form = self.context.paginate_selector = \
                self.context.paginator = self.context.paginate_info = ""
            limitby = None
        else:
            #### pagination
            self.context.paginate_selector = PaginateSelector(paginates=(10, 25, 50, 100))
            self.context.paginator = Paginator(paginate=self.context.paginate_selector.paginate)
            self.context.paginator.records = self.db(query).count()
            self.context.paginate_info = PaginateInfo(self.context.paginator.page, self.context.paginator.paginate, self.context.paginator.records)
            limitby = self.context.paginator.limitby()
            #### /pagination
            if 'limitby' in self.request.vars:
                limitby = [int(item) for item in self.request.vars.limitby.split(',')]

        if self.context.user.privacy != 1 and \
               relation not in ['contacts', 'follower', 'yourself'] and \
                   not self.db.auth.has_membership("admin", self.db.auth.user_id):
            self.view = 'app/person/board_private'
            self.context.board = []
        else:
            self.view = 'app/person/board'
            self.context.board = self.db(query).select(orderby=~self.db.UserBoard.created_on, limitby=limitby)

    def removeboard(self, msg_id, user_id):
        msg = self.db.UserBoard[int(msg_id)]
        if msg and (user_id in [msg.created_by, msg.user_id]):
            msg.delete_record()
            self.db.commit()
            self.context.eval = "$('#msg_%s').hide();" % msg_id
        else:
            self.context.eval = "alert('%s')" % self.T("It is not possible to delete")

    def removeevent(self, event_id, user_id):
        event = self.db.UserTimeLine[int(event_id)]
        if event and (user_id in [event.created_by, event.event_reference]):
            event.delete_record()
            self.db.commit()
            self.context.eval = "$('#event_%s').hide();" % event_id
        else:
            self.context.eval = "alert('%s')" % self.T("It is not possible to delete")

    def show(self, uid):
        T = self.T
        CURL = self.CURL
        self.db.auth.notifier = self.notifier
        user = None
        try:
            user = self.db.auth_user[int(uid)]
        except Exception:
            user = self.db.auth_user(nickname=uid)
        self.context.user = user or redirect(self.CURL('home', 'index'))

        buttons = CAT()
        if self.session.auth and self.session.auth.user:
            relation = self.db.UserContact._relation(self.session.auth.user.id if self.session.auth else 0, user.id)
        else:
            relation = 'unknown'

        relation_text = {'unknown': T('Your are mutually oblivious'),
                'contacts': T('This person is in your contact list (following each other)'),
                'following': T('You follow this person'),
                'follower': T('This person follows you'),
                'yourself': T('This is you')}

        self.context.relation = relation
        self.context.relation_text = relation_text[relation]

        if relation != 'yourself':
            text = {'unknown': T('follow'),
                    'contacts': T('unfollow'),
                    'following': T('unfollow'),
                    'follower': T('follow')}

            post_text = {'unknown': T('Followed!'),
                    'contacts': T('Contact removed!'),
                    'following': T('Unfollowed!'),
                    'follower': T('Contact added!')}

            url = {'unknown': CURL('person', 'follow', args=[user.id, 'profile']),
                    'contacts': CURL('person', 'unfollow', args=[user.id, 'profile']),
                    'following': CURL('person', 'unfollow', args=[user.id, 'profile']),
                    'follower': CURL('person', 'follow', args=[user.id, 'profile'])}

            buttons.append(TAG.BUTTON(text[relation], _onclick="jQuery(this).text('%s');ajax('%s', [], ':eval');jQuery('#relation-text').text('%s');" % (post_text[relation], url[relation], post_text[relation]), _class="btn btn-danger" if relation in ['following', 'contacts'] else 'btn btn-success'))
            #buttons.append(TAG.BUTTON(T("Message"), _class="btn", _onclick="alert('Sorry, it is not implemented yet')"))
            buttons.append(TAG.BUTTON(T("Report/Block"), _class="btn", _onclick="alert('Sorry, it is not implemented yet')"))
        else:
            buttons.append(A(T("Edit Profile"), _class="button btn", _href=CURL('default', 'user', args='profile')))
            #buttons.append(A(T("My Messages"), _class="button btn", _href=CURL('person', 'messages', args=user.nickname or user.id)))

        self.context.buttons = buttons
        self.context.resume = UL(
                                 LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='attach_round.24.png')), A(T("Wrote %s articles", user.articles), _href=self.CURL('article', 'list', vars={'author': user.id}))),
                                 LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='favorite_rounded.24.png')), A(T("Has %s favorites", user.favorites), _href=self.CURL('article', 'list', vars={'favorite': user.id}))),
                                 LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='like_rounded.24.png')), A(T("Liked %s articles", user.likes), _href=self.CURL('article', 'list', vars={'like': user.id}))),
                                 LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='face.24.png')), A(T("Has %s contacts", user.contacts), _href=self.CURL('person', 'contacts', args=user.nickname or user.id))),
                                 #LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='movuca.24.png')), A(T("Joined %s groups", user.groups))),
                                 _class="person-resume"
                                )

        if user.id == self.db.auth.user_id:
            self.context.resume.append(LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='like_rounded.24.png')), A(T("Disliked %s articles", user.dislikes), _href=self.CURL('article', 'list', vars={'dislike': user.id}))))
            self.context.resume.append(LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='like_rounded.24.png')), A(T("Subscribed to %s articles", user.subscriptions), _href=self.CURL('article', 'list', vars={'subscribe': user.id}))))

        self.response.meta.title = "%s | %s | %s" % (
                                                     user.nickname or user.first_name,
                                                     self.T("Profile"),
                                                     self.db.config.meta.title,
                                                    )
        self.response.meta.description = str(user.tagline or user.about) + ' ' + str(user.city or '') + ' ' + str(user.country or '')
        self.response.meta.keywords = [user.first_name, user.last_name, user.nickname]

        self.context.twittername = self.context.user.twitter.split('/')[-1].strip() if self.context.user.twitter else ""
        if self.db.config.auth.use_mailhide:
            key = dict(self.db.config.get_list('auth', 'mailhide'))
            from helpers.mailhide import asurl
            self.context.hiddenmail = asurl(self.context.user.email, key['public'], key['private'])
        else:
            self.context.hiddenmail = ''

        #facebook/google issue
        if self.db.session["%s_setpassword" % self.context.user.id]:
            self.context.user.update_record(password=self.db.session["%s_setpassword" % self.context.user.id])
            self.db.session["%s_setpassword" % self.context.user.id] = None

        if self.db.session["is_new_from"]:
            self.context.alerts.append(XML(self.T("Welcome! You logged in using your %s account, please go to your <a href='%s'>settings</a> page choose your username and complete your profile!", (self.db.session["is_new_from"], self.db.CURL('person', 'account', args='profile')))))
            self.db.auth.initial_user_permission(self.context.user)

        #user extra links image
        # TODO: limit the number of links?
        self.context.extra_links = []
        if user.extra_links:
            image_map = {"github.com": 'github.png',
                         "plus.google.com": 'gplus.png',
                         'twitter.com': 'twitter.png',
                         'facebook.com': 'facebook.png'}
            titles = {"github.com": 'Github',
                         "plus.google.com": 'Google +',
                         'twitter.com': 'Twitter',
                         'facebook.com': 'Facebook'}

            for link in user.extra_links:
                for key, img in image_map.items():
                    if key in link:
                        self.context.extra_links.append({"img": URL('static', '%s/images/icons' % self.context.theme_name, args=img), "link": link, "title": titles.get(key, "")})
                        continue
                if link not in [item['link'] for item in self.context.extra_links]:
                    self.context.extra_links.append({"img": URL('static', '%s/images/icons' % self.context.theme_name, args='globe.png'), "link": link, "title": link})

        if self.context.user.privacy != 1 and \
               relation not in ['contacts', 'follower', 'yourself'] and \
                   not self.db.auth.has_membership("admin", self.db.auth.user_id):
            self.view = 'app/person/show_private'
        else:
            self.view = 'app/person/show'

    def account(self):
        self.db.auth.notifier = self.notifier

        verify_email = self.notifier.build_message_from_template("verify_email")
        reset_password = self.notifier.build_message_from_template("reset_password")
        self.db.auth.messages.verify_email = verify_email['message'][1]
        self.db.auth.messages.reset_password = reset_password['message'][1]
        self.db.auth.messages.verify_email_subject = verify_email['subject']
        self.db.auth.messages.reset_password_subject = reset_password['subject']

        self.context.auth = self.db.auth
        self.context.form = self.db.auth()
        self.context.customfield = customfield
        if 'profile' in self.request.args:
            self.notifier.permission.add_permission_if_dont_exists(self.db.auth.user)
            self.context.permissions = self.db(self.notifier.permission.entity.user_id == self.db.auth.user_id).select()
            self.context.permission_events = dict(self.notifier.permission.events)

    def loginbare(self):
        username = self.request.vars.email
        password = self.request.vars.password
        user = self.db.auth.login_bare(username, password)
        if user:
            redirect(self.CURL('person', 'show'))
        else:
            redirect(self.CURL('home', 'index', args=[username, 'loginerror']))

    def facebook(self):
        self.db.auth.notifier = self.notifier
        if not self.db.config.auth.use_facebook:
            redirect(self.CURL('person', 'account', args=self.request.args, vars=self.request.vars))
        self.context.auth = self.db.auth
        self.context.auth.settings.controller = 'person'
        self.context.auth.settings.login_url = self.CURL('person', 'facebook', args='login')
        self.context.auth.settings.login_next = self.CURL('person', 'show')
        self.context.auth.settings.register_next = self.CURL('person', 'show')
        from helpers.facebook import FaceBookAccount
        self.context.auth.settings.login_form = FaceBookAccount(self.db)
        self.context.form = self.context.auth()

    def google(self):
        self.db.auth.notifier = self.notifier
        if not self.db.config.auth.use_google:
            redirect(self.CURL('person', 'account', args=self.request.args, vars=self.request.vars))
        self.context.auth = self.db.auth
        self.context.auth.settings.controller = 'person'
        self.context.auth.settings.login_url = self.CURL('person', 'google', args='login')
        self.context.auth.settings.login_next = self.CURL('person', 'show')
        self.context.auth.settings.register_next = self.CURL('person', 'show')
        from helpers.googleplus import GooglePlusAccount
        self.context.auth.settings.login_form = GooglePlusAccount(self.db)
        self.context.form = self.context.auth()

    def check_availability(self, items):
        #returns True when error, False when ok
        if not all(items.values()):
            return {items['field']: self.db.T("Empty")}
        items_to_check = {items['field']: items['value']}
        if self.db.session.auth:
            if items_to_check[items['field']] == self.db.session.auth.user[items['field']]:
                return {}

        return self.db.auth_user._validate(**items_to_check)

    def notificationpermission(self, pid, way, action):
        permission = self.notifier.permission.entity(user_id=self.db.auth.user.id, id=pid)
        if permission:
            current_way = permission.way
            if action == "enable" and not way in current_way:
                current_way.append(way)
                permission.update_record(way=current_way)
                self.db.commit()
                self.context.button = TAG.BUTTON(TAG['i'](_class="icon-ok", _style="margin-right:5px;"),
                    self.T("Enabled"),
                    _class="notificationpermission btn btn-success",
                    _id="%s_%s" % (way, pid),
                    **{"_data-url": URL('person', 'notificationpermission', args=[pid, way, 'disable'])})
            elif action == "disable" and way in current_way:
                current_way.remove(way)
                permission.update_record(way=current_way)
                self.db.commit()
                self.context.button = TAG.BUTTON(TAG['i'](_class="icon-off", _style="margin-right:5px;"),
                    self.T("Disabled"),
                    _class="notificationpermission btn btn-danger",
                    _id="%s_%s" % (way, pid),
                    **{"_data-url": URL('person', 'notificationpermission', args=[pid, way, 'enable'])})


def customfield(form, field, css={"main": "row", "label": "", "comment": "", "widget": "", "input": "", "error": ""}):
    tablefield = (form.table, field)
    maindiv = DIV(_id="%s_%s__row" % tablefield, _class=css.get("main", ""))
    if field in form.errors:
        maindiv["_class"] += css.get("error", "")
    labeldiv = DIV(_class="w2p_fl %s" % css.get("label", ""))
    commentdiv = DIV(_class="w2p_fc %s" % css.get("comment", ""))
    widgetdiv = DIV(_class="w2p_fw %s" % css.get("widget", ""))

    label = LABEL(form.custom.label[field], _for="%s_%s" % tablefield, _id="%s_%s__label" % tablefield)
    comment = form.custom.comment[field]
    widget = form.custom.widget[field]

    widget_class = widget.attributes.get("_class", "")
    widget_class += css.get("input", "")
    widget["_class"] = widget_class

    labeldiv.append(label)
    commentdiv.append(comment)
    widgetdiv.append(widget)

    maindiv.append(labeldiv)
    maindiv.append(commentdiv)
    maindiv.append(widgetdiv)

    return maindiv

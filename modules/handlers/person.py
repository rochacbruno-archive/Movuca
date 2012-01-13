# -*- coding: utf-8 -*-

from handlers.base import Base
from gluon import *
from helpers.person import contact_box


class Person(Base):
    def start(self):
        from movuca import DataBase, User, UserTimeLine, UserContact, UserBoard
        self.db = DataBase([User, UserTimeLine, UserContact, UserBoard])

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

    def get_timeline(self, query, orderby=None, limitby=None):
        timeline = self.db.UserTimeLine
        self.context.events = self.db(query).select(orderby=orderby or ~timeline.created_on, limitby=limitby or (0, 20))

    def usertimeline(self):
        if self.request.args(0):
            try:
                user = self.db.auth_user[int(self.request.args(0))]
            except Exception:
                user = self.db.auth_user(nickname=self.request.args(0))
        else:
            user = self.db.auth_user[self.session.auth.user.id]
        self.context.user = user
        if user:
            query = self.db.UserTimeLine.user_id == user.id
            if 'limitby' in self.request.vars:
                limitby = [int(item) for item in self.request.vars.limitby.split(',')]
            else:
                limitby = None
            self.get_timeline(query, limitby=limitby)

        self.context.TIMELINEFUNCTIONS = '%s/app/person/usertimeline_events.html' % self.context.theme_name

    def publictimeline(self):
        if 'limitby' in self.request.vars:
            limitby = [int(item) for item in self.request.vars.limitby.split(',')]
        else:
            limitby = None
        self.get_timeline(self.db.UserTimeLine, limitby=limitby)
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
        if 'limitby' in self.request.vars:
            limitby = [int(item) for item in self.request.vars.limitby.split(',')]
        else:
            limitby = None
        self.get_timeline(query, limitby=limitby)
        if self.db.request.args(0) == "sidebar":
            self.context.TIMELINEFUNCTIONS = '%s/app/person/sidebar_privatetimeline_events.html' % self.context.theme_name
        else:
            self.context.TIMELINEFUNCTIONS = '%s/app/person/privatetimeline_events.html' % self.context.theme_name

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
                                                  "event_image": self.get_image(followed.thumbnail, 'user'),
                                                  "event_to": followed.nickname or followed.first_name,
                                                  "event_reference": followed.id,
                                                  "event_text": "",
                                                  "event_link": followed.nickname or followed.id})
                relation = self.db.UserContact._relation(follower.id, followed.id)
                if relation == 'contacts':
                    acount = followed.contacts + 1
                    followed.update_record(contacts=acount)
                    follower_user = self.db.auth_user[int(follower.id)]
                    bcount = follower_user.contacts + 1
                    follower_user.update_record(contacts=bcount)

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
                relation = self.db.UserContact._relation(follower.id, followed.id)
                query = (self.db.UserContact.follower == follower.id) & (self.db.UserContact.followed == followed.id)
                self.db(query).delete()
                self.db.commit()
                if relation == 'contacts':
                    acount = followed.contacts - 1
                    followed.update_record(contacts=acount)
                    follower_user = self.db.auth_user[int(follower.id)]
                    bcount = follower_user.contacts - 1
                    follower_user.update_record(contacts=bcount)
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
            self.context.results = self.db(query & (self.db.auth_user.id != self.session.auth.user.id)).select(orderby=~self.db.auth_user.id)

            from helpers.person import contact_box
            self.context.contact_box = contact_box

        self.context.form = SQLFORM.factory(Field('q', default=q or '', label=self.T("Search Term"), comment=self.T("In name, email, nickname, about")), formstyle='divs', _method="GET")

    def new_board_event(self, form=None, writer=None, user=None, relation=None):
        writer_user = self.db.auth_user[writer]

        self.db.UserTimeLine._new_event(v={"user_id": writer_user.id,
                                  "nickname": writer_user.nickname,
                                  "event_type": "wrote_on_wall",
                                  "event_image": self.get_image(user.thumbnail, 'user'),
                                  "event_to": self.T("own") if relation == 'yourself' else user.nickname or user.first_name,
                                  "event_reference": user.id,
                                  "event_text": form.vars.board_text,
                                  "event_link": user.nickname or user.id})

    def board(self, uid):
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
            self.db.UserBoard.board_text.label = CAT(board_text_label, A(T(" add photo "), _onclick="alert('Sorry, Photo upload is under development!');"))
            self.context.form = SQLFORM(self.db.UserBoard, formstyle='divs', submit_button=T('Post'), separator='').process(onsuccess=lambda form: self.new_board_event(form, writer=self.session.auth.user.id, user=user, relation=relation))
        else:
            self.context.form = ''
        if 'limitby' in self.request.vars:
            limitby = [int(item) for item in self.request.vars.limitby.split(',')]
        else:
            limitby = (0, 12)
        self.context.board = self.db(self.db.UserBoard.user_id == user.id).select(orderby=~self.db.UserBoard.created_on, limitby=limitby)

    def show(self, uid):
        T = self.T
        CURL = self.CURL
        try:
            user = self.db.auth_user[int(uid)]
        except Exception:
            user = self.db.auth_user(nickname=uid)
        self.context.user = user

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

            buttons.append(TAG.BUTTON(text[relation], _onclick="jQuery(this).text('%s');ajax('%s', [], ':eval');jQuery('#relation-text').text('%s');" % (post_text[relation], url[relation], post_text[relation]), _class=""))
            buttons.append(TAG.BUTTON(T("Message"), _class=""))
            buttons.append(TAG.BUTTON(T("Report/Block"), _class=""))
        else:
            buttons.append(A(T("Edit Profile"), _class="button", _href=CURL('default', 'user', args='profile')))
            buttons.append(A(T("My Messages"), _class="button", _href=CURL('person', 'messages', args=user.nickname or user.id)))

        self.context.buttons = buttons
        self.context.resume = UL(
                                 LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='attach_round.24.png')), A(T("Wrote %s articles", user.articles), _href=self.CURL('article', 'list', vars={'author': user.id, 'limitby': '0,25'}))),
                                 LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='favorite_rounded.24.png')), T("Has %s favorites", user.favorites)),
                                 LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='like_rounded.24.png')), T("Liked %s articles", user.likes)),
                                 LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='face.24.png')), A(T("Has %s contacts", user.contacts), _href=self.CURL('person', 'contacts', args=user.nickname or user.id))),
                                 LI(IMG(_src=URL('static', '%s/images/icons' % self.context.theme_name, args='movuca.24.png')), T("Joined %s groups", user.groups)),
                                 _class="person-resume"
                                )

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
            self.context.hiddenmail = asurl('rochacbruno@gmail.com', key['public'], key['private'])
        else:
            self.context.hiddenmail = None

        #facebook issue
        if self.db.session["%s_setpassword" % self.context.user.id]:
            print self.db.session["%s_setpassword" % self.context.user.id]
            self.context.user.update_record(password=self.db.session["%s_setpassword" % self.context.user.id])
            self.db.session["%s_setpassword" % self.context.user.id] = None

    def account(self):
        self.context.auth = self.db.auth
        self.context.form = self.db.auth()

    def loginbare(self):
        username = self.request.vars.email
        password = self.request.vars.password
        user = self.db.auth.login_bare(username, password)
        if user:
            redirect(self.CURL('home', 'index'))
        else:
            redirect(self.CURL('home', 'index', args=[username, 'loginerror']))

    def facebook(self):
        if not self.db.config.auth.use_facebook:
            redirect(self.CURL('person', 'account', args=self.request.args, vars=self.request.vars))
        self.context.auth = self.db.auth
        self.context.auth.settings.controller = 'person'
        self.context.auth.settings.controller = 'person'
        self.context.auth.settings.login_url = self.CURL('person', 'facebook', args='login')
        self.context.auth.settings.login_next = self.CURL('person', 'show')
        self.context.auth.settings.register_next = self.CURL('person', 'account', args='profile')
        from helpers.facebook import FaceBookAccount
        self.context.auth.settings.login_form = FaceBookAccount(self.db)
        self.context.form = self.context.auth()

    def check_availability(self, items):
        #returns True when error, False when ok
        if not all(items.values()):
            return {items['field']: "empty"}
        items_to_check = {items['field']: items['value']}
        return self.db.auth_user._validate(**items_to_check)

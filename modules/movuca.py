# -*- coding: utf-8 -*-

###############################################################################
# Movuca - The Social CMS
# Copyright (C) 2012  Bruno Cezar Rocha <rochacbruno@gmail.com>

# License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
###############################################################################

from gluon.tools import Auth, Crud, Mail
from gluon.dal import DAL


class DataBase(DAL):
    def __init__(self, classes=[]):
        from gluon import current
        self.request = current.request
        self.session = current.session
        self.response = current.response
        self.T = current.T
        self.CURL = current.CURL
        self.cache = current.cache
        self.TIMEFORMAT = current.TIMEFORMAT
        self.DATEFORMAT = current.DATEFORMAT
        self.pdate = current.pdate
        self.ftime = current.ftime
        self.get_image = current.get_image
        from config import Config
        self.config = Config()
        if not current.request.env.web2py_runtime_gae:
            DAL.__init__(self, self.config.db.uri,
                         migrate_enabled=self.config.db.migrate_enabled,
                         check_reserved=['all'])
        else:
            DAL.__init__(self, self.config.db.gaeuri)
            current.session.connect(current.request, current.response, db=self)

        if classes:
            self.define_classes(classes)

    def define_classes(self, classes):
        for cls in classes:
            obj = cls(self)
            self.__setattr__(cls.__name__, obj.entity)
            if obj.__class__.__name__ == "Access":
                self.__setattr__("auth", obj)


class Access(Auth):
    def __init__(self, db):
        self.db = db
        self.hmac_key = Auth.get_or_create_key()
        Auth.__init__(self, self.db, hmac_key=self.hmac_key)
        #self.settings.logout_onlogout = lambda user: self.remove_session(user)
        #self.settings.register_onaccept = lambda form: add_to_users_group(form)
        self.settings.register_onaccept = [lambda form: self.send_welcome_email(form.vars),
                                           lambda form: self.initial_user_permission(form.vars)]
        #self.settings.login_onaccept = [lambda form: self.initial_user_permission(form.vars)]
        #self.settings.profile_onvalidation = []
        self.settings.profile_onaccept = [lambda form: self.remove_facebook_google_alert(form)]  # remove facebook / google alert session
        #self.settings.change_password_onaccept = [] # send alert email
        self.settings.controller = 'person'
        self.settings.allow_basic_login = True
        self.settings.register_verify_password = True
        self.settings.login_url = self.url('account', args='login')
        self.settings.verify_email_next = self.url('account', args='login')
        self.settings.logged_url = self.url('account', args='profile')
        self.settings.login_next = self.db.CURL('person', 'show')
        self.settings.register_next = self.db.CURL('person', 'show')
        self.settings.profile_next = self.db.CURL('person', 'account', args='profile')
        self.settings.retrieve_username_next = self.url('account', args='login')
        self.settings.retrieve_password_next = self.url('account', args='login')
        self.settings.request_reset_password_next = self.url('account', args='login')
        self.settings.reset_password_next = self.url('account', args='login')
        self.settings.change_password_next = self.db.CURL('person', 'show')

        self.messages.verify_email = \
            'Click on the link http://' + self.db.request.env.http_host + \
            self.db.CURL('person', 'account', args=['verify_email']) + \
            '/%(key)s to verify your email'

        self.messages.reset_password = \
            'Click on the link http://' + self.db.request.env.http_host + \
            self.db.CURL('person', 'account', args=['reset_password']) + \
            '/%(key)s to reset your password'

        self.settings.on_failed_authorization = self.url('account', args='not_authorized')
        self.settings.formstyle = 'divs'
        self.settings.label_separator = ''
        self.settings.register_next = self.url('show')
        self.settings.registration_requires_verification = self.db.config.auth.registration_requires_verification
        self.settings.registration_requires_approval = self.db.config.auth.registration_requires_approval
        if 'register' in self.db.request.args and self.db.config.auth.use_recaptcha:
            from gluon.tools import Recaptcha
            recaptcha_options = dict(self.db.config.get_list('auth', 'recaptcha'))
            self.settings.captcha = Recaptcha(self.db.request,
                                    recaptcha_options['public'],
                                    recaptcha_options['private'],
                                    options="theme:'%(theme)s', lang:'%(lang)s'" % recaptcha_options)
        from datamodel.user import User
        user = User(self)
        self.entity = user.entity
        if self.db.config.auth.server == 'default':
            self.settings.mailer = Mailer(self.db)
        else:
            self.settings.mailer.server = self.db.config.auth.server
            self.settings.mailer.sender = self.db.config.auth.sender
            self.settings.mailer.login = self.db.config.auth.login

    def remove_facebook_google_alert(self, form):
        if self.db.session["%s_is_new_from_facebook" % self.db.session.auth.user.facebookid]:
            del self.db.session["%s_is_new_from_facebook" % self.db.session.auth.user.facebookid]
        if self.db.session["%s_is_new_from_google" % self.db.session.auth.user.googleid]:
            del self.db.session["%s_is_new_from_google" % self.db.session.auth.user.googleid]

    def remove_session(self, user):
        del self.db.session.auth

    def initial_user_permission(self, user):
        self.notifier.permission.initial_user_permission(user)

    def send_welcome_email(self, user):
        if 'name' in user:
            user['first_name'] = user['name']
        if 'family_name' in user:
            user['lart_name'] = user['family_name']

        self.notifier.notify_user("welcome_on_register", user['email'], **user)


User = Access  # It is just for direct imports
from datamodel.user import UserTimeLine, UserContact, UserBoard


class Mailer(Mail):
    def __init__(self, db=None):
        if not db:
            from config import Config
            config = Config()
        else:
            config = db.config
        Mail.__init__(self)
        self.settings.server = config.mail.server
        self.settings.sender = config.mail.sender
        self.settings.login = config.mail.login


class FormCreator(Crud):
    def __init__(self, db):
        Crud.__init__(db)
        self.settings.auth = None
        self.settings.formstyle = 'divs'

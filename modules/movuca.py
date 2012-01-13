# -*- coding: utf-8 -*-

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
        #from gluon import current
        #T = current.T
        #request = current.request
        #session = current.session
        self.db = db
        self.hmac_key = Auth.get_or_create_key()
        Auth.__init__(self, self.db, hmac_key=self.hmac_key)
        #self.settings.logout_onlogout = lambda user: remove_session(user)
        #self.settings.register_onaccept = lambda form: add_to_users_group(form)
        self.settings.controller = 'person'
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

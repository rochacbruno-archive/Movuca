# -*- coding: utf-8 -*-

from gluon.tools import Auth, Crud, Mail
from gluon.dal import DAL


class DataBase(DAL):
    def __init__(self):
        from gluon import current
        self.request = current.request
        self.session = current.session
        self.response = current.response
        self.T = current.T
        self.cache = current.cache
        from config import Config
        self.config = Config()
        if not current.request.env.web2py_runtime_gae:
            DAL.__init__(self, self.config.db.uri,
                         migrate_enabled=self.config.db.migrate_enabled,
                         check_reserved=['all'])
        else:
            DAL.__init__(self, self.config.db.gaeuri)
            current.session.connect(current.request, current.response, db=self)


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
        self.settings.formstyle = 'divs'
        from datamodel.user import User
        user = User(self)
        self.entity = user.entity


class Mailer(Mail):
    def __init__(self):
        from config import Config
        from gluon import current
        cache = current.cache
        config = cache.ram('config', Config, time_expire=300)
        Mail.__init__()
        self.settings.server = config.mail.server
        self.settings.sender = config.mail.sender
        self.settings.login = config.mail.login


class FormCreator(Crud):
    def __init__(self, db):
        Crud.__init__(db)
        self.settings.auth = None
        self.settings.formstyle = 'divs'

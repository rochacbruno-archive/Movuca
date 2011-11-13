# -*- coding: utf-8 -*-

from gluon.tools import Auth, Crud, Mail
from gluon.dal import DAL


class DataBase(DAL):
    def __init__(self):
        from gluon import current
        from config import Config
        config = Config()
        if not current.request.env.web2py_runtime_gae:
            DAL.__init__(self, config.db.uri, migrate_enabled=config.db.migrate_enabled, check_reserved=['all'])
        else:
            DAL.__init__(self, config.db.gaeuri)
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
        from datamodel.user import User
        User(self)


class Mailer(Mail):
    def __init__(self):
        from config import Config
        config = Config()
        Mail.__init__()
        self.settings.server = config.mail.server
        self.settings.sender = config.mail.sender
        self.settings.login = config.mail.login


class FormCreator(Crud):
    def __init__(self, db):
        Crud.__init__(db)
        self.settings.auth = None
        self.settings.formstyle = 'divs'

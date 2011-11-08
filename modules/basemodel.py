# -*- coding: utf-8 -*-
from gluon.dal import DAL, Field
from gluon.tools import Auth
from config import Config


class BaseModel(object):
    def __init__(self, db=None, auth={}, migrate=None, format=None):
        self.db = db or auth.get('db', None)
        assert isinstance(self.db, DAL)
        self.auth = auth
        self.config = Config()
        self.migrate = migrate or self.config.db_migrate
        self.format = format
        self.define_model()
        if auth:
            self.auth.settings.table_user = self.entity
            self.auth.define_tables(migrate=self.migrate)

    def define_model(self):
        self.entity = self.db.define_table(self.tablename,
                                           *self.properties,
                                           migrate=self.migrate,
                                           format=self.format)

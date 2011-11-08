# -*- coding: utf-8 -*-
from gluon.dal import DAL
#from gluon.tools import Auth


class BaseModel(object):
    def __init__(self, db=None, auth={}, migrate=None, format=None):
        self.db = auth.db if hasattr(auth, 'db') else db
        assert isinstance(self.db, DAL)
        self.auth = auth
        from config import Config
        self.config = Config()
        self.migrate = migrate or self.config.db_migrate
        self.format = format
        self.set_properties()
        self.set_validators()
        self.set_visibility()
        self.set_representation()
        self.set_widgets()
        self.set_labels()
        self.set_comments()
        if auth:
            self.auth.settings.table_user = self.entity
            self.auth.define_tables(migrate=self.migrate)

    def set_properties(self):
        #fakeauth = Auth(DAL(None))
        #self.properties.extend([fakeauth.signature])
        self.entity = self.db.define_table(self.tablename,
                                           *self.properties,
                                           migrate=self.migrate,
                                           format=self.format)

    def set_validators(self):
        validators = self.validators if hasattr(self, 'validators') else {}
        for field, value in validators.items():
            self.entity[field].requires = value

    def set_visibility(self):
        visibility = self.visibility if hasattr(self, 'visibility') else {}
        for field, value in visibility.items():
            self.entity[field].writable, self.entity[field].readable = value

    def set_representation(self):
        representation = self.representation if hasattr(self, 'representation') else {}
        for field, value in representation.items():
            self.entity[field].represent = value

    def set_widgets(self):
        widgets = self.widgets if hasattr(self, 'widgets') else {}
        for field, value in widgets.items():
            self.entity[field].widget = value

    def set_labels(self):
        labels = self.labels if hasattr(self, 'labels') else {}
        for field, value in labels.items():
            self.entity[field].label = value

    def set_comments(self):
        comments = self.comments if hasattr(self, 'comments') else {}
        for field, value in comments.items():
            self.entity[field].comment = value

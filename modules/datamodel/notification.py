# -*- coding: utf-8 -*-

from gluon.dal import Field
from basemodel import BaseModel
from gluon.sqlhtml import SQLFORM
from gluon.validators import IS_IN_SET


class NotificationPermission(BaseModel):
    tablename = "notification_permission"

    def set_properties(self):
        T = self.db.T
        self.fields = [
                       Field("user_id", "reference auth_user"),
                       Field("event_type", "string", notnull=True),
                       Field("way", "list:string", notnull=True),
                       Field("unikey", unique=True, notnull=True)
        ]

        self.events = self.db.config.get_list('notification', 'event')
        self.ways = self.db.config.get_list('notification', 'way')

        self.validators = {
            "way": IS_IN_SET(self.ways, multiple=True),
            "event_type": IS_IN_SET(self.events)
        }

        self.computations = {
            "unikey": lambda row: "%(user_id)s_%(event_type)s" % row
        }

        self.widgets = {
            "way": SQLFORM.widgets.checkboxes.widget
        }

        self.labels = {
            "event_type": T("When"),
            "way": T("You want to be notified by")
        }

    def set_fixtures(self):
        self.entity._initial_user_permission = self.initial_user_permission

    def initial_user_permission(self, user):
        try:
            for event, value in self.events:
                self.entity.update_or_insert(self.entity.unikey == "%s_%s" % (user.id, event),
                                             user_id=user['id'],
                                             event_type=event,
                                             way=[key for key, val in self.ways])
        except Exception:
            self.db.rollback()
        else:
            self.db.commit()

    def set_permission_to_all(self):
        users = self.db(self.db.auth_user.id > 0).select()
        for user in users:
            for event, value in self.events:
                self.entity.update_or_insert(self.entity.unikey == "%s_%s" % (user.id, event), user_id=user.id, event_type=event, way=[key for key, val in self.ways])
                self.db.commit()


class Notification(BaseModel):
    tablename = "notification"

    def set_properties(self):
        self.fields = [
            Field("user_id", "reference auth_user"),
            Field("event_type", "string", notnull=True),
            Field("event_text", "string"),
            Field("event_link", "string"),
            Field("event_reference", "integer"),
            Field("event_image", "string"),
            Field("mail_sent", "boolean", default=False),
            Field("is_read", "boolean", default=False),
        ]


class EmailTemplate(BaseModel):
    tablename = "email_template"

    def set_properties(self):
        self.fields = [
            Field("template_key", "string", notnull=True, unique=True),
            Field("plain_text", "text", notnull=True, default=""),
            Field("html_text", "text", notnull=True, default=""),
            Field("subject_text", "string"),
            Field("copy_to", "string"),
            Field("reply_to", "string"),
            Field("detect_links", "boolean", default=True),
            Field("attachment_file", "upload"),
        ]

        from plugin_ckeditor import CKEditor
        ckeditor = CKEditor(self.db, self.db.config.theme.name)
        self.widgets = {
            "html_text": ckeditor.widget
        }

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
            "event_type": IS_IN_SET([(key, value % ("", "")) for key, value in self.events])
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
                self.entity.update_or_insert(self.entity.unikey == "%s_%s" % (user['id'], event),
                                             user_id=user['id'],
                                             event_type=event,
                                             way=[key for key, val in self.ways])
        except Exception:
            self.db.rollback()
        else:
            self.db.commit()

    def add_permission_if_dont_exists(self, user):
        try:
            for event, value in self.events:
                permission = self.entity(unikey="%s_%s" % (user['id'], event))
                if not permission:
                    self.entity.insert(user_id=user['id'],
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
            Field("kwargs", "text"),
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

    def set_fixtures(self):
        self.default_html = """
        <html>
        <p>
            <a href="http://movu.ca/demo">
               <img alt="Movuca The Social CMS" src="https://movu.ca/demo/static/images/minilogo.png"/>
            </a>
        </p>
        <p>
          <img src="{{=event_image}}" width="100">
          <br />
          <h2>
          {{=event_text}}
          </h2>
          <br />
          <a href="{{="http://%s%s" % (http_host, event_info[event_type]['url_to']+'/'+event_link)}}"> Click here and go to the event!</a>
        </p>
        <p>
            This is a notification of {{=event_type}} from Movuca The Social CMS - http://movu.ca
        </p>
        Movuca Beta
        </html>
        """
        self.default_welcome_html = """
        <html>
        <p>
            <a href="http://movu.ca/demo">
               <img alt="Movuca The Social CMS" src="https://movu.ca/demo/static/images/minilogo.png"/>
            </a>
        </p>
        <p>
           Welcome to Movuca Social CMS
           <br/>
           Go to your profile and complete your data!
        </p>
        <p>
            This is a notification from Movuca The Social CMS - http://movu.ca
        </p>
        Movuca Beta
        </html>
        """
        self.default_verify_email_html = """
        <html>
        <p>
            <a href="http://movu.ca/demo">
               <img alt="Movuca The Social CMS" src="https://movu.ca/demo/static/images/minilogo.png"/>
            </a>
        </p>
        <p>
           Click the link below to verify your e-mail
           <br/>
           {{=CURL('person', 'account', args=['verify_email'], scheme=True, host=True)}}/%(key)s
        </p>
        <p>
            This is a notification from Movuca The Social CMS - http://movu.ca
        </p>
        Movuca Beta
        </html>
        """
        self.default_reset_password_html = """
        <html>
        <p>
            <a href="http://movu.ca/demo">
               <img alt="Movuca The Social CMS" src="https://movu.ca/demo/static/images/minilogo.png"/>
            </a>
        </p>
          <p>
           Click the link below to reset your password
           <br/>
           {{=CURL('person', 'account', args=['reset_password'], scheme=True, host=True)}}/%(key)s
        </p>
        <p>
            This is a notification from Movuca The Social CMS - http://movu.ca
        </p>
        Movuca Beta
        </html>
        """
        self.default_keys = dict(self.db.config.get_list('notification', 'event'))
        self.auth_keys = {}
        self.auth_keys['welcome_on_register'] = "Welcome to Movuca Social CMS"
        self.auth_keys['verify_email'] = "Verify your email"
        self.auth_keys['reset_password'] = "Reset your password"
        for key, subject in self.default_keys.items():
            if not self.db(self.entity.template_key == key).count():
                self.entity.insert(
                    template_key=key,
                    plain_text="Movuca CMS Notification",
                    html_text=self.default_html,
                    subject_text=subject % ("", ""),
                )

        if not self.db(self.entity.template_key == 'welcome_on_register').count():
                self.entity.insert(
                    template_key='welcome_on_register',
                    plain_text="Movuca CMS Notification",
                    html_text=self.default_welcome_html,
                    subject_text="Welcome to Movuca The Social CMS",
                )
        if not self.db(self.entity.template_key == 'verify_email').count():
                self.entity.insert(
                    template_key='verify_email',
                    plain_text="Movuca CMS Notification",
                    html_text=self.default_verify_email_html,
                    subject_text="Movuca CMS - Verify your email",
                )
        if not self.db(self.entity.template_key == 'reset_password').count():
                self.entity.insert(
                    template_key='reset_password',
                    plain_text="Movuca CMS Notification",
                    html_text=self.default_reset_password_html,
                    subject_text="Movuca CMS Reset your password",
                )




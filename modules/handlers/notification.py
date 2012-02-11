# -*- coding: utf-8 -*-

###############################################################################
# Movuca - The Social CMS
# Copyright (C) 2012  Bruno Cezar Rocha <rochacbruno@gmail.com>

# License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
###############################################################################

from datamodel.notification import NotificationPermission, Notification, EmailTemplate
from gluon import URL
from handlers.base import Base
from movuca import DataBase, User
from helpers.object_cleaner import clean_object


class Notifications(Base):
    def start(self):
        self.db = DataBase([User, Notification])

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

    def list_unread(self, user_id):
        self.context.notifications = self.db((self.db.Notification.user_id == user_id) & (self.db.Notification.is_read == False)).select(orderby=~self.db.Notification.created_on)
        self.context.notifications_ids = [row.id for row in self.context.notifications]

    def list_latest(self, user_id, limitby="0,10"):
        if isinstance(limitby, str):
            limitby = [int(index) for index in limitby.split(",")]

        self.context.notifications = self.db((self.db.Notification.user_id == user_id)).select(orderby=self.db.Notification.is_read | ~self.db.Notification.created_on, limitby=limitby)
        self.context.notifications_ids = [row.id for row in self.context.notifications if row.is_read == False]

    def counter(self, user_id):
        try:
            self.context.count = self.db((self.db.Notification.user_id == user_id) & (self.db.Notification.is_read == False)).count()
        except Exception:
            self.context.count = 0

    def mark_as_read(self, user_id, ids):
        ids = ids.split(",")
        if ids:
            notifications = self.db((self.db.Notification.user_id == user_id) & (self.db.Notification.is_read == False) & (self.db.Notification.id.belongs(ids))).select()
            for notification in notifications:
                notification.update_record(is_read=True)
                self.db.commit()


class Notifier(object):
    """
     Build the notifier object
     Check User permissions - return ['site', 'email']
     if site:
        insert new site notification
     if email:
        build message from template
        send the email to user
        check mail_sent to true
    """

    def notify(self, event_type, user=None, user_id=None, email=None, **kwargs):
        if not any([user, user_id]):
            raise Exception("You need to inform user or user_id")
        permission = self.check_permission(event_type, user_id or user.id, user)
        kwargs['http_host'] = str(self.db.request.env.http_host)
        kwargs = self.check_image_urls(kwargs)
        if 'site' in permission:
            params = dict(
                user_id=user_id or user.id,
                event_type=event_type,
                event_text=kwargs.get("event_text", ""),
                event_link=kwargs.get("event_link", ""),
                event_reference=kwargs.get("event_reference", 0),
                event_image=kwargs.get("event_image", ""),
                kwargs=clean_object(kwargs, self.db.T)
            )
            self.insert_site_notification(**params)

        if 'email' in permission:
            if user:
                to = user.email
            elif email:
                to = email
            else:
                to = self.db.auth_user[user_id].email

            self.send_email(to, event_type, **kwargs)
        else:
            if self.record:
                self.notification.entity[self.record].update_record(mail_sent=True)

    def notify_all(self, event_type, emails, users, **kwargs):
        kwargs['http_host'] = str(self.db.request.env.http_host)
        kwargs = self.check_image_urls(kwargs)
        for user in users:
            params = dict(
                user_id=user,
                event_type=event_type,
                event_text=kwargs.get("event_text", ""),
                event_link=kwargs.get("event_link", ""),
                event_reference=kwargs.get("event_reference", 0),
                event_image=kwargs.get("event_image", ""),
                is_read=False,
                kwargs=clean_object(kwargs, self.db.T)
            )
            self.insert_site_notification_all(**params)

        self.send_email("Undisclosed Recipients", event_type, bcc=emails, **kwargs)

    def notify_user(self, event_type, to, **kwargs):
        kwargs = self.check_image_urls(kwargs)
        self.send_email(to, event_type, bypass=True, **kwargs)

    def __init__(self, db):
        self.db = db
        self.config = db.config
        self.request, self.response, self.session = self.db.request, self.db.response, self.db.session
        self.permission = NotificationPermission(self.db)
        self.notification = Notification(self.db)
        self.emailtemplate = EmailTemplate(self.db)
        self.record = None
        self.records = []

    def check_permission(self, event_type, user_id=None, user=None):
        row = self.permission.entity(user_id=user_id, event_type=event_type)
        if not row:
            user = user or self.db.auth_user[user_id]
            self.permission.initial_user_permission(user)
            row = self.permission.entity(user_id=user.id, event_type=event_type)
        return row.way

    def insert_site_notification(self, **kwargs):
        self.record = self.notification.entity.update_or_insert(**kwargs)

    def insert_site_notification_all(self, **kwargs):
        record = self.notification.entity.update_or_insert(**kwargs)
        if record:
            self.records.append(record)

    def build_message_from_template(self, event_type, **kwargs):
        template = self.emailtemplate.entity(template_key=event_type)
        if not template:
            return dict(message="Movuca notification message, you need to define an email template for %s event \n %s" % (event_type, str(kwargs)), subject="New notification from Movuca CMS")

        # if template.detect_links:
        #     from gluon import MARKMIN
        #     self.pre_render = lambda value: str(MARKMIN(value))
        # else:
        self.pre_render = lambda value: value

        from gluon.template import render
        from gluon import current
        self.render = lambda text: render(text, context=dict(theme_name=self.config.theme.name, CURL=self.db.CURL, event_type=event_type, event_info=current.event_info, **kwargs))
        # >>> from gluon.template import render
        # >>> render(str(MARKMIN("{{=number}} Bruno http://dfdfd.com")), context={"number":1})
        # '<p>1 Bruno <a href="http://dfdfd.com">http://dfdfd.com</a></p>'

        pre_html_message = self.pre_render(template.html_text)
        html_message = self.render(pre_html_message)
        plain_message = self.render(template.plain_text)

        # TODO: Include Attachment

        return dict(message=[plain_message, "<html>%s</html>" % html_message], subject=template.subject_text % kwargs, reply_to=template.reply_to or "Undisclosed Recipients", bcc=template.copy_to or "")

    def send_email(self, to, event_type, bcc=[], bypass=False, **kwargs):
        if self.config.notification.worker == 'site' or bypass:
            from movuca import Mailer
            mail = Mailer(self.db)
            try:
                message = self.build_message_from_template(event_type, **kwargs)
                if 'bcc' in message:
                    bcc = message['bcc'].split(',') + bcc
                    del message['bcc']

                params = dict(to=to, bcc=bcc, **message)
                sent = mail.send(**params)
            except Exception, e:
                print str(e)
                sent = False
            else:
                if self.record:
                    self.notification.entity[self.record].update_record(mail_sent=True)
                if self.records:
                    for record in self.records:
                        self.notification.entity[record].update_record(mail_sent=True)
            return sent

    def check_image_urls(self, args):
        if 'event_image' in args:
            args['event_image'] = self.ensure_image_url(args['event_image'])
        if 'event_image_to' in args:
            args['event_image_to'] = self.ensure_image_url(args['event_image_to'])

        if 'data' in args:
            if 'event_image' in args['data']:
                args['data']['event_image'] = self.ensure_image_url(args['data']['event_image'])
            if 'event_image_to' in args['data']:
                args['data']['event_image_to'] = self.ensure_image_url(args['data']['event_image_to'])
        return args

    def ensure_image_url(self, url):
        if url.startswith("http"):
            return url
        else:
            parts = url.split("/")
            return URL(parts[1], parts[2], parts[3], args=parts[4:], scheme=True, host=True, extension=False)

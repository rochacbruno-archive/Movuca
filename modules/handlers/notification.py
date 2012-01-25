# -*- coding: utf-8 -*-

from datamodel.notification import NotificationPermission, Notification, EmailTemplate


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
        if 'site' in permission:
            params = dict(
                user_id=user_id or user.id,
                event_type=event_type,
                event_text=kwargs.get("event_text", ""),
                event_link=kwargs.get("event_link", ""),
                event_reference=kwargs.get("event_reference", 0),
                event_image=kwargs.get("event_image", ""),
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
        for user in users:
            params = dict(
                user_id=user,
                event_type=event_type,
                event_text=kwargs.get("event_text", ""),
                event_link=kwargs.get("event_link", ""),
                event_reference=kwargs.get("event_reference", 0),
                event_image=kwargs.get("event_image", ""),
            )
            self.insert_site_notification_all(**params)

        self.send_email("Undisclosed Recipients", event_type, bcc=emails, **kwargs)

    def notify_user(self, event_type, to, **kwargs):
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
            return dict(message="Movuca notification message, you need to define an email template for %s event" % event_type, subject="New notification from Movuca CMS")

        # if template.detect_links:
        #     from gluon import MARKMIN
        #     self.pre_render = lambda value: str(MARKMIN(value))
        # else:
        self.pre_render = lambda value: value

        from gluon.template import render
        self.render = lambda text: render(text, context=dict(theme_name=self.config.theme.name, **kwargs))
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
                mail.send(**params)
            except Exception, e:
                print str(e)
            else:
                if self.record:
                    self.notification.entity[self.record].update_record(mail_sent=True)
                if self.records:
                    for record in self.records:
                        self.notification.entity[record].update_record(mail_sent=True)

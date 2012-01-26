#!/usr/bin/python
# -*- coding: utf-8 -*-

from handlers.notification import Notifications


def list_unread():
    notifications = Notifications()
    notifications.list_unread(session.auth.user.id)
    return notifications.render("app/notification/list_unread")


def count():
    notifications = Notifications()
    notifications.counter(session.auth.user.id)
    return notifications.context.count


def mark_as_read():
    notifications = Notifications()
    notifications.mark_as_read(session.auth.user.id, request.vars.notifications_ids)
    return "all marked as read.."

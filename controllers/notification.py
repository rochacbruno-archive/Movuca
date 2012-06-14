#!/usr/bin/python
# -*- coding: utf-8 -*-

from handlers.notification import Notifications


def list_unread():
    notifications = Notifications('list_unread')
    return notifications.render("app/notification/list_unread")


def list_latest():
    notifications = Notifications('list_latest')
    return notifications.render("app/notification/list_latest")


def count():
    notifications = Notifications('counter')
    return notifications.context.count


def mark_as_read():
    if "notifications_ids" in request.vars:
        Notifications('mark_as_read')
        return "all marked as read.."
    else:
        return "nothing to do..."

# coding: utf-8

from handlers.admin import Admin


def index():
    admin = Admin("configindex")
    return admin.render("admin/generic")


def mail_options():
    admin = Admin("configtables")
    return admin.render("admin/generic")


def auth_options():
    admin = Admin("configtables")
    return admin.render("admin/generic")


def article_options():
    admin = Admin("configtables")
    return admin.render("admin/generic")


def comment_options():
    admin = Admin("configtables")
    return admin.render("admin/generic")


def db_options():
    admin = Admin("configtables")
    return admin.render("admin/generic")


def meta_options():
    admin = Admin("configtables")
    return admin.render("admin/generic")


def notification_options():
    admin = Admin("configtables")
    return admin.render("admin/generic")


def theme_options():
    admin = Admin("configtables")
    return admin.render("admin/generic")


def crud_options():
    admin = Admin("configtables")
    return admin.render("admin/generic")

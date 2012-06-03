# coding: utf-8

from handlers.admin import Admin


def index():
    admin = Admin("adminindex")
    return admin.render("admin/generic")


def content_type():
    admin = Admin("tables")
    return admin.render("admin/generic")


def article_category():
    admin = Admin("tables")
    return admin.render("admin/generic")


def article():
    admin = Admin("tables")
    return admin.render("admin/generic")


def auth_user():
    admin = Admin("tables")
    return admin.render("admin/generic")


def auth_group():
    admin = Admin("tables")
    return admin.render("admin/generic")


def auth_membership():
    admin = Admin("tables")
    return admin.render("admin/generic")


def article_comments():
    admin = Admin("tables")
    return admin.render("admin/generic")


def notification():
    admin = Admin("tables")
    return admin.render("admin/generic")


def email_template():
    admin = Admin("tables")
    return admin.render("admin/generic")


def internal_page():
    admin = Admin("tables")
    return admin.render("admin/generic")


def menu():
    admin = Admin("tables")
    return admin.render("admin/generic")

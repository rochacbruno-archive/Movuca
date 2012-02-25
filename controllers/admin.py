# coding: utf-8

from handlers.admin import Admin


def index():
    admin = Admin()
    return admin.render("admin/index")

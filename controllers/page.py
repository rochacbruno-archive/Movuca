# coding: utf-8

from handlers.page import Page


def show():
    page = Page("show")
    return page.render("app/page/show")


def new():
    page = Page("new")
    return page.render("app/page/new")


def edit():
    page = Page("edit")
    return page.render("app/page/edit")

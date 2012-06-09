# coding: utf-8

from handlers.page import Page


def list():
    page = Page("list")
    return page.render("app/page/list")


def show():
    page = Page("show")
    return page.render("app/page/show")


def new():
    page = Page("new")
    return page.render("app/page/new")


def edit():
    page = Page("edit")
    return page.render("app/page/edit")


def reportcontent():
    page = Page("reportcontent")
    return page.render("app/page/new")

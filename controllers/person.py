#!/usr/bin/python
# -*- coding: utf-8 -*-

from handlers.person import Person


def usertimeline():
    person = Person('usertimeline')
    return person.render("app/person/usertimeline")


def publictimeline():
    person = Person('publictimeline')
    return person.render("app/person/publictimeline")


def followers():
    person = Person()
    person.followers(request.args(0))
    return person.render()


def following():
    person = Person()
    person.following(request.args(0))
    return person.render()


def contacts():
    person = Person()
    person.contacts(request.args(0))
    person.context.left_sidebar_enabled = True
    return person.render('app/person/contacts')


def search():
    person = Person()
    person.context.left_sidebar_enabled = True
    person.search(request.vars.get('q'))
    return person.render('app/person/search')


def follow():
    person = Person()
    return person.follow()


def unfollow():
    person = Person()
    return person.unfollow()


def show():
    person = Person()
    person.show(request.args(0) or session.auth.user.id)
    return person.render('app/person/show')


def board():
    person = Person()
    person.board(request.args(0) or session.auth.user.id)
    return person.render('app/person/board')
